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
from datetime import datetime
import openpyxl
import httpx
import database

logger = logging.getLogger(__name__)

# Model Registry
FAST_FLASH_MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash",
    "gemini-3.5-flash",
    "gemini-flash-latest",
]

GEMMA_MODELS = [
    "gemma-4-31b-it",
    "gemma-4-26b-a4b-it",
    "gemma-2-27b-it",
    "gemma-2-9b-it",
]

EMBEDDING_MODELS = [
    "gemini-embedding-001",
    "text-embedding-004",
    "gemini-embedding-2-preview",
    "gemini-embedding-2",
]

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

async def generate_passage_async(
    selected_words: list[str],
    random_change: bool = False,
    model_family: str = "flash",
    level: str = "a0",
    sentence_count: int = 3
):
    """
    Async sinh đoạn văn luyện dịch từ danh sách từ đã chọn với tùy chọn 5 cấp độ chi tiết:
    - a0: Khởi động (Mất gốc hoàn toàn)
    - a1: Căn bản (Cực dễ)
    - a2: Sơ cấp (Giao tiếp hàng ngày)
    - b1_minus: Tiền trung cấp (Mở rộng ngữ cảnh)
    - b1: Trung cấp vững (Đa dạng cấu trúc)
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
    if random_change or len(selected_words) > sample_size:
        target_words = random.sample(selected_words, sample_size)
    else:
        target_words = selected_words

    cache_key = (tuple(sorted(target_words)), level, sentence_count)
    if not random_change and cache_key in PASSAGE_CACHE:
        logger.info(f"[Passage Cache] Cache hit for words: {target_words} (level={level}, sentences={sentence_count})")
        return PASSAGE_CACHE[cache_key]

    api_keys = get_api_keys()
    if not api_keys:
        raise RuntimeError("Không tìm thấy GEMINI_API_KEYS trong file .env")

    # Chọn danh sách model ưu tiên
    if model_family == "gemma":
        models_to_try = GEMMA_MODELS + FAST_FLASH_MODELS
    else:
        models_to_try = FAST_FLASH_MODELS + GEMMA_MODELS

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

    # Tính toán maxOutputTokens linh hoạt theo số câu để đảm bảo không bao giờ bị đứt câu
    dynamic_max_tokens = max(350, min(1200, sentence_count * 75 + 200))

    last_error = None
    async with httpx.AsyncClient(timeout=30.0) as client:
        for idx, key in enumerate(api_keys):
            key_label = f"Key {idx + 1} (...{key[-6:]})"
            key_switched = False

            for model_name in models_to_try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={key}"
                
                # Cấu hình config: Flash hỗ trợ responseMimeType JSON
                gen_config = {
                    "maxOutputTokens": dynamic_max_tokens,
                    "temperature": 0.7,
                }
                if "flash" in model_name:
                    gen_config["responseMimeType"] = "application/json"

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
                        # Clean potential fences
                        if text.startswith("```"):
                            lines = text.splitlines()
                            if lines[0].startswith("```"):
                                lines = lines[1:]
                            if lines and lines[-1].startswith("```"):
                                lines = lines[:-1]
                            text = "\n".join(lines).strip()

                        data = json.loads(text)
                        logger.info(f"[Passage Gen] Successfully generated passage using {model_name} & {key_label}!")

                        # Save to Cache
                        PASSAGE_CACHE[cache_key] = data

                        # Record into Sheet Luyen_Dich_Passages & SQLite
                        try:
                            record_passage_to_excel(
                                used_words=", ".join(data.get("used_words", target_words)),
                                english_passage=data.get("english_passage", ""),
                                vietnamese_translation=data.get("vietnamese_translation", "")
                            )
                        except Exception as excel_err:
                            logger.error(f"[Passage Gen] Error recording passage: {excel_err}")

                        return data

                    elif is_quota_error(resp.status_code, resp.text):
                        next_idx = (idx + 1) % len(api_keys) + 1
                        print(
                            f"[REST API] Key {idx + 1} quota exceeded (HTTP {resp.status_code}) -> Switching to Key {next_idx}...",
                            flush=True
                        )
                        logger.warning(
                            f"[REST API] Key {idx + 1} quota exceeded (HTTP {resp.status_code}) -> Switching to Key {next_idx}..."
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
                        next_idx = (idx + 1) % len(api_keys) + 1
                        print(
                            f"[REST API] Key {idx + 1} quota exceeded ({type(ex).__name__}) -> Switching to Key {next_idx}...",
                            flush=True
                        )
                        logger.warning(
                            f"[REST API] Key {idx + 1} quota exceeded -> Switching to Key {next_idx}..."
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
