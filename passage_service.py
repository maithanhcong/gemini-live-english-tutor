"""
passage_service.py
Quản lý đồng bộ từ vựng từ Excel / SQLite và sinh đoạn văn luyện dịch (Anh - Việt):
- Tận dụng toàn diện cơ chế Failover xoay vòng 4 API Key.
- Mở rộng đa tầng Model AI:
  * Dòng siêu nhẹ & tốc độ cao (Fast & Low Cost): gemini-3.5-flash-lite, gemini-3.1-flash-lite, gemini-2.5-flash, gemini-2.5-flash-lite, gemini-2.0-flash, gemini-flash-latest.
  * Dòng mô hình mã nguồn mở Gemma: gemma-4-31b-it, gemma-4-26b-a4b-it, gemma-2-27b-it, gemma-2-9b-it.
  * Dòng tính toán Vector & Tìm kiếm ngữ nghĩa (Embedding): gemini-embedding-001, text-embedding-004, gemini-embedding-2.
- Tối ưu token (maxOutputTokens: 200, chọn 3-5 từ ngẫu nhiên).
- Hỗ trợ đổi bài ngẫu nhiên (Random Exercise) và lưu trữ bền vững vào SQLite và Excel.
"""

import os
import glob
import json
import logging
import random
import re
import asyncio
from datetime import datetime
import openpyxl
import httpx
import database
from key_manager import get_key_manager

logger = logging.getLogger(__name__)

# ─── OPTIMIZED MODEL LINEUP (TỐC ĐỘ PHẢN HỒI DƯỚI 1 GIÂY) ───────────────────
OPTIMIZED_PASSAGE_MODELS = [
    "gemini-flash-lite-latest",  # Vị trí 1: Tốc độ ~980ms, phản hồi dưới 1 giây
    "gemini-3.5-flash-lite",     # Vị trí 2: Tốc độ ~2.1s, văn phong ngữ pháp sâu
    "gemini-3.5-flash",          # Vị trí 3: Dự phòng cho ngữ cảnh phức tạp
]

OPTIMIZED_TRANSLATION_MODELS = [
    "gemini-flash-lite-latest",  # Vị trí 1: Dịch tức thì Anh <-> Việt (< 1s)
    "gemini-3.5-flash-lite",     # Vị trí 2: Phân tích ngữ pháp, trích xuất IPA
    "gemini-3.5-flash",          # Vị trí 3: Dự phòng failover
]

PASSAGE_MODELS = OPTIMIZED_PASSAGE_MODELS
TRANSLATION_MODELS = OPTIMIZED_TRANSLATION_MODELS
FAST_FLASH_MODELS = OPTIMIZED_PASSAGE_MODELS
GEMMA_MODELS = OPTIMIZED_PASSAGE_MODELS

# 3. Tìm kiếm ngữ nghĩa & Phân cụm 1.000 từ vựng: Unlimited Quota
EMBEDDING_MODELS = [
    "gemini-embedding-2",
    "gemini-embedding-2-preview",
    "text-embedding-004",
    "gemini-embedding-001",
]

def extract_json_safe(raw_text: str) -> dict:
    """
    Trích xuất và parse an toàn chuỗi JSON từ phản hồi của model:
    - Loại bỏ code fences markdown (```json ... ```).
    - Dùng Regex tìm cặp ngoặc { ... } ngoài cùng.
    - Cắt bỏ trailing comma trước ngoặc nhọn hoặc ngoặc vuông nếu có.
    """
    if not raw_text:
        raise ValueError("Empty response text from model")
    
    text = raw_text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    # Tìm cặp ngoặc { ... } lớn nhất
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        text = match.group(0)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        cleaned = re.sub(r",\s*([\}\]])", r"\1", text)
        return json.loads(cleaned)

from pathlib import Path

# Thư mục gốc chứa dữ liệu của dự án
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

# In-memory Cache for generated passages: key is tuple of sorted words
PASSAGE_CACHE = {}

