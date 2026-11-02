import asyncio
import base64
import json
import logging
import os

from typing import List, Optional
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi import FastAPI, Query, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
try:
    from scripts.twilio_handler import TwilioHandler
except ImportError:
    try:
        from twilio_handler import TwilioHandler
    except ImportError:
        TwilioHandler = None
import passage_service
import database

# Load environment variables
load_dotenv()

# Configure logging - DEBUG for our modules, INFO for everything else
logging.basicConfig(level=logging.INFO)
logging.getLogger("gemini_live").setLevel(logging.DEBUG)
logging.getLogger(__name__).setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)

# Configuration & Failover Setup
api_keys_env = os.getenv("GEMINI_API_KEYS")
if api_keys_env:
    GEMINI_API_KEYS = [k.strip() for k in api_keys_env.split(",") if k.strip()]
else:
    single_key = os.getenv("GEMINI_API_KEY")
    GEMINI_API_KEYS = [single_key] if single_key else []

fallback_models_env = os.getenv("FALLBACK_MODELS")
if fallback_models_env:
    FALLBACK_MODELS = [m.strip() for m in fallback_models_env.split(",") if m.strip()]
else:
    single_model = os.getenv("MODEL", "gemini-3.8-live")
    FALLBACK_MODELS = [single_model]

GEMINI_API_KEY = GEMINI_API_KEYS[0] if GEMINI_API_KEYS else None
MODEL = FALLBACK_MODELS[0] if FALLBACK_MODELS else "gemini-3.8-live"

logger.info(
    f"[Live Connect] Initialized with {len(GEMINI_API_KEYS)} API Key(s) and {len(FALLBACK_MODELS)} Fallback Model(s)"
)

# Twilio config (optional — only needed for phone call integration)
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_APP_HOST = os.getenv("TWILIO_APP_HOST")

# Initialize FastAPI
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/")
async def root():
    return FileResponse("frontend/index.html")


async def get_current_user_optional(request: Request) -> Optional[dict]:
    """Trích xuất user hiện tại từ Bearer token, Cookie hoặc query param."""
    auth_header = request.headers.get("Authorization")
    token = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1].strip()
    if not token:
        token = request.cookies.get("session_token")
    if not token:
        token = request.query_params.get("token")
    if not token:
        return None
    user = database.get_user_by_session(token)
    return user


class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


# ─── Auth Endpoints ─────────────────────────────────────────────────────────

@app.post("/api/auth/register")
async def auth_register(req: RegisterRequest, response: Response):
    """Đăng ký tài khoản mới. Tự động cấp session và đăng nhập."""
    user, err = database.register_user(req.username, req.password)
    if err:
        return {"status": "error", "message": err}
    auth_user, token, login_err = database.authenticate_user(req.username, req.password)
    if login_err or not token:
        return {"status": "success", "message": "Đăng ký thành công! Vui lòng đăng nhập.", "token": None, "user": user}
    response.set_cookie(key="session_token", value=token, httponly=True, max_age=86400 * 30, samesite="lax")
    return {
        "status": "success",
        "message": f"Chào mừng {auth_user['username']}! Đăng ký tài khoản thành công.",
        "token": token,
        "user": auth_user,
        "mastered_count": 0,
    }


@app.post("/api/auth/login")
async def auth_login(req: LoginRequest, response: Response):
    """Đăng nhập tài khoản, trả về session_token và số lượng từ đã tích của user."""
    user, token, err = database.authenticate_user(req.username, req.password)
    if err or not user:
        return {"status": "error", "message": err or "Tên đăng nhập hoặc mật khẩu không chính xác."}
    response.set_cookie(key="session_token", value=token, httponly=True, max_age=86400 * 30, samesite="lax")
    selected_words = database.get_user_selected_words(user["id"])
    return {
        "status": "success",
        "message": f"Chào mừng {user['username']} quay trở lại!",
        "token": token,
        "user": user,
        "mastered_count": len(selected_words),
    }


