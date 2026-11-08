"""
database.py
Quản lý cơ sở dữ liệu SQLite (study_progress.db) đa người dùng (Multi-user Data Isolation):
1. Bảng users: Quản lý tài khoản, mã hóa mật khẩu an toàn với salt & SHA-256.
2. Bảng user_sessions: Phiên đăng nhập độc lập.
3. Bảng user_vocab_progress: Trạng thái tích chọn từ vựng riêng biệt cho từng người dùng.
4. Bảng user_passages: Lịch sử đoạn văn và bài dịch của từng người dùng.
5. Duy trì tương thích ngược với file Excel và chế độ khách (Guest).
"""

import os
import sqlite3
import logging
import hashlib
import secrets
import time
from datetime import datetime
import openpyxl

logger = logging.getLogger(__name__)

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "study_progress.db"))

def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=15.0)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.row_factory = sqlite3.Row
    return conn

# ─── PASSWORD HASHING & SECURITY ─────────────────────────────────────────────
def hash_password(password: str) -> str:
    """Tạo salt ngẫu nhiên và băm mật khẩu an toàn bằng SHA-256."""
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.sha256(f"{salt}:{password}".encode("utf-8")).hexdigest()
    return f"{salt}${pwd_hash}"

def verify_password(password: str, stored_hash: str) -> bool:
    """Xác thực mật khẩu với stored_hash bằng hàm chống timing-attack."""
    try:
        if not stored_hash or "$" not in stored_hash:
            return False
        salt, pwd_hash = stored_hash.split("$", 1)
        check_hash = hashlib.sha256(f"{salt}:{password}".encode("utf-8")).hexdigest()
        return secrets.compare_digest(pwd_hash, check_hash)
    except Exception:
        return False