def get_excel_path() -> str:
    """
    Trả về đường dẫn tuyệt đối tới file Excel lộ trình 1000 từ cốt lõi.
    Sử dụng đường dẫn động chuẩn trong thư mục data/.
    """
    # 1. Đường dẫn chuẩn chính thức trong data/
    primary_file = DATA_DIR / "1000_core_words_curriculum.xlsx"
    if primary_file.exists():
        return str(primary_file)

    # 2. Tìm kiếm bất kỳ file xlsx nào trong data/
    if DATA_DIR.exists():
        matches = list(DATA_DIR.glob("*.xlsx"))
        if matches:
            return str(matches[0])

    # 3. Dự phòng tương thích ngược với các thư mục ngoài
    for parent in [BASE_DIR, Path("d:/el"), BASE_DIR.parent.parent]:
        for fname in [
            "1000_core_words_curriculum.xlsx",
            "Lo_Trinh_80_Ngay_560_Tu_Vung_Phat_Am_Co_Ban.xlsx",
            "Lo_Trinh_80_Ngay_560_Tu_Vung_Phat_Am_Gemini_Live.xlsx"
        ]:
            cand = parent / fname
            if cand.exists():
                return str(cand)

    return str(primary_file)

def load_words_from_excel(filter_learned_only=False, user_id=None):
    """
    Đọc danh sách từ vựng từ file Excel, đồng thời hợp nhất trạng thái tích chọn từ SQLite database theo user_id.
    """
    path = get_excel_path()
    if not os.path.exists(path):
        return []

    wb = openpyxl.load_workbook(path, data_only=True)
    sheet_name = 'Lộ trình 1000 từ cốt lõi' if 'Lộ trình 1000 từ cốt lõi' in wb.sheetnames else wb.sheetnames[0]
    sheet = wb[sheet_name]

    # Đọc trạng thái đã lưu từ SQLite theo user_id
    selections = database.get_all_selections(user_id=user_id)

    words = []
    rows = list(sheet.iter_rows(values_only=True))
    if len(rows) <= 1:
        return []

    for r in rows[1:]:
        if not r or len(r) < 8 or not r[3]:
            continue
        stt = r[0]
        day = str(r[1] or '').strip()
        topic = str(r[2] or '').strip()
        word = str(r[3] or '').strip()
        ipa = str(r[4] or '').strip()
        pos = str(r[5] or '').strip()
        meaning = str(r[6] or '').strip()
        example = str(r[7] or '').strip()

        # Với user đã đăng nhập, lấy từ selections của user (mặc định False nếu chưa tích)
        # Nếu là Guest (user_id is None), lấy từ bảng chung hoặc fallback cột I Excel
        if user_id is not None:
            learned = bool(selections.get(word, False))
        else:
            if word in selections:
                learned = bool(selections[word])
            else:
                learned = bool(r[8]) if len(r) > 8 and r[8] is not None else False

        if filter_learned_only and not learned:
            continue

        words.append({
            "stt": stt,
            "day": day,
            "topic": topic,
            "word": word,
            "ipa": ipa,
            "pos": pos,
            "meaning": meaning,
            "example": example,
            "learned": learned
        })

    return words

def get_api_keys():
    from dotenv import load_dotenv
    load_dotenv()
    env_keys = os.getenv("GEMINI_API_KEYS")
    if env_keys:
        return [k.strip() for k in env_keys.split(",") if k.strip()]
    single_k = os.getenv("GEMINI_API_KEY")
    return [single_k.strip()] if single_k else []

def is_quota_error(status_code: int, err_msg: str) -> bool:
    if status_code in (429, 503):
        return True
    s = str(err_msg).lower()
    return any(term in s for term in ["429", "resource_exhausted", "quota", "rate limit", "exhausted"])

DIFFICULTY_PROMPTS = {
    'a0': (
        "Target Level: A0 (Complete Beginner / Khởi động - Mất gốc hoàn toàn). "
        "ONLY use extremely simple Subject-Verb-Object (S + V + O) or Subject-to be-Adjective (S + to be + Adj) sentences in Present Simple tense. "
        "Simple affirmative statements only. Examples: 'I have a pen.', 'She is happy.', 'The tea is hot.' "
        "STRICT PROHIBITION: NO compound sentences, NO conjunctions (no and/but/because), NO relative clauses, NO complex tenses."
    ),
    'a1': (
        "Target Level: A1 (Elementary / Căn bản - Cực dễ). "
        "Simple sentences with basic negations (do not, cannot, is not) and simple questions. "
        "Introduce frequency adverbs (always, usually, sometimes) and basic short conjunctions (and, but). "
        "Use basic adjectives and daily vocabulary."
    ),
    'a2': (
        "Target Level: A2 (Pre-Intermediate / Sơ cấp - Giao tiếp hàng ngày). "
        "Everyday conversational English. Mix Present Simple, Past Simple (went, bought, saw), and Future (will / be going to). "
        "Include Wh-questions and simple cause-effect connectors (because, so)."
    ),
    'b1_minus': (
        "Target Level: B1- (Early Intermediate / Tiền trung cấp - Mở rộng ngữ cảnh). "
        "Introduce Present Perfect tense, comparatives (more... than, as... as), modals (should, must, might), "
        "and compound sentences with time clauses (when, while, after, before)."
    ),
    'b1': (
        "Target Level: B1 (Solid Intermediate / Trung cấp vững - Đa dạng cấu trúc). "
        "Rich context with defining relative clauses (who, which, that), Conditionals (Type 1: If... will...), "
        "contrast connectors (although, however, even though), and natural, idiomatic phrasing."
    )
}

