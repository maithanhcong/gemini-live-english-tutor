# scripts/add_final_37.py
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

print(f"Current count: {len(seen)}. Exactly needed: {2850 - len(seen)}")

needed_37 = [
    ("knowledge", "/ˈnɒlɪdʒ/", "noun", "kiến thức, sự hiểu biết", "Broad knowledge of vocabulary empowers confident conversation.", "Giáo dục & Học thuật", "A2"),
    ("knowledgeable", "/ˈnɒlɪdʒəbl/", "adj", "am hiểu, uyên bác", "The AI companion is remarkably knowledgeable across all themes.", "Giáo dục & Học thuật", "B2"),
    ("label", "/ˈleɪbl/", "noun", "nhãn mác, tên định danh", "Read the medicine label carefully for dosing instructions.", "Đồ dùng trong nhà", "A2"),
    ("laboratory", "/ləˈbɒrətri/", "noun", "phòng thí nghiệm", "Scientists conducted research in the acoustic physics laboratory.", "Khoa học & Đổi mới", "A2"),
    ("ladder", "/ˈlædə(r)/", "noun", "cái thang trèo", "He climbed the wooden ladder to inspect the roof tiles.", "Đồ dùng trong nhà", "A2"),
    ("landscape", "/ˈlændskeɪp/", "noun", "phong cảnh thiên nhiên", "The scenic mountain landscape was shrouded in morning mist.", "Thiên nhiên & Cảnh sắc", "B1"),
    ("lane", "/leɪn/", "noun", "làn đường xe, ngõ nhỏ", "Follow the designated bicycle lane through the quiet park.", "Giao thông & Di chuyển", "A2"),
    ("lantern", "/ˈlæntən/", "noun", "đèn lồng thắp sáng", "Silk lanterns cast a warm golden glow across Hoi An canal.", "Thiên nhiên & Cảnh sắc", "A2"),
    ("laser", "/ˈleɪzə(r)/", "noun", "tia la-de", "Modern eye surgery employs high-precision surgical lasers.", "Khoa học & Đổi mới", "A2"),
    ("laundry", "/ˈlɔːndri/", "noun", "giặt giũ quần áo", "Fold clean, fragrant cotton shirts after completing the laundry.", "Nhà cửa & Tiện nghi đời sống", "A2"),
    ("lawsuit", "/ˈlɔːsuːt/", "noun", "vụ kiện tụng pháp lý", "The consumer union filed a public class-action lawsuit.", "Pháp luật & Xã hội", "B2"),
    ("layout", "/ˈleɪaʊt/", "noun", "bố cục giao diện", "The minimalist card layout keeps learners calm and focused.", "Giao diện & Trải nghiệm", "B2"),
    ("lease", "/liːs/", "noun", "hợp đồng thuê nhà", "Review all terms before signing the residential lease contract.", "Nhà cửa & Tiện nghi đời sống", "B2"),
    ("legacy", "/ˈleɡəsi/", "noun", "di sản để lại", "Bilingual fluency is an enduring educational legacy for life.", "Phát triển bản thân", "B2"),
    ("lemonade", "/ˌleməˈneɪd/", "noun", "nước chanh giải khát", "Sip cold iced lemonade on a hot sunny summer afternoon.", "Đồ uống & Tráng miệng", "A1"),
    ("liberty", "/ˈlɪbəti/", "noun", "sự tự do, quyền tự do", "Universal human liberty encompasses freedom of speech.", "Chính trị & Xã hội", "B2"),
    ("librarian", "/laɪˈbreəriən/", "noun", "thủ thư thư viện", "The helpful librarian recommended three bilingual fiction books.", "Giáo dục & Học thuật", "A2"),
    ("lifetime", "/ˈlaɪftaɪm/", "noun", "suốt cuộc đời, cả đời", "Mastering the Oxford 3000 is an investment for a lifetime.", "Phát triển bản thân", "B1"),
    ("lighthouse", "/ˈlaɪthaʊs/", "noun", "ngọn hải đăng bờ biển", "The historic stone lighthouse warned vessels of coastal reefs.", "Thiên nhiên & Cảnh sắc", "A2"),
    ("limb", "/lɪm/", "noun", "tay chân, cành cây lớn", "Gentle physical stretching keeps limbs agile and flexible.", "Cơ thể & Giác quan", "B2"),
    ("limitation", "/ˌlɪmɪˈteɪʃn/", "noun", "sự hạn chế, giới hạn", "Consistent daily study breaks through every mental limitation.", "Phát triển bản thân", "B1"),
    ("linguistic", "/lɪŋˈɡwɪstɪk/", "adj", "thuộc ngôn ngữ học", "Linguistic reflex allows speakers to converse without hesitation.", "Giáo dục & Học thuật", "B2"),
    ("liquidate", "/ˈlɪkwɪdeɪt/", "verb", "thanh lý tài sản, tất toán", "The company voted to liquidate surplus office equipment.", "Kinh tế & Đầu tư", "B2"),
    ("liquidity", "/lɪˈkwɪdəti/", "noun", "tính thanh khoản tài chính", "Financial liquidity ensures businesses handle sudden emergencies.", "Kinh tế & Đầu tư", "B2"),
    ("literacy", "/ˈlɪtərəsi/", "noun", "trình độ biết chữ", "Global digital literacy initiatives empower remote students.", "Giáo dục & Học thuật", "B2"),
    ("livestock", "/ˈlaɪvstɒk/", "noun", "vật nuôi gia súc trang trại", "Farmers provided fresh clean water to their pasture livestock.", "Động vật nuôi", "B2"),
    ("lodging", "/ˈlɒdʒɪŋ/", "noun", "chỗ ở tạm thời", "We secured comfortable lodging near the conference hall.", "Du lịch & Khám phá", "B1"),
    ("lottery", "/ˈlɒtəri/", "noun", "xổ số may mắn", "Language fluency is not a lottery; it is built on daily reps.", "Thái độ sống", "A2"),
    ("loyalty", "/ˈlɔɪəlti/", "noun", "lòng trung thành, tận tụy", "Customer loyalty reflects dependable, caring software service.", "Họp hành & Công sở", "B2"),
    ("luggage", "/ˈlʌɡɪdʒ/", "noun", "hành lý du lịch", "Fasten durable luggage tags to all your checked travel bags.", "Du lịch & Hành lý", "A2"),
    ("lumber", "/ˈlʌmbə(r)/", "noun", "gỗ xẻ xây dựng", "Carpenters stacked fragrant pine lumber in the workshop.", "Nhà cửa & Phòng ốc", "B2"),
    ("lyric", "/ˈlɪrɪk/", "noun", "lời bài hát thi vị", "Reading lyrical poetry attunes the ear to English rhythm.", "Âm nhạc & Nghệ thuật", "B1"),
    ("machinery", "/məˈʃiːnəri/", "noun", "máy móc thiết bị cơ khí", "Modern automated machinery manufactures precision microchips.", "Khoa học & Đổi mới", "B1"),
    ("madam", "/ˈmædəm/", "noun", "thưa quý bà, bà", "May I assist you with your baggage, madam?", "Giao tiếp lịch thiệp", "A1"),
    ("magazine", "/ˌmæɡəˈziːn/", "noun", "tạp chí định kỳ", "Read an English science magazine during your morning tea.", "Truyền thông & Đa phương tiện", "A1"),
    ("magic", "/ˈmædʒɪk/", "noun", "phép thuật màu nhiệm", "Speaking another language feels like wielding everyday magic.", "Tự tin giao tiếp & Thành quả", "A1"),
    ("magical", "/ˈmædʒɪkl/", "adj", "kỳ diệu, huyền diệu", "Sunset over the bay was a truly magical spectacle.", "Thiên nhiên & Cảnh sắc", "A2"),
]

final_list = get_final_batch()
target = 2850
added = 0
for item in needed_37:
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

out_file = os.path.join("scripts", "oxford_final_batch.py")
with open(out_file, "w", encoding="utf-8") as f:
    f.write("# scripts/oxford_final_batch.py\n")
    f.write("# Danh mục từ vựng bổ sung cuối cùng đạt chính xác 2.850 từ\n\n")
    f.write("def get_final_batch():\n")
    f.write(f"    return {json.dumps(final_list, ensure_ascii=False, indent=8)}\n")

print(f"Updated {out_file} to reach exact target!")