# ─── DATABASE INITIALIZATION ────────────────────────────────────────────────
def init_db(excel_words=None):
    """
    Khởi tạo cấu trúc các bảng cho hệ thống đa người dùng nếu chưa tồn tại.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Bảng Users
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Bảng User Sessions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_sessions (
        session_token TEXT PRIMARY KEY,
        user_id INTEGER NOT NULL,
        expires_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    # 3. Bảng User Vocab Progress (Độc lập cho từng user, hỗ trợ Recency-Weighted Sampling)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_vocab_progress (
        user_id INTEGER NOT NULL,
        word TEXT NOT NULL,
        is_mastered INTEGER DEFAULT 0,
        selected_at INTEGER DEFAULT 0,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id, word),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    # 4. Bảng User Passages (Lịch sử bài dịch riêng của từng user)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_passages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        used_words TEXT,
        english_passage TEXT,
        vietnamese_translation TEXT,
        user_translation TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    # 5. Các bảng chung (Legacy / Global fallback)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vocab_selection (
        word TEXT PRIMARY KEY,
        topic TEXT,
        is_selected INTEGER DEFAULT 0,
        selected_at INTEGER DEFAULT 0,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS translations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        used_words TEXT,
        english_passage TEXT,
        vietnamese_translation TEXT,
        my_translation TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 6. Bảng Passage Cache (Persistent AI Cache tăng tốc phản hồi)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS passage_cache (
        cache_key TEXT PRIMARY KEY,
        english_passage TEXT NOT NULL,
        vietnamese_translation TEXT NOT NULL,
        used_words TEXT,
        level TEXT,
        sentence_count INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 7. Bảng Vocab Dictionary (Kho từ vựng chuẩn Oxford 3000 & Từ tùy chỉnh)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vocab_dictionary (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        word TEXT UNIQUE NOT NULL,
        ipa TEXT,
        pos TEXT,
        meaning_vi TEXT,
        example_sentence TEXT,
        topic TEXT,
        level TEXT DEFAULT 'A1',
        is_custom INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_vocab_dict_word ON vocab_dictionary(word);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_vocab_dict_topic ON vocab_dictionary(topic);")

    # Migration: Bổ sung cột selected_at nếu chưa tồn tại
    try:
        cursor.execute("ALTER TABLE user_vocab_progress ADD COLUMN selected_at INTEGER DEFAULT 0;")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE vocab_selection ADD COLUMN selected_at INTEGER DEFAULT 0;")
    except sqlite3.OperationalError:
        pass

    # Index tăng tốc Recency-Weighted Sampling
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_user_vocab_recency 
    ON user_vocab_progress(user_id, is_mastered, selected_at DESC);
    """)
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_vocab_selection_recency 
    ON vocab_selection(is_selected, selected_at DESC);
    """)
    conn.commit()

    # Seed từ vựng ban đầu nếu bảng chung rỗng
    cursor.execute("SELECT COUNT(*) FROM vocab_selection")
    count = cursor.fetchone()[0]

    if count == 0 and excel_words:
        logger.info(f"[Database] Seeding vocab_selection with {len(excel_words)} words from Excel...")
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        records = [
            (w["word"], w.get("topic", ""), 1 if w.get("learned", False) else 0, now_str)
            for w in excel_words if w.get("word")
        ]
        cursor.executemany(
            "INSERT OR REPLACE INTO vocab_selection (word, topic, is_selected, updated_at) VALUES (?, ?, ?, ?)",
            records
        )
        conn.commit()
        logger.info("[Database] Seeding completed.")

    conn.close()

# ─── USER & AUTHENTICATION MANAGEMENT ───────────────────────────────────────
def register_user(username: str, password: str, excel_words=None):
    """
    Đăng ký tài khoản mới. Trả về (user_dict, error_message).
    """
    username = (username or "").strip()
    if len(username) < 3:
        return None, "Tên đăng nhập phải có ít nhất 3 ký tự."
    if len(password or "") < 4:
        return None, "Mật khẩu phải có ít nhất 4 ký tự."

    conn = get_connection()
    cursor = conn.cursor()

    try:
        pwd_hash = hash_password(password)
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, pwd_hash)
        )
        user_id = cursor.lastrowid
        conn.commit()

        # Tự động khởi tạo trạng thái từ vựng mặc định cho tài khoản mới
        # Khởi tạo mặc định: người dùng mới bắt đầu với 0 từ đã học để học từ đầu
        user = {"id": user_id, "username": username}
        logger.info(f"[Auth] Registered new user: {username} (ID: {user_id})")
        return user, None
    except sqlite3.IntegrityError:
        return None, "Tên đăng nhập đã tồn tại. Vui lòng chọn tên khác."
    except Exception as e:
        logger.error(f"[Auth] Register error: {e}")
        return None, f"Lỗi hệ thống khi đăng ký: {e}"
    finally:
        conn.close()

def authenticate_user(username: str, password: str):
    """
    Xác thực người dùng và cấp session_token. Trả về (user_dict, token, error_message).
    """
    username = (username or "").strip()
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id, username, password_hash, created_at FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        if not row:
            return None, None, "Tài khoản không tồn tại."

        if not verify_password(password, row["password_hash"]):
            return None, None, "Mật khẩu không chính xác."

        user_id = row["id"]
        # Tạo session token ngẫu nhiên
        token = secrets.token_urlsafe(32)
        cursor.execute(
            "INSERT INTO user_sessions (session_token, user_id) VALUES (?, ?)",
            (token, user_id)
        )
        conn.commit()

        user = {"id": user_id, "username": row["username"], "created_at": row["created_at"]}
        logger.info(f"[Auth] User logged in: {username} (Token: ...{token[-6:]})")
        return user, token, None
    except Exception as e:
        logger.error(f"[Auth] Login error: {e}")
        return None, None, f"Lỗi đăng nhập: {e}"
    finally:
        conn.close()

def get_user_by_session(session_token: str):
    """
    Lấy thông tin người dùng từ session_token.
    """
    if not session_token:
        return None
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        SELECT u.id, u.username, u.created_at
        FROM user_sessions s
        JOIN users u ON s.user_id = u.id
        WHERE s.session_token = ?
        """, (session_token,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    finally:
        conn.close()

def delete_session(session_token: str):
    """Hủy session khi đăng xuất."""
    if not session_token:
        return
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_sessions WHERE session_token = ?", (session_token,))
    conn.commit()
    conn.close()

def change_user_password(user_id: int, old_password: str, new_password: str) -> tuple[bool, str]:
    """
    Xác thực mật khẩu cũ và cập nhật mật khẩu mới cho user_id.
    """
    if not new_password or len(new_password) < 4:
        return False, "Mật khẩu mới phải có ít nhất 4 ký tự."

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, username, password_hash FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        if not row:
            return False, "Không tìm thấy thông tin tài khoản."

        if not verify_password(old_password, row["password_hash"]):
            return False, "Mật khẩu hiện tại không chính xác."

        new_hash = hash_password(new_password)
        cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, user_id))
        conn.commit()
        logger.info(f"[Auth] Password changed successfully for user ID {user_id} ({row['username']})")
        return True, "Đổi mật khẩu thành công!"
    except Exception as e:
        logger.error(f"[Auth] Error changing password for user {user_id}: {e}")
        return False, f"Lỗi hệ thống khi đổi mật khẩu: {e}"
    finally:
        conn.close()