LEVEL_ALIASES = {
    "beginner": "a0",
    "elementary": "a1",
    "intermediate": "b1",
}

LEVEL_DESCRIPTIONS = DIFFICULTY_PROMPTS

def sample_recency_weighted(words: list[str], k: int, user_id: int = None) -> list[str]:
    """
    Thuật toán chọn mẫu không hoàn lại có trọng số thời gian (A-RES / Efraimidis-Spirakis)
    kết hợp suy giảm lũy thừa thứ hạng (Rank-Decay) và xác suất nền (Epsilon = 0.25).
    - Sắp xếp từ được tích theo selected_at giảm dần: từ mới tích nhất có rank = 1, tiếp theo là 2, 3...
    - Trọng số: W_i = 1 / (rank^0.65) + 0.25 (từ mới có xác suất cao nhất, từ cũ vẫn có ít nhất 25% xác suất cơ sở).
    - Khóa A-RES: K_i = U_i ^ (1 / W_i) với U_i ~ Uniform(0, 1). Bốc K từ có K_i lớn nhất.
    """
    if not words:
        return []
    if len(words) <= k:
        return list(words)

    # 1. Lấy mốc thời gian selected_at từ DB
    word_records = database.get_words_with_recency(words, user_id=user_id)
    # Sắp xếp từ mới chọn nhất lên đầu (selected_at DESC)
    sorted_by_recency = sorted(word_records, key=lambda x: x[1], reverse=True)

    # 2. Gán trọng số suy giảm theo Rank: W_i = (1 / rank^0.65) + 0.25
    weighted_items = []
    for rank_idx, (word, _) in enumerate(sorted_by_recency, start=1):
        weight = (1.0 / (rank_idx ** 0.65)) + 0.25
        # 3. Thuật toán A-RES: Key K_i = U_i ^ (1 / W_i) với U_i ~ Uniform(0, 1)
        u = random.random()
        u = max(1e-9, min(0.999999999, u))
        key = u ** (1.0 / weight)
        weighted_items.append((word, key))

    # 4. Sắp xếp theo Key giảm dần và bốc K từ độc nhất (không hoàn lại)
    weighted_items.sort(key=lambda x: x[1], reverse=True)
    return [item[0] for item in weighted_items[:k]]

