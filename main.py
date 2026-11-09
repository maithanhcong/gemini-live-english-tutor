import asyncio
import base64
import json
import logging
import os
import random

from typing import List, Optional
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi import FastAPI, Query, WebSocket, WebSocketDisconnect, HTTPException, Request, BackgroundTasks
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
from gemini_live import GeminiLive

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


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class LiveTranslateRequest(BaseModel):
    text: str
    source_lang: str = "en"
    target_lang: str = "vi"

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


@app.post("/api/auth/change-password")
async def auth_change_password(req: ChangePasswordRequest, request: Request):
    """Đổi mật khẩu người dùng sau khi xác thực mật khẩu hiện tại."""
    user = await get_current_user_optional(request)
    if not user:
        raise HTTPException(status_code=401, detail="Vui lòng đăng nhập để đổi mật khẩu.")
    
    ok, msg = database.change_user_password(user["id"], req.old_password, req.new_password)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"status": "success", "message": msg}


@app.post("/api/user/reset-vocab")
async def api_reset_vocab(request: Request):
    """Đặt lại toàn bộ tiến độ từ vựng của người dùng về mặc định (0 từ)."""
    user = await get_current_user_optional(request)
    if not user:
        raise HTTPException(status_code=401, detail="Vui lòng đăng nhập để đặt lại từ vựng.")
    
    ok = database.reset_user_vocab(user["id"])
    if not ok:
        raise HTTPException(status_code=500, detail="Không thể đặt lại từ vựng.")
    return {"status": "success", "message": "Đã đặt lại tiến độ từ vựng về mặc định (0 từ)."}


@app.post("/api/user/reset-history")
async def api_reset_history(request: Request):
    """Xóa toàn bộ lịch sử bài tập luyện dịch của người dùng."""
    user = await get_current_user_optional(request)
    if not user:
        raise HTTPException(status_code=401, detail="Vui lòng đăng nhập để xóa lịch sử bài dịch.")
    
    ok = database.reset_user_history(user["id"])
    if not ok:
        raise HTTPException(status_code=500, detail="Không thể xóa lịch sử bài dịch.")
    return {"status": "success", "message": "Đã xóa toàn bộ lịch sử bài dịch thành công."}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for Gemini Live with Auto Failover & Dynamic Vocab Sync theo user_id."""
    try:
        await websocket.accept()
    except Exception as e:
        logger.error(f"WebSocket accept error: {e}", exc_info=True)
        return

    username_str = "Khách"
    try:
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
                    mastered_words = list(set(mastered_words + [w.strip() for w in mastered_param.split(",") if w.strip()]))
            except Exception:
                mastered_words = list(set(mastered_words + [w.strip() for w in mastered_param.split(",") if w.strip()]))

        logger.info(
            f"WebSocket connection accepted from client ({username_str}). Mastered words count: {len(mastered_words)}"
        )

        audio_input_queue = asyncio.Queue()
        video_input_queue = asyncio.Queue()
        text_input_queue = asyncio.Queue()

        async def audio_output_callback(data):
            try:
                await websocket.send_bytes(data)
            except Exception as e:
                logger.debug(f"Audio output callback error: {e}")

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
                                            f"""System: [ĐỒNG BỘ TRẠNG THÁI TỪ VỰNG TỪ TAB LUYỆN DỊCH]
"""
                                            f"""Danh sách các từ học viên {username_str} ĐÃ THÀNH THẠO ({len(mastered_list)} từ): [{words_sample}].
"""
                                            f"""Hướng dẫn cho Gia sư: Tuyệt đối KHÔNG yêu cầu học viên đọc lại hay kiểm tra lại những từ này! """
                                            f"""Hãy tập trung hỏi, luyện phát âm và đàm thoại dựa trên các từ còn lại mà học viên CHƯA học."""
                                        )
                                    else:
                                        sync_directive = (
                                            f"""System: [ĐỒNG BỘ TRẠNG THÁI TỪ VỰNG]