def reset_user_vocab(user_id: int) -> bool:
    """Xóa toàn bộ các từ đã đánh dấu của user_id (đặt lại về mặc định 0 từ)."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM user_vocab_progress WHERE user_id = ?", (user_id,))
        conn.commit()
        logger.info(f"[Vocab] Reset all vocab selections for user ID {user_id}")
        return True
    except Exception as e:
        logger.error(f"[Vocab] Reset vocab error for user {user_id}: {e}")
        return False
    finally:
        conn.close()

def reset_user_history(user_id: int) -> bool:
    """Xóa toàn bộ lịch sử bài dịch của user_id."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM user_passages WHERE user_id = ?", (user_id,))
        conn.commit()
        logger.info(f"[Passage] Reset translation history for user ID {user_id}")
        return True
    except Exception as e:
        logger.error(f"[Passage] Reset history error for user {user_id}: {e}")
        return False
    finally:
        conn.close()

# ─── MULTI-USER VOCABULARY PROGRESS ─────────────────────────────────────────
def get_user_all_selections(user_id: int) -> dict[str, bool]:
    """Trả về dictionary {word: is_mastered (bool)} của riêng user_id."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT word, is_mastered FROM user_vocab_progress WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return {r["word"]: bool(r["is_mastered"]) for r in rows}

def get_user_selected_words(user_id: int) -> list[str]:
    """Trả về danh sách từ vựng đang được tích chọn (is_mastered = 1) của riêng user_id, sắp xếp theo thứ tự chọn gần nhất."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT word FROM user_vocab_progress WHERE user_id = ? AND is_mastered = 1 ORDER BY selected_at DESC, updated_at DESC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [r["word"] for r in rows]

def update_user_vocab_selection(user_id: int, words: list[str], is_mastered: bool):
    """Cập nhật trạng thái tích chọn cho một nhóm từ của user_id kèm timestamp selected_at."""
    if not words:
        return
    conn = get_connection()
    cursor = conn.cursor()
    val = 1 if is_mastered else 0
    now_epoch = int(time.time()) if is_mastered else 0
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.executemany(
        """
        INSERT INTO user_vocab_progress (user_id, word, is_mastered, selected_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(user_id, word) DO UPDATE SET 
            is_mastered = excluded.is_mastered, 
            selected_at = excluded.selected_at, 
            updated_at = excluded.updated_at
        """,
        [(user_id, w, val, now_epoch, now_str) for w in words]
    )
    conn.commit()
    conn.close()

def set_all_user_selections(user_id: int, selected_words: list[str]):
    """Đồng bộ toàn bộ danh sách từ được tích của user_id."""
    conn = get_connection()
    cursor = conn.cursor()
    now_epoch = int(time.time())
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Đưa tất cả từ của user về 0
    cursor.execute("UPDATE user_vocab_progress SET is_mastered = 0, selected_at = 0, updated_at = ? WHERE user_id = ?", (now_str, user_id))

    # Cập nhật các từ được chọn thành 1 kèm selected_at
    if selected_words:
        cursor.executemany(
            """
            INSERT INTO user_vocab_progress (user_id, word, is_mastered, selected_at, updated_at)
            VALUES (?, ?, 1, ?, ?)
            ON CONFLICT(user_id, word) DO UPDATE SET 
                is_mastered = 1, 
                selected_at = CASE WHEN user_vocab_progress.selected_at > 0 THEN user_vocab_progress.selected_at ELSE excluded.selected_at END,
                updated_at = excluded.updated_at
            """,
            [(user_id, w, now_epoch, now_str) for w in selected_words]
        )
    conn.commit()
    conn.close()