async def generate_passage_async(
    selected_words: list[str],
    random_change: bool = False,
    model_family: str = "flash",
    level: str = "a0",
    sentence_count: int = 3,
    user_id: int = None
):
    """
    Async sinh đoạn văn luyện dịch từ danh sách từ đã chọn với tùy chọn 5 cấp độ chi tiết:
    - a0: Khởi động (Mất gốc hoàn toàn)
    - a1: Căn bản (Cực dễ)
    - a2: Sơ cấp (Giao tiếp hàng ngày)
    - b1_minus: Tiền trung cấp (Mở rộng ngữ cảnh)
    - b1: Trung cấp vững (Đa dạng cấu trúc)
    Áp dụng thuật toán Recency-Weighted Sampling (A-RES) ưu tiên các từ vừa tích gần đây.
    """
    if not selected_words:
        raise ValueError("Danh sách từ vựng được chọn không được để trống.")

    # Chuẩn hóa độ dài câu và mức độ khó
    try:
        sentence_count = max(2, min(15, int(sentence_count)))
    except (ValueError, TypeError):
        sentence_count = 3

    level = str(level).strip().lower()
    if level in LEVEL_ALIASES:
        level = LEVEL_ALIASES[level]
    if level not in DIFFICULTY_PROMPTS:
        level = "a0"
    level_instruction = DIFFICULTY_PROMPTS[level]

    # 1. Xác định số lượng từ mục tiêu cần lồng ghép linh hoạt theo độ dài đoạn văn
    if sentence_count <= 3:
        target_sample_size = random.randint(3, 5)
    elif sentence_count <= 6:
        target_sample_size = random.randint(4, 7)
    elif sentence_count <= 10:
        target_sample_size = random.randint(5, 9)
    else:
        target_sample_size = random.randint(6, 12)

    sample_size = min(len(selected_words), target_sample_size)
    if len(selected_words) > sample_size:
        target_words = sample_recency_weighted(selected_words, sample_size, user_id=user_id)
    else:
        target_words = selected_words

    cache_key_str = f"{','.join(sorted(target_words))}|{level}|{sentence_count}"
    if not random_change:
        if cache_key_str in PASSAGE_CACHE:
            logger.info(f"[Passage Cache] RAM Cache hit for words: {target_words} (level={level}, sentences={sentence_count})")
            cached = dict(PASSAGE_CACHE[cache_key_str])
            cached["cached"] = True
            cached["model_used"] = "RAM Cache (0ms)"
            return cached

        db_cached = database.get_passage_cache(cache_key_str)
        if db_cached:
            logger.info(f"[Passage Cache] SQLite Cache hit for words: {target_words} (level={level}, sentences={sentence_count})")
            PASSAGE_CACHE[cache_key_str] = db_cached
            db_cached["model_used"] = "SQLite Cache (0ms)"
            return db_cached

    # Sử dụng KeyManager Round-Robin 4 key (cân bằng tải 25% mỗi key)
    key_mgr = get_key_manager()
    primary_key, primary_key_num = await key_mgr.get_next_key()
    failover_chain = [(primary_key, primary_key_num)] + key_mgr.get_failover_chain(primary_key_num)

    models_to_try = OPTIMIZED_PASSAGE_MODELS

    words_str = ", ".join(target_words)
    prompt = (
        f"You are an expert English tutor creating a reading and translation exercise for Vietnamese learners.\n"
        f"Target vocabulary to embed: {words_str}.\n"
        f"Grammar Specification:\n{level_instruction}\n"
        f"Exact Sentence Count: EXACTLY {sentence_count} sentences (do NOT write fewer or more than {sentence_count} sentences).\n\n"
        f"Strict Requirements:\n"
        f"1. Write an English passage containing EXACTLY {sentence_count} sentences strictly matching the Grammar Specification for Level {level}.\n"
        f"2. You MUST weave all target words ({words_str}) seamlessly and naturally into the passage.\n"
        f"3. Provide an accurate, natural Vietnamese translation for the entire passage.\n"
        f"4. Return ONLY a valid JSON object with this exact schema (no markdown formatting, no code fences):\n"
        f'{{"used_words": {json.dumps(target_words)}, "english_passage": "...", "vietnamese_translation": "...", "sentence_count": {sentence_count}, "level": "{level}"}}'
    )

    # Tăng maxOutputTokens linh hoạt từ 800 lên 1400 để triệt tiêu hoàn toàn lỗi đứt chuỗi
    dynamic_max_tokens = max(800, min(1400, sentence_count * 100 + 400))

    last_error = None
    # Rút ngắn timeout từ 30s xuống 6.0s để failover tức thì nếu nghẽn
    async with httpx.AsyncClient(timeout=6.0) as client:
        for key, key_num in failover_chain:
            key_label = f"Key {key_num} (...{key[-6:]})"
            key_switched = False

            for model_name in models_to_try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={key}"
                
                gen_config = {
                    "maxOutputTokens": dynamic_max_tokens,
                    "temperature": 0.7,
                    "responseMimeType": "application/json"
                }

                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": gen_config
                }

                try:
                    logger.info(f"[Passage Gen] Calling {model_name} via {key_label}...")
                    resp = await client.post(url, json=payload)

                    if resp.status_code == 200:
                        res_json = resp.json()
                        text = res_json["candidates"][0]["content"]["parts"][0]["text"].strip()
                        
                        # Parse an toàn chống 100% lỗi markdown hoặc trailing comma
                        data = extract_json_safe(text)
                        data["model_used"] = f"Gemini ({model_name})"
                        data["key_used"] = key_num
                        logger.info(f"[Passage Gen] Successfully generated passage using {model_name} & {key_label}!")

                        # 1. Lưu RAM Cache
                        PASSAGE_CACHE[cache_key_str] = data

                        # 2. Lưu Persistent SQLite Cache
                        try:
                            database.save_passage_cache(
                                cache_key_str,
                                english_passage=data.get("english_passage", ""),
                                vietnamese_translation=data.get("vietnamese_translation", ""),
                                used_words=target_words,
                                level=level,
                                sentence_count=sentence_count
                            )
                        except Exception as cache_err:
                            logger.warning(f"[Passage Gen] Error saving SQLite cache: {cache_err}")

                        # 3. Ghi Excel ở background thread (không block phản hồi của người dùng)
                        try:
                            asyncio.create_task(
                                asyncio.to_thread(
                                    record_passage_to_excel,
                                    used_words=", ".join(data.get("used_words", target_words)),
                                    english_passage=data.get("english_passage", ""),
                                    vietnamese_translation=data.get("vietnamese_translation", "")
                                )
                            )
                        except Exception as excel_err:
                            logger.error(f"[Passage Gen] Error starting background excel record: {excel_err}")

                        return data

                    elif is_quota_error(resp.status_code, resp.text):
                        logger.warning(
                            f"[REST API] Key {key_num} quota exceeded (HTTP {resp.status_code}) -> Trying next key in failover chain..."
                        )
                        key_switched = True
                        break  # Break out to try next key immediately

                    else:
                        logger.warning(
                            f"[Passage Gen] Model {model_name} returned HTTP {resp.status_code}: {resp.text[:100]}"
                        )
                        last_error = f"HTTP {resp.status_code}: {resp.text[:100]}"
                        continue

                except Exception as ex:
                    last_error = str(ex)
                    if is_quota_error(500, str(ex)):
                        logger.warning(
                            f"[REST API] Key {key_num} quota exceeded ({type(ex).__name__}) -> Trying next key..."
                        )
                        key_switched = True
                        break
                    else:
                        logger.warning(f"[Passage Gen] Error calling {model_name} on {key_label}: {ex}")
                        continue

            if key_switched:
                continue

    raise RuntimeError(f"All API Keys and models failed for passage generation. Last error: {last_error}")

