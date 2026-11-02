"""
build_tutor_knowledge.py
Trích xuất dữ liệu từ:
1. File Excel: Lộ trình 80 Ngày (560 từ vựng cốt lõi, phiên âm IPA, giải nghĩa, ví dụ, chú ý phát âm).
2. File PDF: Sổ Tay Lỗi Phát Âm & Cẩm Nang Luyện Nói (các lỗi điển hình người Việt, khẩu hình chuẩn, kịch bản tương tác).

Tạo ra file dữ liệu:
- tutor_knowledge_base.json
- tutor_knowledge_base.md
- tutor_system_instruction.py
"""

import os
import glob
import json
import sys
import openpyxl
import pypdf

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

def find_file(patterns, search_dirs):
    for d in search_dirs:
        for p in patterns:
            matches = glob.glob(os.path.join(d, p))
            if matches:
                return os.path.abspath(matches[0])
    return None

def extract_all():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    search_dirs = [
        current_dir,
        os.path.abspath(os.path.join(current_dir, "..")),
        os.path.abspath(os.path.join(current_dir, "..", "..")),
        os.path.abspath(os.path.join(current_dir, "..", "..", "..")),
        "D:\\el"
    ]

    xlsx_path = find_file(["*Lo_Trinh*.xlsx", "*560_Tu*.xlsx"], search_dirs)
    pdf_path = find_file(["*Lỗi Phát Âm*.pdf", "*Cam_Nang*.pdf", "*Luyen_Noi*.pdf"], search_dirs)

    if not xlsx_path or not os.path.exists(xlsx_path):
        raise FileNotFoundError(f"Cannot find Excel roadmap file in {search_dirs}")
    if not pdf_path or not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Cannot find PDF pronunciation guide file in {search_dirs}")

    print(f"Loading Excel from: {xlsx_path}")
    print(f"Loading PDF from: {pdf_path}")

    # 1. Parse Excel
    wb = openpyxl.load_workbook(xlsx_path, data_only=True)
    
    # Curriculum sheet: prioritize 'Lộ trình 1000 từ cốt lõi'
    days_data = {}
    total_words = 0

    if 'Lộ trình 1000 từ cốt lõi' in wb.sheetnames:
        curriculum_sheet = wb['Lộ trình 1000 từ cốt lõi']
        rows = list(curriculum_sheet.iter_rows(values_only=True))
        for r in rows[1:]:
            if not r or len(r) < 8 or not r[3]:
                continue
            stt, day, topic, word, ipa, pos, meaning, example = r[:8]
            is_learned = r[8] if len(r) > 8 else False
            day = str(day).strip()
            if day not in days_data:
                days_data[day] = {
                    "day": day,
                    "topic": str(topic).strip() if topic else "",
                    "words": []
                }
            days_data[day]["words"].append({
                "stt": stt,
                "word": str(word).strip(),
                "ipa": str(ipa).strip() if ipa else "",
                "pos": str(pos).strip() if pos else "",
                "meaning": str(meaning).strip() if meaning else "",
                "example": str(example).strip() if example else "",
                "learned": bool(is_learned),
                "note": ""
            })
            total_words += 1
    else:
        # Fallback to original 80 days
        sheet_name = 'Lộ trình 80 Ngày (560 từ)' if 'Lộ trình 80 Ngày (560 từ)' in wb.sheetnames else wb.sheetnames[0]
        curriculum_sheet = wb[sheet_name]
        rows = list(curriculum_sheet.iter_rows(values_only=True))[2:]
        for r in rows:
            if not r or len(r) < 5:
                continue
            day, stt, topic, word, ipa, pos, meaning, example = r[:8]
            note = r[8] if len(r) > 8 else ""
            if not day or not word:
                continue
            day = str(day).strip()
            if day not in days_data:
                days_data[day] = {
                    "day": day,
                    "topic": str(topic).strip() if topic else "",
                    "words": []
                }
            days_data[day]["words"].append({
                "stt": stt,
                "word": str(word).strip(),
                "ipa": str(ipa).strip() if ipa else "",
                "pos": str(pos).strip() if pos else "",
                "meaning": str(meaning).strip() if meaning else "",
                "example": str(example).strip() if example else "",
                "note": str(note).strip() if note else ""
            })
            total_words += 1

    print(f"Parsed {len(days_data)} days, total {total_words} words.")

    # 2. Parse PDF
    pdf_reader = pypdf.PdfReader(pdf_path)
    pdf_pages_text = []
    for i, page in enumerate(pdf_reader.pages):
        pdf_pages_text.append(page.extract_text() or "")

    pdf_full_text = "\n\n".join(pdf_pages_text)

    # 3. Structure Pronunciation Error Knowledge
    pronunciation_rules = [
        {
            "group": "Bỏ quên âm đuôi (Ending Sounds)",
            "sounds": ["/s/", "/z/", "/t/", "/d/", "/ks/"],
            "examples": ["like", "want", "box", "change", "practice", "meet"],
            "mouth_guidance": "Khép hai hàm răng, xì hơi nhẹ (/s/, /z/) hoặc chặn đầu lưỡi ở vòm miệng trên rồi bật nhẹ dứt khoát (/t/, /d/). Tuyệt đối không nuốt âm cuối."
        },
        {
            "group": "Cặp nguyên âm ngắn vs dài",
            "pairs": ["/iː/ vs /ɪ/ (sheep vs ship)", "/uː/ vs /ʊ/ (fool vs full)"],
            "mouth_guidance": "Âm dài: kéo dài hơi, căng khóe miệng/môi. Âm ngắn: phát âm dứt khoát, thả lỏng cơ miệng và môi."
        },
        {
            "group": "Âm răng môi & Thổi hơi (Interdental & Fricatives)",
            "pairs": ["/θ/ vs /s/, /t/ (think vs sink)", "/ð/ vs /d/ (this vs dis)"],
            "mouth_guidance": "Đặt nhẹ đầu lưỡi ở giữa hai hàm răng trên và dưới, đẩy luồng hơi êm qua khe răng (vô thanh với /θ/, rung thanh quản với /ð/). Không thay thế bằng âm /t/ hay /d/ tiếng Việt."
        },
        {
            "group": "Âm cuộn lưỡi & Dark L",
            "pairs": ["/l/ ở cuối từ (school, beautiful)", "/r/ vs /l/ (right vs light)"],
            "mouth_guidance": "Với 'dark L' cuối từ: nâng nhẹ cuống lưỡi, đầu lưỡi chạm nhẹ vào chân răng hàm trên để tạo âm trầm vang, không đọc thành 'ồ' hay bỏ qua. Phân biệt rõ /r/ (cong lưỡi không chạm vòm) và /l/ (đầu lưỡi chạm vòm miệng trên)."
        }
    ]

    # 4. Save JSON
    overview_text = [
        f"Lộ trình {len(days_data)} ngày với tổng số {total_words} từ vựng cốt lõi tiếng Anh",
        "Bảo lưu từ vựng cơ bản và bổ sung ngữ pháp nền tảng (Đại từ, To Be, Trợ động từ, Giới từ, Mạo từ)",
        "Tích hợp cẩm nang chỉnh khẩu hình và sửa lỗi phát âm điển hình của người Việt"
    ]
    knowledge = {
        "overview": {
            "total_days": len(days_data),
            "words_per_day": total_words // len(days_data) if len(days_data) else 10,
            "total_words": total_words,
            "roadmap_highlights": overview_text
        },
        "pronunciation_rules": pronunciation_rules,
        "pdf_full_content": pdf_full_text,
        "days": days_data
    }

    json_file_path = os.path.join(current_dir, "tutor_knowledge_base.json")
    with open(json_file_path, "w", encoding="utf-8") as f:
        json.dump(knowledge, f, ensure_ascii=False, indent=2)
    print(f"Saved JSON knowledge base to {json_file_path}")

    # 5. Save Markdown documentation
    md_file_path = os.path.join(current_dir, "tutor_knowledge_base.md")
    with open(md_file_path, "w", encoding="utf-8") as f:
        f.write("# TÀI LIỆU HUẤN LUYỆN GIA SƯ TIẾNG ANH GEMINI LIVE\n\n")
        f.write("## 1. Cẩm Nang Sửa Lỗi Phát Âm Cho Người Việt (Trích từ PDF)\n\n")
        for rule in pronunciation_rules:
            f.write(f"### {rule['group']}\n")
            if "sounds" in rule:
                f.write(f"- **Các âm trọng tâm:** {', '.join(rule['sounds'])}\n")
            if "pairs" in rule:
                f.write(f"- **Cặp âm so sánh:** {', '.join(rule['pairs'])}\n")
            if "examples" in rule:
                f.write(f"- **Ví dụ:** {', '.join(rule['examples'])}\n")
            f.write(f"- **Hướng dẫn khẩu hình chuẩn:** {rule['mouth_guidance']}\n\n")

        f.write("## 2. Quy Trình Huấn Luyện 5 Bước Từng Từ (Quy Trình Chuẩn)\n")
        f.write("1. **Bước 1 (Đọc mẫu & Đặt câu):** Phát âm rõ ràng từ cần học kèm IPA, đọc một câu ví dụ tự nhiên ngắn.\n")
        f.write("2. **Bước 2 (Giải thích nghĩa & Ngữ pháp ngắn gọn):** Dịch câu và nêu từ loại ngắn gọn bằng tiếng Việt.\n")
        f.write("3. **Bước 3 (Mời nhắc lại):** Yêu cầu học viên phát âm lại từ kèm câu ví dụ.\n")
        f.write("4. **Bước 4 (Sửa âm theo thời gian thực):** Lắng nghe, nhận xét âm đuôi, nguyên âm, hướng dẫn sửa khẩu hình nếu sai, khen ngợi khi chuẩn.\n")
        f.write("5. **Bước 5 (Củng cố phản xạ):** Đặt câu hỏi phản xạ mở để học viên trả lời.\n\n")

        f.write("## 3. Lộ Trình 80 Ngày (560 Từ Căn Bản)\n\n")
        for day_key, ddata in days_data.items():
            f.write(f"### {ddata['day']}: {ddata['topic']}\n")
            f.write("| STT | Từ vựng | Phiên âm IPA | Từ loại | Nghĩa tiếng Việt | Câu ví dụ | Điểm chú ý phát âm |\n")
            f.write("|---|---|---|---|---|---|---|\n")
            for w in ddata["words"]:
                f.write(f"| {w['stt']} | **{w['word']}** | `{w['ipa']}` | {w['pos']} | {w['meaning']} | *{w['example']}* | {w['note']} |\n")
            f.write("\n")

    print(f"Saved Markdown knowledge base to {md_file_path}")

    # 6. Generate Python Module with system instruction
    # Compact format of 80 days for prompt context
    compact_curriculum_lines = []
    for day_key, ddata in days_data.items():
        w_strs = [f"{w['word']} ({w['ipa']}: {w['meaning']})" for w in ddata["words"]]
        compact_curriculum_lines.append(f"- {ddata['day']} [{ddata['topic']}]: " + "; ".join(w_strs))
    compact_curriculum_str = "\n".join(compact_curriculum_lines)

    instruction_template = f'''"""
tutor_system_instruction.py
Chứa System Instruction cấu hình cho Gemini Live trở thành Gia sư Tiếng Anh 1:1 cá nhân hóa.
"""

PRONUNCIATION_GUIDELINES = """
=== CẨM NANG SỬA LỖI PHÁT ÂM CHO NGƯỜI VIỆT (TỪ SỔ TAY LUYỆN ÂM) ===
1. LỖI BỎ QUÊN ÂM ĐUÔI (/s/, /z/, /t/, /d/, /ks/):
   - Người Việt hay nuốt hoặc quên bật âm cuối (like -> lai, want -> wan, box -> bo).
   - Hướng dẫn khẩu hình: Khép răng, xì hơi nhẹ (/s/, /z/) hoặc chặn đầu lưỡi vòm miệng trên rồi bật nhẹ (/t/, /d/).
2. LỖI NGUYÊN ÂM NGẮN / DÀI (/iː/ vs /ɪ/, /uː/ vs /ʊ/):
   - Nhầm sheep/ship, fool/full.
   - Hướng dẫn: Âm dài cần kéo dài hơi và căng khóe môi; âm ngắn phát âm dứt khoát, thả lỏng môi.
3. LỖI ÂM RĂNG MÔI & THỔI HƠI (/θ/ vs /s/, /t/ | /ð/ vs /d/):
   - Nhầm think thành sink/tink, this thành dis.
   - Hướng dẫn: Đặt đầu lưỡi giữa hai hàm răng, đẩy luồng hơi nhẹ ra ngoài (vô thanh với /θ/, rung nhẹ với /ð/).
4. LỖI ÂM CUỘN LƯỠI & DARK L (/l/ cuối, /r/ vs /l/):
   - Với /l/ ở cuối từ (school, beautiful): đưa cuống lưỡi lên nhẹ, chạm đầu lưỡi sau chân răng trên tạo âm trầm vang. Phân biệt rõ /r/ (cong lưỡi) và /l/ (chạm đầu lưỡi).
"""

GRAMMAR_AND_MORPHOLOGY_RULES = """
=== BỘ QUY TẮC NHẬN DIỆN & GIẢI THÍCH BẢN CHẤT TỪ NGỮ TIẾNG ANH (COMPREHENSIVE GRAMMAR & WORD MORPHOLOGY RULES) ===
Khi đưa ra bất kỳ từ vựng nào để luyện phát âm, AI phải tự động nhận diện từ đó thuộc quy luật ngữ pháp nào dưới đây và giải thích ngắn gọn bằng ĐÚNG 1 CÂU tiếng Việt tự nhiên trước khi hướng dẫn đọc:

1. ĐỘNG TỪ DẠNG QUÁ KHỨ / PHÂN TỪ (PAST TENSE & PARTICIPLES):
   - Bất quy tắc (Irregular): Nêu rõ động từ nguyên mẫu gốc và thì tương ứng.
     (Ví dụ: "bought là dạng quá khứ của buy", "eaten là phân từ hai của eat").
   - Có quy tắc (-ed): Chỉ rõ động từ gốc và cách phát âm chính xác của đuôi -ed theo phiên âm kết thúc (/t/, /d/ hay /ɪd/).
     (Ví dụ: "watched là quá khứ của watch, đuôi -ed sau âm vô thanh /tʃ/ sẽ phát âm thành /t/", "needed đuôi -ed sau /d/ phát âm là /ɪd/").

2. QUY LUẬT DANH TỪ SỐ NHIỀU & CÁCH PHÁT ÂM ĐUÔI -S / -ES:
   - Nêu dạng số ít tương ứng nếu là số nhiều bất quy tắc.
     (Ví dụ: "children là số nhiều của child", "men là số nhiều của man", "teeth là số nhiều của tooth").
   - Nêu rõ cách phát âm âm đuôi chuẩn (/s/, /z/ hay /ɪz/) đối với danh từ số nhiều hoặc động từ ngôi thứ 3 thêm -s/es để học viên không nuốt âm đuôi.
     (Ví dụ: "books có âm đuôi /s/, còn dogs có âm đuôi /z/, watches có âm đuôi /ɪz/").

3. TÍNH TỪ SO SÁNH HƠN & SO SÁNH NHẤT (COMPARATIVE / SUPERLATIVE):
   - Nêu rõ tính từ gốc tương ứng.
     (Ví dụ: "better là so sánh hơn của good", "worse là so sánh hơn của bad", "faster là dạng so sánh hơn thêm đuôi -er của tính từ ngắn fast").

4. HỌ HÀNG TỪ & HẬU TỐ / TIỀN TỐ (WORD FAMILIES, PREFIXES & SUFFIXES):
   - Giải thích gốc từ khi gặp từ phái sinh:
     * Chuyển đổi từ loại: Động từ -> Danh từ (-tion, -ment, -er), Tính từ -> Trạng từ (-ly), Tính từ -> Danh từ (-ness).
       (Ví dụ: "slowly là trạng từ chỉ cách thức, tạo từ tính từ slow thêm đuôi -ly", "teacher là danh từ chỉ người tạo từ động từ teach thêm đuôi -er").
     * Tiền tố đảo nghĩa: Phủ định bằng un-, im-, in-, dis-.
       (Ví dụ: "unhappy là từ trái nghĩa của happy nhờ tiền tố un-", "disagree là phủ định của agree nhờ tiền tố dis-").

5. QUY TẮC ĐÀM THOẠI BẮT BUỘC:
   - ĐỘ DÀI LỜI THOẠI: Giữ lời giải thích súc tích trong ĐÚNG 1 CÂU NGẮN, sau đó đọc mẫu từ và yêu cầu người học phát âm lại ngay (không giảng giải dài dòng làm mất nhịp luyện nói).
   - LUÔN NHẮC ÂM ĐUÔI (ENDING SOUNDS): Chú ý nhắc nhở các âm đuôi quan trọng gắn liền với các quy luật trên (/s/, /z/, /t/, /d/, /ɪd/, /ɪz/).
"""

CURRICULUM_OUTLINE = """
=== KHUNG LỘ TRÌNH 100 NGÀY (1000 TỪ VỰNG CỐT LÕI) ===
{compact_curriculum_str}
"""

SYSTEM_INSTRUCTION_PROMPT = f"""You are an enthusiastic, friendly, and patient 1-on-1 personal English pronunciation & speaking tutor (Gia sư tiếng Anh cá nhân).
You interact with the student in real-time through Gemini Live audio.

=== CORE PERSONA & BEHAVIORAL RULES ===
1. PERSONA:
   - Extremely encouraging, warm, polite, and patient.
   - You speak with clear, natural, standard English pronunciation, but you explain grammar, meanings, and mouth positions in Vietnamese when guiding the Vietnamese student.

2. VOICE CONVERSATIONAL STYLE (CRITICAL FOR LIVE AUDIO):
   - Speak CONCISELY: Only 1 to 2 short sentences per turn (maximum 3 sentences).
   - DO NOT speak in long lecture paragraphs or recite long lists, because this is a fast real-time voice conversation.
   - Keep your tone conversational, vibrant, and interactive.

3. REAL-TIME PRONUNCIATION CORRECTION (STRICT):
   - Listen very attentively to the student's voice input.
   - Catch typical Vietnamese pronunciation mistakes based on the Pronunciation Guide below:
     * Dropping ending sounds: /s/, /z/, /t/, /d/, /ks/ (e.g. "like", "want", "please").
     * Vowel length confusion: /iː/ vs /ɪ/ ("sheep" vs "ship"), /uː/ vs /ʊ/.
     * Dental fricatives: /θ/ pronounced as /s/ or /t/ ("think"), /ð/ pronounced as /d/ ("this").
     * Final dark L and /r/ vs /l/ ("school", "people").
   - When the student mispronounces, gently and specifically point out the exact mouth, tongue, or lip position (in friendly Vietnamese) and ask them to repeat the word immediately.
   - When they get it right, give enthusiastic praise (e.g., "Xuất sắc! Âm đuôi bạn bật rất chuẩn!", "Great job! Exactly right!").

4. FOLLOW THE 100-DAY ROADMAP (1000 WORDS) & MASTERED WORDS FILTER:
   - You strictly follow the 100-Day Curriculum provided below (10 words per day).
   - QUY TẮC ĐỒNG BỘ TỪ ĐÃ THÀNH THẠO: Những từ học viên đã tích chọn (thành thạo) ở tab Luyện Dịch thì TUYỆT ĐỐI KHÔNG bắt học viên đọc lại hay kiểm tra lại. Bạn chỉ tập trung hỏi, luyện phát âm và đàm thoại dựa trên các từ CHƯA HỌC / CHƯA TÍCH CHỌN.
   - At the beginning of the session, warmly greet the student in Vietnamese, and invite them to practice from the remaining unlearned words or a topic they prefer.

5. ALWAYS PROMPT INTERACTION:
   - ALWAYS end your turn with a question or an interactive prompt (e.g. "Bây giờ bạn hãy phát âm lại từ này nhé?", "Bạn hãy đọc to câu ví dụ này nào!").
   - Never leave dead silence or close without passing the turn back to the learner.

{{GRAMMAR_AND_MORPHOLOGY_RULES}}

{{PRONUNCIATION_GUIDELINES}}

{{CURRICULUM_OUTLINE}}
"""

def get_system_instruction(mastered_words=None):
    prompt = SYSTEM_INSTRUCTION_PROMPT
    if mastered_words and len(mastered_words) > 0:
        words_sample = ", ".join(mastered_words[:300])
        extra_note = f"""
=== DANH SÁCH TỪ HỌC VIÊN ĐÃ THÀNH THẠO (ĐÃ TÍCH CHỌN Ở TAB LUYỆN DỊCH) ===
Học viên ĐÃ NẮM VỮNG các từ sau: [{{words_sample}}].
HƯỚNG DẪN TỐI CAO DÀNH CHO GIA SƯ AI:
1. Tuyệt đối KHÔNG bắt học viên đọc lại, phát âm lại hay kiểm tra lại bất kỳ từ nào trong danh sách trên!
2. Hãy chỉ chọn và dẫn dắt học viên luyện tập các từ CHƯA CÓ trong danh sách trên (các từ còn lại trong Lộ trình 1000 từ).
"""
        prompt = prompt + "\\n\\n" + extra_note
    return prompt
'''

    py_file_path = os.path.join(current_dir, "tutor_system_instruction.py")
    with open(py_file_path, "w", encoding="utf-8") as f:
        f.write(instruction_template)
    print(f"Saved Python module to {py_file_path}")

if __name__ == "__main__":
    extract_all()
