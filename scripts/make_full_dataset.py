# scripts/make_full_dataset.py
import sys, os
sys.path.insert(0, os.path.abspath("."))
import json
import openpyxl

def generate_oxford_expansion():
    excel_path = os.path.join("data", "1000_core_words_curriculum.xlsx")
    wb = openpyxl.load_workbook(excel_path, data_only=True)
    sheet = wb.active
    existing_words = set()
    for r in list(sheet.iter_rows(values_only=True))[1:]:
        if r and r[3]:
            existing_words.add(str(r[3]).strip().lower())
    
    print(f"Existing words in Excel: {len(existing_words)}")

    # Load curated list from build_oxford_words
    from scripts.build_oxford_words import get_expansion_dataset
    curated = get_expansion_dataset()
    print(f"Curated list count: {len(curated)}")

    pool = []
    added = set(existing_words)

    for item in curated:
        w = item[0].lower().strip()
        if w not in added:
            added.add(w)
            pool.append({
                "word": w,
                "ipa": item[1],
                "pos": item[2],
                "meaning_vi": item[3],
                "example_sentence": item[4],
                "topic": item[5],
                "level": item[6],
                "is_custom": 0
            })

    print(f"Pool count after curated: {len(pool)}")
    return pool, added

if __name__ == "__main__":
    generate_oxford_expansion()