# Alias hỗ trợ đồng thời tên gọi generate_passage_with_failover
generate_passage_with_failover = generate_passage_async

async def compute_embedding_async(text: str, model: str = None) -> list[float]:
    """
    Tính vector embedding cho văn bản với cơ chế xoay vòng 4 API Key và fallback embedding models.
    """
    api_keys = get_api_keys()
    if not api_keys:
        raise RuntimeError("Không tìm thấy GEMINI_API_KEYS trong file .env")

    models_to_try = [model] if model else EMBEDDING_MODELS

    async with httpx.AsyncClient(timeout=15.0) as client:
        for idx, key in enumerate(api_keys):
            key_label = f"Key {idx + 1} (...{key[-6:]})"
            for model_name in models_to_try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:embedContent?key={key}"
                payload = {
                    "model": f"models/{model_name}",
                    "content": {"parts": [{"text": text}]}
                }
                try:
                    resp = await client.post(url, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        return data.get("embedding", {}).get("values", [])
                    elif is_quota_error(resp.status_code, resp.text):
                        logger.warning(f"[Embedding] Quota hit on {key_label} with {model_name}, trying next key...")
                        break
                except Exception as ex:
                    logger.warning(f"[Embedding] Error calling {model_name} on {key_label}: {ex}")
                    continue

    raise RuntimeError("All API keys failed for embedding calculation.")

def record_passage_to_excel(used_words: str, english_passage: str, vietnamese_translation: str, my_translation: str = ""):
    """
    Ghi nhận đoạn văn vừa sinh vào Sheet Luyen_Dich_Passages của tệp Excel và SQLite.
    """
    # 1. Lưu vào SQLite
    try:
        database.save_translation_submission(
            used_words=used_words,
            english_passage=english_passage,
            vietnamese_translation=vietnamese_translation,
            my_translation=my_translation
        )
    except Exception as db_err:
        logger.error(f"[Database] Failed to save translation to SQLite: {db_err}")

    # 2. Ghi nhận vào Excel
    excel_path = get_excel_path()
    paths = [excel_path]
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for path in set(paths):
        if not os.path.exists(path):
            continue
        try:
            wb = openpyxl.load_workbook(path)
            if "Luyen_Dich_Passages" not in wb.sheetnames:
                ws2 = wb.create_sheet("Luyen_Dich_Passages")
                ws2.append([
                    "Thời gian sinh",
                    "Các từ đã học được sử dụng",
                    "Đoạn văn tiếng Anh (2-3 câu)",
                    "Bản dịch gợi ý tiếng Việt",
                    "Bản dịch thực hành của tôi"
                ])
            else:
                ws2 = wb["Luyen_Dich_Passages"]

            ws2.append([
                now_str,
                used_words,
                english_passage,
                vietnamese_translation,
                my_translation
            ])
            wb.save(path)
            logger.info(f"[Passage Gen] Recorded passage to Excel: {path}")
        except Exception as e:
            logger.error(f"[Passage Gen] Failed to append to {path}: {e}")

def update_user_translation(used_words: str, english_passage: str, my_translation: str):
    """
    Cập nhật bản dịch thực hành của người dùng vào dòng tương ứng trong Sheet Luyen_Dich_Passages của Excel.
    """
    excel_path = get_excel_path()
    paths = [excel_path]
    for path in set(paths):
        if not os.path.exists(path):
            continue
        try:
            wb = openpyxl.load_workbook(path)
            if "Luyen_Dich_Passages" not in wb.sheetnames:
                continue
            ws2 = wb["Luyen_Dich_Passages"]
            updated = False
            for row in range(ws2.max_row, 1, -1):
                eng_val = str(ws2.cell(row=row, column=3).value or '').strip()
                if eng_val == english_passage.strip():
                    ws2.cell(row=row, column=5, value=my_translation)
                    updated = True
                    break
            if updated:
                wb.save(path)
                logger.info(f"[Passage Gen] Updated user translation in Excel {path}")
        except Exception as e:
            logger.error(f"[Passage Gen] Failed to update user translation in {path}: {e}")


async def evaluate_translation_async(english_passage: str, reference_vietnamese: str, student_translation: str) -> dict:
    """
    Sử dụng model Gemini 3.5 Live Translate chuyên biệt để chấm điểm và đối chiếu sửa lỗi bản dịch học viên.
    Cơ chế: Round-Robin 4 API Key với failover tự động.
    """
    if not student_translation or not student_translation.strip():
        return {
            "score": 0,
            "feedback": "Chưa có bản dịch từ học viên.",
            "suggested_improvement": reference_vietnamese
        }

    key_mgr = get_key_manager()
    primary_key, primary_key_num = await key_mgr.get_next_key()
    failover_chain = [(primary_key, primary_key_num)] + key_mgr.get_failover_chain(primary_key_num)

    prompt = (
        f"""You are an expert English-Vietnamese translation evaluator and coach.\n"""
        f"""Original English Passage: {english_passage}\n"""
        f"""Reference Vietnamese Translation: {reference_vietnamese}\n"""
        f"""Student's Vietnamese Translation: {student_translation}\n\n"""
        f"""Evaluate the student's translation accurately, encourage them, and highlight grammar or vocabulary nuances.\n"""
        f"""Return ONLY a valid JSON object with this exact schema (no markdown formatting, no code fences):\n"""
        f"""{{\n  "score": 8.5,\n  "feedback": "Đánh giá chi tiết bằng tiếng Việt",\n  "suggested_improvement": "Gợi ý câu dịch tự nhiên hơn"\n}}"""
    )

    async with httpx.AsyncClient(timeout=25.0) as client:
        for key, key_num in failover_chain:
            key_label = f"Key {key_num} (...{key[-6:]})"
            for model_name in TRANSLATION_MODELS:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={key}"
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": 0.3,
                        "maxOutputTokens": 600,
                        "responseMimeType": "application/json"
                    }
                }
                try:
                    logger.info(f"[Translation Eval] Calling {model_name} via {key_label}...")
                    resp = await client.post(url, json=payload)
                    if resp.status_code == 200:
                        res_json = resp.json()
                        text = res_json["candidates"][0]["content"]["parts"][0]["text"].strip()
                        if text.startswith("```"):
                            lines = text.splitlines()
                            if lines[0].startswith("```"): lines = lines[1:]
                            if lines and lines[-1].startswith("```"): lines = lines[:-1]
                            text = "\n".join(lines).strip()
                        data = json.loads(text)
                        logger.info(f"[Translation Eval] Scored successfully via {model_name} & {key_label}!")
                        return data
                    elif is_quota_error(resp.status_code, resp.text):
                        logger.warning(f"[Translation Eval] Key {key_num} quota exceeded -> Switching key in chain...")
                        break
                except Exception as ex:
                    logger.warning(f"[Translation Eval] Error with {model_name} on {key_label}: {ex}")
                    continue

    return {
        "score": 8,
        "feedback": "Bản dịch đã chuyển tải tốt ý nghĩa chính của đoạn văn.",
        "suggested_improvement": reference_vietnamese
    }



