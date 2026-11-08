# scripts/build_full_oxford_dict.py
"""
Tổng hợp toàn bộ 2.850 từ vựng chuẩn Oxford 3000 (1.000 từ cốt lõi + 1.850 từ mở rộng)
để nạp vào kho từ vựng SQLite của AuraSpeak AI.
"""
import os
import sys
sys.path.insert(0, os.path.abspath("."))
import openpyxl
import json

from scripts.build_oxford_words import get_expansion_dataset
from scripts.oxford_themes_pool import get_theme_data
from scripts.oxford_extended_pool import get_extended_records
from scripts.oxford_extended_pool_2 import get_extended_records_2

def build_full_dataset():
    excel_path = os.path.join("data", "1000_core_words_curriculum.xlsx")
    wb = openpyxl.load_workbook(excel_path, data_only=True)
    sheet = wb.active

    core_words = []
    seen = set()

    # 1. Đọc 1.000 từ cốt lõi
    for idx, r in enumerate(list(sheet.iter_rows(values_only=True))[1:], 1):
        if not r or not r[3]:
            continue
        w = str(r[3]).strip().lower()
        if w in seen:
            continue
        seen.add(w)
        core_words.append({
            "word": w,
            "ipa": str(r[4] or "").strip(),
            "pos": str(r[5] or "").strip(),
            "meaning_vi": str(r[6] or "").strip(),
            "example_sentence": str(r[7] or "").strip(),
            "topic": str(r[2] or "Chủ đề cốt lõi").strip(),
            "level": "A1" if idx <= 400 else ("A2" if idx <= 800 else "B1"),
            "is_custom": 0
        })

    print(f"Loaded {len(core_words)} core words from Excel.")

    # 2. Tập hợp các từ mở rộng đã định nghĩa
    expansion_words = []

    # Curated batch 1
    for item in get_expansion_dataset():
        w = item[0].strip().lower()
        if w not in seen:
            seen.add(w)
            expansion_words.append({
                "word": w,
                "ipa": item[1],
                "pos": item[2],
                "meaning_vi": item[3],
                "example_sentence": item[4],
                "topic": item[5],
                "level": item[6],
                "is_custom": 0
            })

    # Curated batch 2 (Themes)
    for topic, words in get_theme_data().items():
        for item in words:
            w = item[0].strip().lower()
            if w not in seen:
                seen.add(w)
                expansion_words.append({
                    "word": w,
                    "ipa": item[1],
                    "pos": item[2],
                    "meaning_vi": item[3],
                    "example_sentence": item[4],
                    "topic": topic,
                    "level": item[5],
                    "is_custom": 0
                })

    # Curated batch 3 (Extended 1)
    for item in get_extended_records():
        w = item[0].strip().lower()
        if w not in seen:
            seen.add(w)
            expansion_words.append({
                "word": w,
                "ipa": item[1],
                "pos": item[2],
                "meaning_vi": item[3],
                "example_sentence": item[4],
                "topic": item[5],
                "level": item[6],
                "is_custom": 0
            })

    # Curated batch 4 (Extended 2)
    for item in get_extended_records_2():
        w = item[0].strip().lower()
        if w not in seen:
            seen.add(w)
            expansion_words.append({
                "word": w,
                "ipa": item[1],
                "pos": item[2],
                "meaning_vi": item[3],
                "example_sentence": item[4],
                "topic": item[5],
                "level": item[6],
                "is_custom": 0
            })

    print(f"Curated expansion words collected: {len(expansion_words)}")
    current_total = len(core_words) + len(expansion_words)
    print(f"Current total words: {current_total}")

    target_total = 2850
    needed = target_total - current_total
    print(f"Words needed to reach exactly {target_total}: {needed}")

    if needed > 0:
        # Load supplemental Oxford 3000 words list to complete the exact count
        from scripts.oxford_supplemental import get_supplemental_pool
        supp_records = get_supplemental_pool()
        for item in supp_records:
            if len(core_words) + len(expansion_words) >= target_total:
                break
            w = item["word"].strip().lower()
            if w not in seen:
                seen.add(w)
                expansion_words.append(item)

    final_total = len(core_words) + len(expansion_words)
    print(f"Final total system words: {final_total}")
    assert final_total == target_total, f"Expected {target_total}, got {final_total}"

    all_words = core_words + expansion_words
    out_path = os.path.join("scripts", "oxford_3000_full_dataset.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_words, f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(all_words)} words to {out_path}")
    return all_words

if __name__ == "__main__":
    build_full_dataset()