# ─── MULTI-USER TRANSLATIONS & PASSAGES ──────────────────────────────────────
def save_user_translation_submission(user_id: int, used_words: str, english_passage: str, vietnamese_translation: str, user_translation: str) -> int:
    """Lưu bài dịch của riêng user_id vào bảng user_passages."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO user_passages (user_id, used_words, english_passage, vietnamese_translation, user_translation)
        VALUES (?, ?, ?, ?, ?)
        """,
        (user_id, used_words, english_passage, vietnamese_translation, user_translation)
    )
    inserted_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return inserted_id

def get_user_recent_translations(user_id: int, limit: int = 15) -> list[dict]:
    """Lấy danh sách các bài dịch gần nhất của riêng user_id."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, used_words, english_passage, vietnamese_translation, user_translation as my_translation, created_at
        FROM user_passages
        WHERE user_id = ?
        ORDER BY id DESC LIMIT ?
        """,
        (user_id, limit)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ─── LEGACY & FALLBACK FUNCTIONS (CHO GUEST HOẶC BẢO LƯU DỮ LIỆU CŨ) ─────────
def get_all_selections(user_id: int = None) -> dict[str, bool]:
    if user_id:
        return get_user_all_selections(user_id)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT word, is_selected FROM vocab_selection")
    rows = cursor.fetchall()
    conn.close()
    return {r["word"]: bool(r["is_selected"]) for r in rows}

def get_selected_words_list(user_id: int = None) -> list[str]:
    if user_id:
        return get_user_selected_words(user_id)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT word FROM vocab_selection WHERE is_selected = 1 ORDER BY selected_at DESC, updated_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [r["word"] for r in rows]

def get_words_with_recency(words: list[str], user_id: int = None) -> list[tuple[str, int]]:
    """
    Truy vấn timestamp selected_at cho danh sách từ vựng.
    Trả về [(word, selected_at), ...].
    """
    if not words:
        return []
    conn = get_connection()
    cursor = conn.cursor()
    placeholders = ",".join("?" for _ in words)
    try:
        if user_id:
            cursor.execute(
                f"SELECT word, COALESCE(selected_at, 0) as selected_at FROM user_vocab_progress WHERE user_id = ? AND word IN ({placeholders})",
                [user_id] + words
            )
        else:
            cursor.execute(
                f"SELECT word, COALESCE(selected_at, 0) as selected_at FROM vocab_selection WHERE word IN ({placeholders})",
                words
            )
        rows = cursor.fetchall()
        ts_map = {r["word"]: int(r["selected_at"] or 0) for r in rows}
    except Exception as e:
        logger.warning(f"[Recency] Error fetching selected_at: {e}")
        ts_map = {}
    finally:
        conn.close()
    return [(w, ts_map.get(w, 0)) for w in words]

def update_vocab_selection(words: list[str], is_selected: bool, user_id: int = None):
    if user_id:
        return update_user_vocab_selection(user_id, words, is_selected)
    if not words:
        return
    conn = get_connection()
    cursor = conn.cursor()
    val = 1 if is_selected else 0
    now_epoch = int(time.time()) if is_selected else 0
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.executemany(
        """
        INSERT INTO vocab_selection (word, is_selected, selected_at, updated_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(word) DO UPDATE SET 
            is_selected = excluded.is_selected, 
            selected_at = excluded.selected_at, 
            updated_at = excluded.updated_at
        """,
        [(w, val, now_epoch, now_str) for w in words]
    )
    conn.commit()
    conn.close()