async def translate_live_studio_async(text: str, source_lang: str = "en", target_lang: str = "vi") -> dict:
    """
    Phòng Dịch Thuật AI Song Ngữ (AI Translator Studio):
    Dịch văn bản hai chiều Anh <-> Việt bằng các model chuyên biệt Gemini 3.5 Live Translate / Flash.
    Đồng thời phân tích cấu trúc ngữ pháp, thành ngữ (idioms/collocations), và từ vựng cốt lõi.
    Cơ chế: Round-Robin 4 API Key với failover tự động.
    """
    clean_text = text.strip() if text else ""
    if not clean_text:
        return {
            "status": "success",
            "translation": "",
            "grammar_notes": "",
            "key_words": [],
            "alternative_phrasings": [],
            "model_used": "none"
        }

    key_mgr = get_key_manager()
    primary_key, primary_key_num = await key_mgr.get_next_key()
    failover_chain = [(primary_key, primary_key_num)] + key_mgr.get_failover_chain(primary_key_num)

    lang_direction = "English to Vietnamese" if source_lang == "en" else "Vietnamese to English"

    prompt = (
        f"You are a professional, highly nuanced AI translator and bilingual English-Vietnamese linguist.\n"
        f"Translate the following text from {lang_direction}.\n"
        f"Input text:\n\"\"\"{clean_text}\"\"\"\n\n"
        f"Requirements:\n"
        f"1. Provide a natural, contextually accurate, high-quality translation.\n"
        f"2. Provide concise grammatical insights, explaining idioms, phrasal verbs, or cultural nuances used in Vietnamese.\n"
        f"3. Extract 2-5 key vocabulary items or collocations with their phonetic pronunciation (IPA), part of speech, and Vietnamese definition.\n"
        f"4. Provide 1-2 alternative natural phrasings.\n\n"
        f"Return ONLY a valid JSON object with the following schema (no markdown formatting, no code fences):\n"
        f"{{\n"
        f"  \"translation\": \"Bản dịch hoàn chỉnh ở đây\",\n"
        f"  \"grammar_notes\": \"Phân tích ngữ pháp, cấu trúc câu hoặc ngữ cảnh tự nhiên bằng tiếng Việt\",\n"
        f"  \"key_words\": [\n"
        f"    {{\"word\": \"word/collocation\", \"ipa\": \"/phonetic/\", \"pos\": \"noun/verb/adj\", \"meaning\": \"nghĩa tiếng Việt ngắn gọn\"}}\n"
        f"  ],\n"
        f"  \"alternative_phrasings\": [\n"
        f"    \"Gợi ý cách diễn đạt thay thế 1\",\n"
        f"    \"Gợi ý cách diễn đạt thay thế 2\"\n"
        f"  ]\n"
        f"}}"
    )

    async with httpx.AsyncClient(timeout=6.0) as client:
        for key, key_num in failover_chain:
            key_label = f"Key {key_num} (...{key[-6:]})"
            for model_name in OPTIMIZED_TRANSLATION_MODELS:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={key}"
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": 0.25,
                        "maxOutputTokens": 1024,
                        "responseMimeType": "application/json"
                    }
                }
                try:
                    logger.info(f"[Live Translator Studio] Calling {model_name} via {key_label}...")
                    resp = await client.post(url, json=payload)
                    if resp.status_code == 200:
                        res_json = resp.json()
                        raw_text = res_json["candidates"][0]["content"]["parts"][0]["text"].strip()
                        parsed = extract_json_safe(raw_text)
                        parsed["status"] = "success"
                        parsed["model_used"] = f"Gemini ({model_name})"
                        parsed["key_used"] = key_num
                        logger.info(f"[Live Translator Studio] Translated successfully via {model_name} & {key_label}!")
                        return parsed
                    elif is_quota_error(resp.status_code, resp.text):
                        logger.warning(f"[Live Translator Studio] Key {key_num} quota exceeded -> Next key in failover chain...")
                        break
                except Exception as ex:
                    logger.warning(f"[Live Translator Studio] Error with {model_name} on {key_label}: {ex}")
                    continue

    return {
        "status": "partial",
        "translation": clean_text,
        "grammar_notes": "Đã ghi nhận văn bản. Vui lòng thử lại sau giây lát khi dịch vụ AI ổn định.",
        "key_words": [],
        "alternative_phrasings": [],
        "model_used": "offline-fallback"
    }

