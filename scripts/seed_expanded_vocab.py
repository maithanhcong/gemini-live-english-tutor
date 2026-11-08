# scripts/seed_expanded_vocab.py
"""
Script xây dựng và nạp toàn bộ 2.850 từ vựng chuẩn Oxford 3000 vào SQLite `vocab_dictionary`
và bảo toàn 100% tiến độ học tập trong `user_vocab_progress` và `vocab_selection`.
"""
import os
import sys
sys.path.insert(0, os.path.abspath("."))
import openpyxl
import sqlite3
import database
import passage_service

from scripts.build_oxford_words import get_expansion_dataset
from scripts.oxford_themes_pool import get_theme_data
from scripts.oxford_extended_pool import get_extended_records
from scripts.oxford_extended_pool_2 import get_extended_records_2
from scripts.oxford_supplemental import get_supplemental_pool
from scripts.oxford_full_catalog import get_catalog_words
from scripts.oxford_final_batch import get_final_batch

def run_seed():
    print("=" * 60)
    print("BẮT ĐẦU QUÁ TRÌNH SEED KHO TỪ VỰNG OXFORD 3000 VÀO SQLITE")
    print("=" * 60)

    # 1. Khởi tạo cấu trúc bảng SQLite
    database.init_db()

    # 2. Đọc 1.000 từ cốt lõi từ file Excel
    excel_path = os.path.join("data", "1000_core_words_curriculum.xlsx")
    wb = openpyxl.load_workbook(excel_path, data_only=True)
    sheet = wb.active

    all_vocab = []
    seen = set()

    for idx, r in enumerate(list(sheet.iter_rows(values_only=True))[1:], 1):
        if not r or not r[3]:
            continue
        w = str(r[3]).strip().lower()
        if w in seen:
            continue
        seen.add(w)
        all_vocab.append({
            "word": w,
            "ipa": str(r[4] or "").strip(),
            "pos": str(r[5] or "").strip(),
            "meaning_vi": str(r[6] or "").strip(),
            "example_sentence": str(r[7] or "").strip(),
            "topic": str(r[2] or "Chủ đề cốt lõi").strip(),
            "level": "A1" if idx <= 400 else ("A2" if idx <= 800 else "B1"),
            "is_custom": 0
        })

    print(f"[1] Đã nạp thành công {len(all_vocab)} từ cốt lõi từ Excel.")

    # 3. Nạp danh mục các từ mở rộng đã chuẩn hóa
    pools = [
        ("Curated 1 (Mandatory & Core Expansion)", get_expansion_dataset()),
        ("Curated 2 (Extended 1)", get_extended_records()),
        ("Curated 3 (Extended 2)", get_extended_records_2()),
        ("Curated 4 (Supplemental)", get_supplemental_pool()),
        ("Curated 5 (Catalog Words)", get_catalog_words()),
        ("Curated 6 (Final Batch)", get_final_batch())
    ]

    for label, items in pools:
        added_cnt = 0
        for item in items:
            if isinstance(item, dict):
                w = item["word"].strip().lower()
                if w not in seen:
                    seen.add(w)
                    all_vocab.append(item)
                    added_cnt += 1
            elif isinstance(item, (list, tuple)):
                w = item[0].strip().lower()
                if w not in seen:
                    seen.add(w)
                    all_vocab.append({
                        "word": w,
                        "ipa": item[1],
                        "pos": item[2],
                        "meaning_vi": item[3],
                        "example_sentence": item[4],
                        "topic": item[5],
                        "level": item[6],
                        "is_custom": 0
                    })
                    added_cnt += 1
        print(f"[2] Nạp {added_cnt} từ từ {label}. Tổng hiện tại: {len(all_vocab)}")

    # Nạp từ Themes
    theme_cnt = 0
    for topic, words in get_theme_data().items():
        for item in words:
            w = item[0].strip().lower()
            if w not in seen:
                seen.add(w)
                all_vocab.append({
                    "word": w,
                    "ipa": item[1],
                    "pos": item[2],
                    "meaning_vi": item[3],
                    "example_sentence": item[4],
                    "topic": topic,
                    "level": item[5],
                    "is_custom": 0
                })
                theme_cnt += 1
    print(f"[2] Nạp {theme_cnt} từ từ Thematic Pool. Tổng hiện tại: {len(all_vocab)}")

    target_count = 2850
    print(f"[3] Tổng số từ chuẩn bị đưa vào database: {len(all_vocab)} (Chỉ tiêu: {target_count})")
    assert len(all_vocab) == target_count, f"Dữ liệu chưa khớp: Có {len(all_vocab)}, cần {target_count}"

    # 4. Lưu vào bảng vocab_dictionary trong SQLite
    conn = database.get_connection()
    cursor = conn.cursor()

    db_records = [
        (
            item["word"],
            item.get("ipa", ""),
            item.get("pos", ""),
            item.get("meaning_vi", item.get("meaning", "")),
            item.get("example_sentence", item.get("example", "")),
            item.get("topic", "Chủ đề chung"),
            item.get("level", "A1"),
            item.get("is_custom", 0)
        )
        for item in all_vocab
    ]

    cursor.executemany("""
        INSERT OR REPLACE INTO vocab_dictionary 
        (word, ipa, pos, meaning_vi, example_sentence, topic, level, is_custom)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, db_records)
    conn.commit()
    print(f"[4] Đã nạp thành công {len(db_records)} bản ghi vào bảng vocab_dictionary.")

    # 5. Đồng bộ vào bảng user_vocab_progress cho tất cả người dùng hiện có
    users = cursor.execute("SELECT id, username FROM users").fetchall()
    print(f"[5] Đồng bộ tiến độ cho {len(users)} người dùng đã đăng ký...")

    for u in users:
        u_id = u["id"]
        cursor.execute("""
            INSERT OR IGNORE INTO user_vocab_progress (user_id, word, is_mastered, selected_at)
            SELECT ?, word, 0, 0 FROM vocab_dictionary;
        """, (u_id,))
    conn.commit()

    # Đồng bộ vào bảng vocab_selection cho khách vãng lai (Guest)
    cursor.execute("""
        INSERT OR IGNORE INTO vocab_selection (word, topic, is_selected, selected_at)
        SELECT word, topic, 0, 0 FROM vocab_dictionary;
    """)
    conn.commit()

    # 6. Kiểm tra và xác minh
    cursor.execute("SELECT COUNT(*) FROM vocab_dictionary")
    dict_count = cursor.fetchone()[0]

    cursor.execute("SELECT * FROM vocab_dictionary WHERE word = 'comfortable'")
    row_comf = cursor.fetchone()

    cursor.execute("SELECT * FROM vocab_dictionary WHERE word = 'convenient'")
    row_conv = cursor.fetchone()

    cursor.execute("SELECT * FROM vocab_dictionary WHERE word = 'recommend'")
    row_rec = cursor.fetchone()

    cursor.execute("SELECT * FROM vocab_dictionary WHERE word = 'flexible'")
    row_flex = cursor.fetchone()

    cursor.execute("SELECT * FROM vocab_dictionary WHERE word = 'essential'")
    row_ess = cursor.fetchone()

    cursor.execute("SELECT * FROM vocab_dictionary WHERE word = 'accommodate'")
    row_acc = cursor.fetchone()

    conn.close()

    print("=" * 60)
    print("KẾT QUẢ XÁC MINH CƠ SỞ DỮ LIỆU:")
    print(f"- Tổng số từ trong vocab_dictionary: {dict_count}")
    print(f"- Tra cứu 'comfortable': {dict(row_comf) if row_comf else 'Không tìm thấy'}")
    print(f"- Tra cứu 'convenient': {dict(row_conv) if row_conv else 'Không tìm thấy'}")
    print(f"- Tra cứu 'recommend': {dict(row_rec) if row_rec else 'Không tìm thấy'}")
    print(f"- Tra cứu 'flexible': {dict(row_flex) if row_flex else 'Không tìm thấy'}")
    print(f"- Tra cứu 'essential': {dict(row_ess) if row_ess else 'Không tìm thấy'}")
    print(f"- Tra cứu 'accommodate': {dict(row_acc) if row_acc else 'Không tìm thấy'}")
    print("=" * 60)
    print("HOÀN THÀNH SEED DỮ LIỆU THÀNH CÔNG VÀ AN TOÀN 100%!")

if __name__ == "__main__":
    run_seed()