@app.get("/api/auth/me")
async def auth_me(request: Request):
    """Kiểm tra trạng thái đăng nhập hiện tại và số từ thành thạo của user."""
    user = await get_current_user_optional(request)
    if not user:
        return {"status": "unauthenticated", "user": None, "mastered_count": 0}
    selected_words = database.get_user_selected_words(user["id"])
    return {
        "status": "authenticated",
        "user": user,
        "mastered_count": len(selected_words),
    }


@app.post("/api/auth/logout")
async def auth_logout(request: Request, response: Response):
    """Đăng xuất tài khoản, hủy session_token trong SQLite và xóa Cookie."""
    auth_header = request.headers.get("Authorization")
    token = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1].strip()
    if not token:
        token = request.cookies.get("session_token")
    if token:
        database.delete_session(token)
    response.delete_cookie(key="session_token")
    return {"status": "success", "message": "Đã đăng xuất thành công."}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for Gemini Live with Auto Failover & Dynamic Vocab Sync theo user_id."""
    await websocket.accept()

    token = websocket.query_params.get("token") or websocket.cookies.get("session_token")
    user = database.get_user_by_session(token) if token else None
    user_id = user["id"] if user else None
    username_str = user["username"] if user else "Khách"

    # Lấy danh sách từ đã tích riêng của người dùng
    mastered_words = []
    if user_id:
        mastered_words = database.get_user_selected_words(user_id)

    # Đọc thêm từ query param nếu client gửi kèm
    mastered_param = websocket.query_params.get("mastered")
    if mastered_param:
        try:
            parsed = json.loads(mastered_param)
            if isinstance(parsed, list):
                mastered_words = list(set(mastered_words + [str(w).strip() for w in parsed if str(w).strip()]))
            elif isinstance(parsed, str):
                mastered_words = list(set(mastered_words + [w.strip() for w in parsed.split(",") if w.strip()]))
        except Exception:
            mastered_words = list(set(mastered_words + [w.strip() for w in mastered_param.split(",") if w.strip()]))

    logger.info(
        f"WebSocket connection accepted from client ({username_str}). Mastered words count: {len(mastered_words)}"
    )

    audio_input_queue = asyncio.Queue()
    video_input_queue = asyncio.Queue()
    text_input_queue = asyncio.Queue()

    async def audio_output_callback(data):
        await websocket.send_bytes(data)

    async def audio_interrupt_callback():
        pass

    gemini_client = GeminiLive(
        api_keys=GEMINI_API_KEYS,
        models=FALLBACK_MODELS,
        input_sample_rate=16000,
        mastered_words=mastered_words,
    )

    async def receive_from_client():
        try:
            while True:
                message = await websocket.receive()

                if message.get("bytes"):
                    await audio_input_queue.put(message["bytes"])
                elif message.get("text"):
                    text = message["text"]
                    try:
                        payload = json.loads(text)
                        if isinstance(payload, dict):
                            if payload.get("type") == "image":
                                logger.info(
                                    f"Received image chunk from client: {len(payload['data'])} base64 chars"
                                )
                                image_data = base64.b64decode(payload["data"])
                                await video_input_queue.put(image_data)
                                continue
                            elif payload.get("type") == "sync_vocab_state":
                                mastered_list = payload.get("mastered_words", [])
                                logger.info(
                                    f"Received live sync_vocab_state with {len(mastered_list)} mastered words (user={username_str})"
                                )
                                if user_id:
                                    database.set_all_selections(mastered_list, user_id=user_id)
                                else:
                                    database.set_all_selections(mastered_list)
                                    asyncio.create_task(asyncio.to_thread(database.sync_selection_to_excel, set(mastered_list)))

                                if mastered_list:
                                    words_sample = ", ".join(mastered_list[:250])
                                    sync_directive = (
                                        f"System: [ĐỒNG BỘ TRẠNG THÁI TỪ VỰNG TỪ TAB LUYỆN DỊCH]\n"
                                        f"Danh sách các từ học viên {username_str} ĐÃ THÀNH THẠO ({len(mastered_list)} từ): [{words_sample}].\n"
                                        f"Hướng dẫn cho Gia sư: Tuyệt đối KHÔNG yêu cầu học viên đọc lại hay kiểm tra lại những từ này! "
                                        f"Hãy tập trung hỏi, luyện phát âm và đàm thoại dựa trên các từ còn lại mà học viên CHƯA học."
                                    )
                                else:
                                    sync_directive = (
                                        f"System: [ĐỒNG BỘ TRẠNG THÁI TỪ VỰNG]\n"
                                        f"Học viên {username_str} hiện chưa đánh dấu từ nào là thành thạo. Hãy kiểm tra và hướng dẫn theo các từ trong lộ trình."
                                    )
                                await text_input_queue.put(sync_directive)
                                await websocket.send_json({
                                    "type": "sync_vocab_state_ack",
                                    "mastered_count": len(mastered_list),
                                    "status": "success",
                                })
                                continue
                    except json.JSONDecodeError:
                        pass

                    await text_input_queue.put(text)
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected from client ({username_str})")
            gemini_client.stop()
        except Exception as e:
            logger.error(f"Error receiving from client ({username_str}): {e}")
            gemini_client.stop()

    receive_task = asyncio.create_task(receive_from_client())

    async def run_session():
        async for event in gemini_client.start_session(
            audio_input_queue=audio_input_queue,
            video_input_queue=video_input_queue,
            text_input_queue=text_input_queue,
            audio_output_callback=audio_output_callback,
            audio_interrupt_callback=audio_interrupt_callback,
        ):
            if event:
                await websocket.send_json(event)

    try:
        await run_session()
    except WebSocketDisconnect:
        logger.info(f"Client ({username_str}) disconnected normally")
    except Exception as e:
        logger.error(f"Error in Gemini session ({username_str}): {type(e).__name__}: {e}")
    finally:
        gemini_client.stop()
        receive_task.cancel()
        try:
            await websocket.close()
        except Exception:
            pass


# ─── Luyện Dịch & Từ Vựng Endpoints (SQLite & Multi-user Isolation) ─────────

@app.on_event("startup")
async def startup_event():
    try:
        words = passage_service.load_words_from_excel(filter_learned_only=False)
        database.init_db(excel_words=words)
        logger.info("[Database] study_progress.db initialized on startup.")
    except Exception as e:
        logger.error(f"[Database] Error initializing db on startup: {e}")


class UpdateVocabSelectionRequest(BaseModel):
    words: Optional[List[str]] = None
    is_selected: Optional[bool] = None
    selected_words: Optional[List[str]] = None


class GeneratePassageRequest(BaseModel):
    selected_words: List[str]
    random_change: bool = False
    model_family: str = "flash"


class SubmitTranslationRequest(BaseModel):
    used_words: str
    english_passage: str
    vietnamese_translation: str
    my_translation: str


class SyncVocabStateRequest(BaseModel):
    mastered_words: List[str]


class SaveTranslationRequest(BaseModel):
    used_words: str
    english_passage: str
    my_translation: str


@app.post("/api/vocab/update-selection")
async def update_vocab_selection_api(req: UpdateVocabSelectionRequest, request: Request):
    """
    Cập nhật trạng thái tích chọn từ vựng vào SQLite database (cô lập theo user_id nếu đã đăng nhập).
    """
    try:
        user = await get_current_user_optional(request)
        user_id = user["id"] if user else None

        if req.selected_words is not None:
            database.set_all_selections(req.selected_words, user_id=user_id)
            if not user_id:
                asyncio.create_task(asyncio.to_thread(database.sync_selection_to_excel, set(req.selected_words)))
            count = len(req.selected_words)
        elif req.words is not None and req.is_selected is not None:
            database.update_vocab_selection(req.words, req.is_selected, user_id=user_id)
            curr_selected = set(database.get_selected_words_list(user_id=user_id))
            if not user_id:
                asyncio.create_task(asyncio.to_thread(database.sync_selection_to_excel, curr_selected))
            count = len(curr_selected)
        else:
            raise HTTPException(status_code=400, detail="Thiếu dữ liệu cập nhật trạng thái.")

        return {
            "status": "success",
            "user_id": user_id,
            "selected_count": count,
            "message": "Đã lưu trạng thái tích chọn thành công.",
        }
    except Exception as e:
        logger.error(f"Error updating vocab selection: {e}")
        return {"status": "error", "message": str(e)}


@app.post("/api/vocab/sync-state")
async def sync_vocab_state_api(req: SyncVocabStateRequest, request: Request):
    """API endpoint nhận danh sách từ đã tích chọn từ tab Luyện Dịch."""
    user = await get_current_user_optional(request)
    user_id = user["id"] if user else None
    logger.info(f"REST API /api/vocab/sync-state user={user_id} received {len(req.mastered_words)} mastered words")
    database.set_all_selections(req.mastered_words, user_id=user_id)
    if not user_id:
        asyncio.create_task(asyncio.to_thread(database.sync_selection_to_excel, set(req.mastered_words)))
    return {
        "status": "success",
        "user_id": user_id,
        "mastered_count": len(req.mastered_words),
        "message": f"Đã đồng bộ {len(req.mastered_words)} từ thành thạo lên máy chủ.",
    }


@app.get("/api/vocab/sync")
async def sync_vocab(request: Request, learned_only: bool = False):
    """Đồng bộ từ vựng từ Excel & SQLite theo user_id độc lập."""
    try:
        user = await get_current_user_optional(request)
        user_id = user["id"] if user else None

        all_words = passage_service.load_words_from_excel(filter_learned_only=False, user_id=user_id)
        total_count = len(all_words)

        # Lấy danh sách từ được chọn trực tiếp từ SQLite theo user_id
        selected_words = database.get_selected_words_list(user_id=user_id)
        learned_count = len(selected_words)

        words_to_return = [w for w in all_words if (not learned_only or w["learned"])]

        topics_dict = {}
        for w in words_to_return:
            t = w["topic"] or "Chủ đề chung"
            if t not in topics_dict:
                topics_dict[t] = []
            topics_dict[t].append(w)

        topics = [{"name": t, "words": w_list} for t, w_list in topics_dict.items()]
        return {
            "status": "success",
            "user_id": user_id,
            "total_words": total_count,
            "learned_count": learned_count,
            "selected_words": selected_words,
            "returned_count": len(words_to_return),
            "topics": topics,
        }
    except Exception as e:
        logger.error(f"Error syncing vocab: {e}")
        return {"status": "error", "message": str(e)}


@app.post("/api/passage/generate")
async def generate_passage_api(req: GeneratePassageRequest):
    """Sinh đoạn văn luyện dịch từ danh sách từ được tích chọn (hỗ trợ đổi bài ngẫu nhiên)."""
    if not req.selected_words:
        raise HTTPException(status_code=400, detail="Vui lòng chọn ít nhất 1 từ vựng.")
    try:
        data = await passage_service.generate_passage_async(
            req.selected_words,
            random_change=req.random_change,
            model_family=req.model_family,
        )
        return {"status": "success", "data": data}
    except Exception as e:
        logger.error(f"Error generating passage: {e}")
        return {"status": "error", "message": str(e)}


@app.post("/api/passage/submit-translation")
async def submit_translation_api(req: SubmitTranslationRequest, request: Request):
    """
    Nộp bài luyện dịch: lưu vào SQLite theo user_id riêng biệt.
    """
    try:
        user = await get_current_user_optional(request)
        user_id = user["id"] if user else None

        # Lưu vào SQLite theo user_id
        inserted_id = database.save_translation_submission(
            used_words=req.used_words,
            english_passage=req.english_passage,
            vietnamese_translation=req.vietnamese_translation,
            my_translation=req.my_translation,
            user_id=user_id,
        )
        if not user_id:
            asyncio.create_task(
                asyncio.to_thread(
                    passage_service.update_user_translation,
                    req.used_words,
                    req.english_passage,
                    req.my_translation,
                )
            )
        return {
            "status": "success",
            "submission_id": inserted_id,
            "user_id": user_id,
            "vietnamese_translation": req.vietnamese_translation,
            "message": "Nộp bài và lưu vào CSDL thành công!",
        }
    except Exception as e:
        logger.error(f"Error submitting translation: {e}")
        return {"status": "error", "message": str(e)}


@app.get("/api/passage/history")
async def get_passage_history_api(request: Request, limit: int = 15):
    """Lấy danh sách các bài luyện dịch gần nhất từ SQLite theo user_id."""
    try:
        user = await get_current_user_optional(request)
        user_id = user["id"] if user else None
        history = database.get_recent_translations(limit=limit, user_id=user_id)
        return {"status": "success", "history": history, "user_id": user_id}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/api/passage/save-translation")
async def save_translation_api(req: SaveTranslationRequest, request: Request):
    """Lưu bản dịch của học viên vào SQLite theo user_id."""
    try:
        user = await get_current_user_optional(request)
        user_id = user["id"] if user else None
        database.save_translation_submission(
            used_words=req.used_words,
            english_passage=req.english_passage,
            vietnamese_translation="",
            my_translation=req.my_translation,
            user_id=user_id,
        )
        if not user_id:
            passage_service.update_user_translation(
                used_words=req.used_words,
                english_passage=req.english_passage,
                my_translation=req.my_translation,
            )
        return {"status": "success", "user_id": user_id, "message": "Đã lưu bản dịch thành công!"}
    except Exception as e:
        logger.error(f"Error saving translation: {e}")
        return {"status": "error", "message": str(e)}



# ─── Twilio Endpoints ─────────────────────────────────────────────────────────

@app.post("/twilio/inbound")
async def twilio_inbound():
    """Handles inbound Twilio calls. Returns TwiML to open a media stream."""
    host = TWILIO_APP_HOST or "localhost:8000"
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>Connecting to Gemini Live.</Say>
    <Connect>
        <Stream url="wss://{host}/twilio/stream" />
    </Connect>
</Response>"""
    return Response(content=twiml, media_type="application/xml")