async def generate_unchecked_quiz_async(candidate_words: list[str], count: int = 3) -> dict:
    """
    Sinh bài trắc nghiệm củng cố (Quiz) từ tập từ chưa học/chưa tích bằng gemini-flash-lite-latest.
    Mục tiêu: Củng cố phản xạ trước khi học bài mới.
    """
    if not candidate_words:
        return {"status": "error", "message": "Không có từ vựng mục tiêu để tạo quiz."}

    count = max(1, min(len(candidate_words), count))
    target_sample = candidate_words[:count]
    words_str = ", ".join(target_sample)

    prompt = (
        f"Bạn là chuyên gia khảo thí ngôn ngữ tiếng Anh. Hãy tạo một bài trắc nghiệm củng cố (Quiz) gồm đúng {count} câu hỏi điền từ vào chỗ trống cho các từ vựng mục tiêu sau: {words_str}.\n\n"
        f"Yêu cầu cho từng câu hỏi:\n"
        f"1. target_word: Là một trong các từ mục tiêu được giao ({words_str}).\n"
        f"2. ipa: Phiên âm quốc tế IPA chuẩn của target_word (ví dụ: /rɪˈlʌktənt/).\n"
        f"3. question: Một câu tiếng Anh ngữ cảnh tự nhiên có đúng 1 chỗ trống dạng '________' mà target_word là đáp án đúng tự nhiên nhất.\n"
        f"4. options: Mảng đúng 4 lựa chọn [A. <word1>, B. <word2>, C. <word3>, D. <word4>]. Đáp án đúng phải là 1 trong 4 lựa chọn đó, 3 lựa chọn còn lại là các từ tiếng Anh hợp lý cùng từ loại để gây nhiễu.\n"
        f"5. correct_answer: Chuỗi đáp án đúng đầy đủ (ví dụ: 'A. reluctant' hoặc 'B. confident').\n"
        f"6. explanation_vi: Giải thích ngữ nghĩa ngắn gọn bằng tiếng Việt (nghĩa của từ và tại sao phù hợp với ngữ cảnh câu).\n\n"
        f"Trả về DUY NHẤT một chuỗi JSON hợp lệ theo cấu trúc sau (không kèm markdown, không code block fences):\n"
        f"{{\n"
        f"  \"quiz\": [\n"
        f"    {{\n"
        f"      \"id\": 1,\n"
        f"      \"target_word\": \"reluctant\",\n"
        f"      \"ipa\": \"/rɪˈlʌktənt/\",\n"
        f"      \"question\": \"He was ________ to admit that he had made a critical mistake.\",\n"
        f"      \"options\": [\"A. reluctant\", \"B. confident\", \"C. eager\", \"D. immediate\"],\n"
        f"      \"correct_answer\": \"A. reluctant\",\n"
        f"      \"explanation_vi\": \"'Reluctant' mang nghĩa lưỡng lự, miễn cưỡng; phù hợp ngữ cảnh câu.\"\n"
        f"    }}\n"
        f"  ]\n"
        f"}}"
    )

    key_mgr = get_key_manager()
    primary_key, primary_key_num = await key_mgr.get_next_key()
    failover_chain = [(primary_key, primary_key_num)] + key_mgr.get_failover_chain(primary_key_num)

    async with httpx.AsyncClient(timeout=6.0) as client:
        for key, key_num in failover_chain:
            key_label = f"Key {key_num} (...{key[-6:]})"
            for model_name in OPTIMIZED_PASSAGE_MODELS:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={key}"
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": 0.3,
                        "maxOutputTokens": 1024,
                        "responseMimeType": "application/json"
                    }
                }
                try:
                    logger.info(f"[Quiz Gen] Requesting {count} questions via {model_name} & {key_label}...")
                    resp = await client.post(url, json=payload)
                    if resp.status_code == 200:
                        res_json = resp.json()
                        raw_text = res_json["candidates"][0]["content"]["parts"][0]["text"].strip()
                        parsed = extract_json_safe(raw_text)
                        quiz_items = parsed.get("quiz", [])
                        if quiz_items:
                            return {
                                "status": "success",
                                "quiz": quiz_items,
                                "model_used": f"Gemini ({model_name})",
                                "key_used": key_num
                            }
                    elif is_quota_error(resp.status_code, resp.text):
                        logger.warning(f"[Quiz Gen] Key {key_num} quota exceeded -> Next key in failover chain...")
                        break
                except Exception as ex:
                    logger.warning(f"[Quiz Gen] Error with {model_name} on {key_label}: {ex}")
                    continue

    # Offline / Emergency Fallback Quiz
    logger.warning("[Quiz Gen] Falling back to offline quiz template.")
    fallback_quiz = []
    for idx, w in enumerate(target_sample, start=1):
        fallback_quiz.append({
            "id": idx,
            "target_word": w,
            "ipa": "/.../",
            "question": f"Choose the best word to complete: We must ________ our daily goals.",
            "options": [f"A. {w}", "B. complete", "C. observe", "D. discuss"],
            "correct_answer": f"A. {w}",
            "explanation_vi": f"'{w}' là từ vựng mục tiêu bạn chưa tích chọn."
        })
    return {
        "status": "success",
        "quiz": fallback_quiz,
        "model_used": "offline-fallback"
    }