"""
                                            f"""Học viên {username_str} hiện chưa đánh dấu từ nào là thành thạo. Hãy kiểm tra và hướng dẫn theo các từ trong lộ trình."""
                                        )
                                    await text_input_queue.put(sync_directive)
                                    await websocket.send_json({
                                        "type": "sync_vocab_state_ack",
                                        "mastered_count": len(mastered_list),
                                        "status": "success",
                                    })
                                    continue
                                elif "text" in payload:
                                    await text_input_queue.put(payload["text"])
                                    continue
                        except json.JSONDecodeError:
                            pass

                        await text_input_queue.put(text)
            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected from client ({username_str})")
                gemini_client.stop()
            except Exception as e:
                logger.error(f"Error receiving from client ({username_str}): {e}", exc_info=True)
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
            logger.error(f"Error in Gemini session ({username_str}): {type(e).__name__}: {e}", exc_info=True)
        finally:
            gemini_client.stop()
            receive_task.cancel()
            try:
                await websocket.close()
            except Exception:
                pass
    except Exception as e:
        logger.error(f"WebSocket error in websocket_endpoint ({username_str}): {e}", exc_info=True)
        try:
            await websocket.close()
        except Exception:
            pass


# ─── Luyện Dịch & Từ Vựng Endpoints (SQLite & Multi-user Isolation) ─────────

@app.on_event("startup")
async def startup_event():
    try:
        database.init_db()
        logger.info("[Database] study_progress.db initialized on startup (Pure SQLite Single Source of Truth).")
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
    level: str = "a0"
    sentence_count: int = 3


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
            curr_selected = database.get_selected_words_list(user_id=user_id)
            if not user_id:
                asyncio.create_task(asyncio.to_thread(database.sync_selection_to_excel, set(curr_selected)))
            count = len(curr_selected)
            return {
                "status": "success",
                "user_id": user_id,
                "selected_count": count,
                "selected_words": curr_selected,
                "message": "Đã lưu trạng thái tích chọn thành công.",
            }
        else:
            raise HTTPException(status_code=400, detail="Thiếu dữ liệu cập nhật trạng thái.")

        return {
            "status": "success",
            "user_id": user_id,
            "selected_count": count,
            "selected_words": database.get_selected_words_list(user_id=user_id),
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
    """Đồng bộ từ vựng 100% từ SQLite theo user_id độc lập (Single Source of Truth, ~2ms)."""
    try:
        user = await get_current_user_optional(request)
        user_id = user["id"] if user else None

        all_words = database.get_all_vocab_dictionary(user_id=user_id, filter_learned_only=False)
        total_count = len(all_words)

        selected_words = database.get_selected_words_list(user_id=user_id)
        learned_count = len(selected_words)

        # Build full topics dictionary for 100% of Oxford 3000
        full_topics_dict = {}
        for w in all_words:
            t = w["topic"] or "Chủ đề chung"
            if t not in full_topics_dict:
                full_topics_dict[t] = []
            full_topics_dict[t].append(w)
        all_topics = [{"name": t, "words": w_list} for t, w_list in full_topics_dict.items()]

        # Filtered topics if learned_only is requested
        if learned_only:
            filtered_topics_dict = {}
            for w in all_words:
                if w["learned"]:
                    t = w["topic"] or "Chủ đề chung"
                    if t not in filtered_topics_dict:
                        filtered_topics_dict[t] = []
                    filtered_topics_dict[t].append(w)
            topics = [{"name": t, "words": w_list} for t, w_list in filtered_topics_dict.items()]
            returned_count = sum(len(x["words"]) for x in topics)
        else:
            topics = all_topics
            returned_count = total_count

        return {
            "status": "success",
            "user_id": user_id,
            "total_words": total_count,
            "learned_count": learned_count,
            "selected_words": selected_words,
            "returned_count": returned_count,
            "topics": topics,
            "all_topics": all_topics,
        }
    except Exception as e:
        logger.error(f"Error syncing vocab from SQLite: {e}")
        return {"status": "error", "message": str(e)}


@app.get("/api/vocab/export")
async def export_vocab_backup(request: Request):
    """Xuất file Excel dự phòng khi người dùng chủ động yêu cầu."""
    try:
        user = await get_current_user_optional(request)
        user_id = user["id"] if user else None
        filepath = database.export_vocab_to_excel(user_id=user_id)
        if filepath and os.path.exists(filepath):
            filename = os.path.basename(filepath)
            return FileResponse(filepath, filename=filename, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        raise HTTPException(status_code=500, detail="Không thể tạo file sao lưu Excel.")
    except Exception as e:
        logger.error(f"Error exporting vocab backup: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class CustomWordRequest(BaseModel):
    word: str


@app.post("/api/vocab/custom-word")
async def add_custom_word_api(req: CustomWordRequest, request: Request, background_tasks: BackgroundTasks):
    """
    Thêm một từ vựng mới tùy chỉnh hoặc đánh dấu từ đã có là thành thạo.
    - Nếu từ đã có trong vocab_dictionary: tự động đánh dấu đã học cho user.
    - Nếu từ chưa có: gọi Gemini Flash-Lite lấy IPA, pos, meaning_vi, example, lưu vào SQLite (is_custom=1),
      đánh dấu đã học cho user, và kích hoạt background task để ghi bổ sung vào Excel.
    """
    clean_word = (req.word or "").strip().lower()
    if not clean_word:
        raise HTTPException(status_code=400, detail="Vui lòng nhập từ vựng hợp lệ.")

    user = await get_current_user_optional(request)
    user_id = user["id"] if user else None

    # 1. Kiểm tra xem từ đã tồn tại trong từ điển chưa
    existing = database.find_vocab_dictionary_word(clean_word)
    if existing:
        database.update_vocab_selection([clean_word], True, user_id=user_id)
        return {
            "status": "success",
            "is_new": False,
            "word": existing["word"],
            "ipa": existing["ipa"],
            "pos": existing["pos"],
            "meaning_vi": existing["meaning_vi"],
            "example": existing["example_sentence"],
            "topic": existing["topic"],
            "level": existing["level"],
            "is_custom": bool(existing["is_custom"]),
            "message": f"Từ '{clean_word}' đã có trong kho từ vựng và được đánh dấu thành thạo."
        }

    # 2. Sinh thông tin từ vựng mới qua Gemini Flash-Lite
    word_info = passage_service.generate_custom_word_details(clean_word)
    database.add_vocab_dictionary_word(
        word=clean_word,
        ipa=word_info.get("ipa", f"/{clean_word}/"),
        pos=word_info.get("pos", "word"),
        meaning_vi=word_info.get("meaning_vi", f"Nghĩa của {clean_word}"),
        example_sentence=word_info.get("example", f"I use {clean_word} in my conversation."),
        topic=word_info.get("topic", "Từ tùy chỉnh"),
        level=word_info.get("level", "B1"),
        is_custom=1
    )

    # 3. Đánh dấu đã học cho người dùng hiện tại
    database.update_vocab_selection([clean_word], True, user_id=user_id)

    # 4. Background Excel Sync: Ghi bổ sung ngầm không nghẽn event loop
    word_record_for_excel = {
        "word": clean_word,
        "ipa": word_info.get("ipa", ""),
        "pos": word_info.get("pos", ""),
        "meaning_vi": word_info.get("meaning_vi", ""),
        "example_sentence": word_info.get("example", ""),
        "topic": "Từ tùy chỉnh"
    }
    background_tasks.add_task(asyncio.to_thread, passage_service.append_word_to_excel, word_record_for_excel)

    return {
        "status": "success",
        "is_new": True,
        "word": clean_word,
        "ipa": word_info.get("ipa", f"/{clean_word}/"),
        "pos": word_info.get("pos", "word"),
        "meaning_vi": word_info.get("meaning_vi", f"Nghĩa của {clean_word}"),
        "example": word_info.get("example", ""),
        "topic": "Từ tùy chỉnh",
        "level": "B1",
        "is_custom": True,
        "message": f"Đã thêm thành công từ mới '{clean_word}' vào lộ trình học."
    }



class GenerateQuizRequest(BaseModel):
    count: Optional[int] = 3
    selected_words: Optional[List[str]] = None


@app.post("/api/passage/generate")
async def generate_passage_api(req: GeneratePassageRequest, request: Request):
    """Sinh đoạn văn luyện dịch từ danh sách từ được tích chọn (hỗ trợ đổi bài ngẫu nhiên & recency-weighted)."""
    if not req.selected_words:
        raise HTTPException(status_code=400, detail="Vui lòng chọn ít nhất 1 từ vựng.")
    try:
        user = await get_current_user_optional(request)
        user_id = user["id"] if user else None
        data = await passage_service.generate_passage_async(
            req.selected_words,
            random_change=req.random_change,
            model_family=req.model_family,
            level=req.level,
            sentence_count=req.sentence_count,
            user_id=user_id,
        )
        return {"status": "success", "data": data}
    except Exception as e:
        logger.error(f"Error generating passage: {e}")
        return {"status": "error", "message": str(e)}


@app.post("/api/quiz/generate-unchecked")
async def generate_unchecked_quiz_api(req: Optional[GenerateQuizRequest] = None, request: Request = None):
    """
    Sinh bài trắc nghiệm củng cố (Quiz) từ tập từ vựng CHƯA TÍCH (chưa thuộc) của học viên.
    """
    try:
        user = await get_current_user_optional(request) if request else None
        user_id = user["id"] if user else None

        # 1. Lấy toàn bộ từ vựng 100% từ SQLite (Single Source of Truth)
        all_words_list = [w["word"] for w in database.get_all_vocab_dictionary(user_id=user_id, filter_learned_only=False)]
        
        # 2. Lấy các từ đã tích chọn (mastered)
        mastered_set = set(database.get_selected_words_list(user_id=user_id))
        if req and req.selected_words:
            mastered_set.update(req.selected_words)

        # 3. Lọc ra danh sách từ chưa tích (is_mastered = 0)
        unchecked_words = [w for w in all_words_list if w not in mastered_set]
        if not unchecked_words:
            unchecked_words = all_words_list

        count = req.count if (req and req.count) else 3
        count = max(1, min(count, 5))
        
        # 4. Bốc ngẫu nhiên 3 đến 5 từ chưa thuộc
        candidate_count = min(len(unchecked_words), count + 2)
        candidate_words = random.sample(unchecked_words, candidate_count)

        # 5. Gọi hàm sinh Quiz siêu tốc qua gemini-flash-lite-latest
        quiz_data = await passage_service.generate_unchecked_quiz_async(candidate_words, count=count)
        return quiz_data
    except Exception as e:
        logger.error(f"Error generating unchecked quiz: {e}")
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
        # Gọi AI đánh giá và chấm điểm bản dịch của học viên
        evaluation = None
        try:
            evaluation = await passage_service.evaluate_translation_async(
                english_passage=req.english_passage,
                reference_vietnamese=req.vietnamese_translation,
                student_translation=req.my_translation
            )
        except Exception as eval_err:
            logger.warning(f"[Submit Translation] AI Evaluation error: {eval_err}")

        return {
            "status": "success",
            "submission_id": inserted_id,
            "user_id": user_id,
            "vietnamese_translation": req.vietnamese_translation,
            "evaluation": evaluation,
            "message": "Nộp bài và chấm điểm thành công!",
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



@app.post("/api/translate/live")
async def live_translate_api(req: LiveTranslateRequest):
    """Phòng Dịch Thuật AI Song Ngữ: Dịch trực tiếp hai chiều Anh <-> Việt và phân tích ngữ pháp."""
    if not req.text or not req.text.strip():
        return {
            "status": "success",
            "translation": "",
            "grammar_notes": "",
            "key_words": [],
            "alternative_phrasings": [],
            "model_used": "none"
        }
    try:
        data = await passage_service.translate_live_studio_async(
            text=req.text,
            source_lang=req.source_lang,
            target_lang=req.target_lang
        )
        return data
    except Exception as e:
        logger.error(f"Error in live translation: {e}")
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