@app.post("/twilio/outbound")
async def twilio_outbound(
    to_number: str = Query(..., description="Destination phone number (E.164 format)"),
    from_number: str = Query(..., description="Your Twilio phone number (E.164 format)"),
):
    """Initiates an outbound Twilio call that connects to Gemini Live."""
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        return {"error": "TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN must be set in environment"}
    if not TWILIO_APP_HOST:
        return {"error": "TWILIO_APP_HOST must be set in environment"}

    from twilio.rest import Client as TwilioClient

    client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    twiml = f"""<Response>
    <Say>Connecting to Gemini Live.</Say>
    <Connect>
        <Stream url="wss://{TWILIO_APP_HOST}/twilio/stream" />
    </Connect>
</Response>"""

    call = client.calls.create(
        to=to_number,
        from_=from_number,
        twiml=twiml,
    )
    logger.info(f"Outbound call initiated: {call.sid}")
    return {"callSid": call.sid, "status": call.status}


@app.websocket("/twilio/stream")
async def twilio_stream(websocket: WebSocket):
    """WebSocket endpoint for Twilio Media Streams."""
    await websocket.accept()
    if TwilioHandler is None:
        logger.error("TwilioHandler is not available")
        await websocket.close()
        return

    handler = TwilioHandler(gemini_api_key=GEMINI_API_KEY, model=MODEL)
    try:
        await handler.handle_media_stream(websocket)
    except Exception as e:
        logger.error(f"Twilio stream error: {e}", exc_info=True)
    finally:
        try:
            await websocket.close()
        except Exception:
            pass
        logger.info("Twilio media stream WebSocket closed")


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
