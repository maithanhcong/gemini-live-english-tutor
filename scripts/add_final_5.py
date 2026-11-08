# scripts/add_final_5.py
import os, sys, json
sys.path.insert(0, os.path.abspath("."))
import openpyxl

from scripts.build_oxford_words import get_expansion_dataset
from scripts.oxford_themes_pool import get_theme_data
from scripts.oxford_extended_pool import get_extended_records
from scripts.oxford_extended_pool_2 import get_extended_records_2
from scripts.oxford_supplemental import get_supplemental_pool
from scripts.oxford_full_catalog import get_catalog_words
from scripts.oxford_final_batch import get_final_batch

excel_path = os.path.join("data", "1000_core_words_curriculum.xlsx")
wb = openpyxl.load_workbook(excel_path, data_only=True)
sheet = wb.active
seen = set()

for r in list(sheet.iter_rows(values_only=True))[1:]:
    if r and r[3]:
        seen.add(str(r[3]).strip().lower())

for item in get_expansion_dataset():
    seen.add(item[0].strip().lower())
for t, words in get_theme_data().items():
    for item in words:
        seen.add(item[0].strip().lower())
for item in get_extended_records():
    seen.add(item[0].strip().lower())
for item in get_extended_records_2():
    seen.add(item[0].strip().lower())
for item in get_supplemental_pool():
    seen.add(item["word"].strip().lower())
for item in get_catalog_words():
    seen.add(item["word"].strip().lower())
for item in get_final_batch():
    seen.add(item["word"].strip().lower())

needed = 2850 - len(seen)
print(f"Current count: {len(seen)}. Exactly needed: {needed}")

needed_5 = [
    ("magnet", "/ˈmæɡnət/", "noun", "nam châm hút sắt", "The magnetic compass uses a magnetized steel needle.", "Khoa học & Đổi mới", "A2"),
    ("magnetic", "/mæɡˈnetɪk/", "adj", "có từ tính, lôi cuốn", "Her magnetic enthusiasm drew everyone into the conversation.", "Tính từ phẩm chất", "B1"),
    ("magnify", "/ˈmæɡnɪfaɪ/", "verb", "phóng đại hình ảnh", "Microscopes magnify cellular structures a thousand times.", "Khoa học & Đổi mới", "B2"),
    ("magnitude", "/ˈmæɡnɪtjuːd/", "noun", "tầm vóc, cường độ lớn", "We appreciated the monumental magnitude of her linguistic feat.", "Tư duy & Đánh giá", "B2"),
    ("maiden", "/ˈmeɪdn/", "adj", "đầu tiên, trinh nguyên", "The supersonic passenger aircraft completed its maiden voyage.", "Du lịch & Khám phá", "B2"),
]

final_list = get_final_batch()
target = 2850
added = 0
for item in needed_5:
    if len(seen) >= target:
        break
    w = item[0].strip().lower()
    if w not in seen:
        seen.add(w)
        final_list.append({
            "word": w,
            "ipa": item[1],
            "pos": item[2],
            "meaning_vi": item[3],
            "example_sentence": item[4],
            "topic": item[5],
            "level": item[6],
            "is_custom": 0
        })
        added += 1

print(f"Added {added} final words. Total unique words now: {len(seen)}")
assert len(seen) == 2850, f"Expected 2850, got {len(seen)}"

out_file = os.path.join("scripts", "oxford_final_batch.py")
with open(out_file, "w", encoding="utf-8") as f:
    f.write("# scripts/oxford_final_batch.py\n")
    f.write("# Danh mục từ vựng bổ sung cuối cùng đạt chính xác 2.850 từ\n\n")
    f.write("def get_final_batch():\n")
    f.write(f"    return {json.dumps(final_list, ensure_ascii=False, indent=8)}\n")

print(f"Updated {out_file} to reach exact target of 2,850 words!")