def set_all_selections(selected_words: list[str], user_id: int = None):
    if user_id:
        return set_all_user_selections(user_id, selected_words)
    conn = get_connection()
    cursor = conn.cursor()
    now_epoch = int(time.time())
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("UPDATE vocab_selection SET is_selected = 0, selected_at = 0, updated_at = ?", (now_str,))
    if selected_words:
        cursor.executemany(
            """
            INSERT INTO vocab_selection (word, is_selected, selected_at, updated_at)
            VALUES (?, 1, ?, ?)
            ON CONFLICT(word) DO UPDATE SET 
                is_selected = 1, 
                selected_at = CASE WHEN vocab_selection.selected_at > 0 THEN vocab_selection.selected_at ELSE excluded.selected_at END,
                updated_at = excluded.updated_at
            """,
            [(w, now_epoch, now_str) for w in selected_words]
        )
    conn.commit()
    conn.close()

def save_translation_submission(used_words: str, english_passage: str, vietnamese_translation: str, my_translation: str, user_id: int = None) -> int:
    if user_id:
        return save_user_translation_submission(user_id, used_words, english_passage, vietnamese_translation, my_translation)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO translations (used_words, english_passage, vietnamese_translation, my_translation)
        VALUES (?, ?, ?, ?)
        """,
        (used_words, english_passage, vietnamese_translation, my_translation)
    )
    inserted_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return inserted_id

def get_recent_translations(limit: int = 15, user_id: int = None) -> list[dict]:
    if user_id:
        return get_user_recent_translations(user_id, limit)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, used_words, english_passage, vietnamese_translation, my_translation, created_at
        FROM translations
        ORDER BY id DESC LIMIT ?
        """,
        (limit,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def sync_selection_to_excel(selected_words_set: set[str], excel_paths: list[str] = None):
    """
    Đồng bộ trạng thái tích chọn vào cột I (Đã học) của file Excel.
    """
    if not excel_paths:
        from pathlib import Path
        data_dir = Path(__file__).resolve().parent / "data"
        primary_excel = data_dir / "1000_core_words_curriculum.xlsx"
        excel_paths = [str(primary_excel)]

    for path in set(excel_paths):
        if not os.path.exists(path):
            continue
        try:
            wb = openpyxl.load_workbook(path)
            sheet_name = 'Lộ trình 1000 từ cốt lõi' if 'Lộ trình 1000 từ cốt lõi' in wb.sheetnames else wb.sheetnames[0]
            ws = wb[sheet_name]

            for row in range(2, ws.max_row + 1):
                word_val = str(ws.cell(row=row, column=4).value or '').strip()
                if not word_val:
                    continue
                is_checked = word_val in selected_words_set
                ws.cell(row=row, column=9, value=is_checked)

            wb.save(path)
            logger.info(f"[Database Sync] Synchronized selection to Excel column I: {path}")
        except Exception as e:
            logger.error(f"[Database Sync] Failed to update Excel {path}: {e}")

# ─── PASSAGE PERSISTENT CACHE (TỐI ƯU HÓA ĐỘ TRỄ 0MS) ────────────────────────
def get_passage_cache(cache_key: str) -> dict | None:
    """Truy xuất đoạn văn đã lưu trong SQLite persistent cache."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT english_passage, vietnamese_translation, used_words, level, sentence_count FROM passage_cache WHERE cache_key = ?",
            (cache_key,)
        )
        row = cursor.fetchone()
        conn.close()
        if row:
            used_words_list = [w.strip() for w in (row["used_words"] or "").split(",") if w.strip()]
            return {
                "english_passage": row["english_passage"],
                "vietnamese_translation": row["vietnamese_translation"],
                "used_words": used_words_list,
                "level": row["level"],
                "sentence_count": row["sentence_count"],
                "cached": True,
            }
    except Exception as e:
        logger.warning(f"[Cache] Error reading passage_cache: {e}")
    return None

def save_passage_cache(cache_key: str, english_passage: str, vietnamese_translation: str, used_words, level: str, sentence_count: int):
    """Lưu đoạn văn sinh mới vào SQLite persistent cache."""
    try:
        words_str = ", ".join(used_words) if isinstance(used_words, (list, set, tuple)) else str(used_words or "")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO passage_cache (cache_key, english_passage, vietnamese_translation, used_words, level, sentence_count)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (cache_key, english_passage, vietnamese_translation, words_str, level, sentence_count)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        logger.warning(f"[Cache] Error saving passage_cache: {e}")

# ─── OXFORD 3000 & CUSTOM VOCABULARY DICTIONARY ──────────────────────────────
def add_vocab_dictionary_word(word: str, ipa: str = "", pos: str = "", meaning_vi: str = "", example_sentence: str = "", topic: str = "Từ tùy chỉnh", level: str = "B1", is_custom: int = 1):
    """Thêm một từ mới vào kho từ điển SQLite."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO vocab_dictionary (word, ipa, pos, meaning_vi, example_sentence, topic, level, is_custom)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (word.strip().lower(), ipa.strip(), pos.strip(), meaning_vi.strip(), example_sentence.strip(), topic.strip(), level.strip().upper(), is_custom)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"[Database] Error adding vocab word {word}: {e}")
        return False

def add_vocab_dictionary_bulk(records: list):
    """Nạp hàng loạt bản ghi từ vựng vào kho từ điển SQLite."""
    if not records:
        return 0
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.executemany(
            """
            INSERT OR REPLACE INTO vocab_dictionary (word, ipa, pos, meaning_vi, example_sentence, topic, level, is_custom)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            records
        )
        conn.commit()
        count = cursor.rowcount
        conn.close()
        return count
    except Exception as e:
        logger.error(f"[Database] Error bulk inserting vocab words: {e}")
        return 0

def get_vocab_dictionary_count() -> int:
    """Đếm tổng số từ vựng trong kho từ điển SQLite."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM vocab_dictionary")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except Exception as e:
        logger.error(f"[Database] Error counting vocab_dictionary: {e}")
        return 0

def find_vocab_dictionary_word(word: str) -> dict | None:
    """Tìm một từ vựng trong kho từ điển."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vocab_dictionary WHERE word = ?", (word.strip().lower(),))
        row = cursor.fetchone()
        conn.close()
        if row:
            return dict(row)
    except Exception as e:
        logger.error(f"[Database] Error finding vocab word {word}: {e}")
    return None

def get_all_vocab_dictionary(user_id=None, filter_learned_only: bool = False) -> list:
    """
    Lấy toàn bộ từ vựng trong kho từ điển SQLite, đồng thời hợp nhất trạng thái học từ user_vocab_progress / vocab_selection.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, word, ipa, pos, meaning_vi, example_sentence, topic, level, is_custom 
            FROM vocab_dictionary 
            ORDER BY topic ASC, word ASC
        """)
        rows = cursor.fetchall()
        conn.close()

        selections = get_all_selections(user_id=user_id)
        words = []
        for r in rows:
            w_word = r["word"]
            learned = bool(selections.get(w_word, False))
            if filter_learned_only and not learned:
                continue
            words.append({
                "stt": r["id"],
                "day": "",
                "topic": r["topic"] or "Chủ đề chung",
                "word": w_word,
                "ipa": r["ipa"] or "",
                "pos": r["pos"] or "",
                "meaning": r["meaning_vi"] or "",
                "example": r["example_sentence"] or "",
                "level": r["level"] or "A1",
                "is_custom": bool(r["is_custom"]),
                "learned": learned
            })
        return words
    except Exception as e:
        logger.error(f"[Database] Error fetching all vocab dictionary: {e}")
        return []

def sync_user_vocab_defaults(user_id=None):
    """
    Đảm bảo tất cả các từ trong kho từ điển đều có mặt trong user_vocab_progress (hoặc vocab_selection).
    Dùng INSERT OR IGNORE để bảo toàn 100% tiến độ học đã có.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        if user_id is not None:
            cursor.execute("""
                INSERT OR IGNORE INTO user_vocab_progress (user_id, word, is_mastered, selected_at)
                SELECT ?, word, 0, 0 FROM vocab_dictionary;
            """, (user_id,))
        else:
            cursor.execute("""
                INSERT OR IGNORE INTO vocab_selection (word, topic, is_selected, selected_at)
                SELECT word, topic, 0, 0 FROM vocab_dictionary;
            """)
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"[Database] Error syncing user vocab defaults: {e}")

