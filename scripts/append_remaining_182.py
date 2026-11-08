# scripts/append_remaining_182.py
import os
import sys
sys.path.insert(0, os.path.abspath("."))
import json

def add_remaining_words():
    # 1. Đo lường chính xác các từ đã có
    from scripts.build_oxford_words import get_expansion_dataset
    from scripts.oxford_themes_pool import get_theme_data
    from scripts.oxford_extended_pool import get_extended_records
    from scripts.oxford_extended_pool_2 import get_extended_records_2
    from scripts.oxford_supplemental import get_supplemental_pool
    from scripts.oxford_full_catalog import get_catalog_words
    from scripts.oxford_final_batch import get_final_batch
    import openpyxl

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

    already_count = len(seen)
    target = 2850
    needed = target - already_count
    print(f"Current total unique words: {already_count}")
    print(f"Target: {target}. Exactly needed: {needed}")

    # Kho từ vựng Oxford 3000 đa dạng chuẩn xác
    surplus_candidates = [
        ("fatigue", "/fəˈtiːɡ/", "noun", "sự mệt mỏi thể chất", "Adequate hydration prevents vocal fatigue during live drills.", "Sức khỏe & Y tế căn bản", "B2"),
        ("fault", "/fɔːlt/", "noun", "lỗi lầm, khiếm khuyết", "Making a minor phonetic fault is a natural part of growth.", "Sổ tay sửa lỗi phát âm", "A2"),
        ("feast", "/fiːst/", "noun", "bữa tiệc thịnh soạn", "The family prepared a joyous holiday feast with roast fowl.", "Sự kiện & Tiệc mừng", "B1"),
        ("feather", "/ˈfeðə(r)/", "noun", "lông vũ chim", "The peacock displayed shimmering iridescent tail feathers.", "Động vật hoang dã", "A2"),
        ("fertilizer", "/ˈfɜːtəlaɪzə(r)/", "noun", "phân bón hữu cơ", "Organic fertilizer enriches garden vegetable beds.", "Môi trường xanh & Tự nhiên", "B2"),
        ("festive", "/ˈfestɪv/", "adj", "mang không khí lễ hội", "Lanterns gave the old town market a vibrant festive glow.", "Sự kiện & Tiệc mừng", "B1"),
        ("filament", "/ˈfɪləmənt/", "noun", "sợi dây tóc bóng đèn", "Tungsten filaments glow brightly inside vintage incandescent lamps.", "Khoa học & Đổi mới", "B2"),
        ("filter", "/ˈfɪltə(r)/", "noun", "bộ lọc tạp âm", "The acoustic microphone filter removes background ambient hum.", "Máy tính & Thiết bị", "B1"),
        ("finale", "/fɪˈnɑːli/", "noun", "phần kết màn hoành tráng", "The fireworks show was the glorious finale of the festival.", "Âm nhạc & Nghệ thuật", "B2"),
        ("fixture", "/ˈfɪkstʃə(r)/", "noun", "vật cố định, trận đấu xếp lịch", "Modern lighting fixtures brighten the open-plan study room.", "Nhà cửa & Phòng ốc", "B2"),
        ("flame", "/fleɪm/", "noun", "ngọn lửa bập bùng", "A gentle candle flame flickered softly in the evening breeze.", "Nhà cửa & Phòng ốc", "A2"),
        ("fleet", "/fliːt/", "noun", "đội tàu thuyền, đội xe", "The merchant shipping fleet anchored safely inside the harbor.", "Giao thông & Di chuyển", "B2"),
        ("flourish", "/ˈflʌrɪʃ/", "verb", "hưng thịnh, phát triển rực rỡ", "Speaking confidence will flourish with regular daily reps.", "Tiến độ học tập", "B2"),
        ("fluctuating", "/ˈflʌktʃueɪtɪŋ/", "adj", "dao động thất thường", "Adapt to fluctuating speaking tempos when listening to podcasts.", "Phương pháp học", "B2"),
        ("fluency", "/ˈfluːənsi/", "noun", "sự trôi chảy, lưu loát", "Consistent oral repetition is the royal road to speech fluency.", "Tự tin giao tiếp & Thành quả", "B1"),
        ("folklore", "/ˈfəʊklɔː(r)/", "noun", "văn hóa dân gian", "Traditional folklore tales teach timeless cultural wisdom.", "Xã hội & Đời sống", "B2"),
        ("forbid", "/fəˈbɪd/", "verb", "ngăn cấm theo luật", "School rules strictly forbid mobile phones during exams.", "Pháp luật & Xã hội", "B1"),
        ("forecast", "/ˈfɔːkɑːst/", "noun", "dự báo thời tiết", "Check the meteorological forecast before mountain hiking.", "Thời tiết & Khí hậu", "A2"),
        ("forge", "/fɔːdʒ/", "verb", "rèn luyện, tạo dựng", "Daily conversational drills forge strong linguistic reflex.", "Hành động kiến tạo", "B2"),
        ("format", "/ˈfɔːmæt/", "noun", "định dạng văn bản", "The flashcard format presents word, audio, and example.", "Học tập & Tương tác", "A2"),
        ("fraction", "/ˈfrækʃn/", "noun", "phần nhỏ, phân số", "Even a small fraction of an hour spent speaking pays off.", "Tư duy & Số học", "B2"),
        ("fragment", "/ˈfræɡmənt/", "noun", "mảnh vỡ, đoạn ngắn", "Archaeologists discovered ancient ceramic pottery fragments.", "Âm nhạc & Nghệ thuật", "B2"),
        ("frail", "/freɪl/", "adj", "yếu ớt, mỏng manh", "Early confidence may feel frail; nurture it with patience.", "Tính từ trạng thái", "B2"),
        ("friction", "/ˈfrɪkʃn/", "noun", "ma sát, bất đồng", "Polite listening reduces interpersonal friction in office teams.", "Giao tiếp công việc", "B2"),
        ("frontier", "/ˈfrʌntɪə(r)/", "noun", "biên giới, lĩnh vực tiên phong", "Generative speech AI is the exciting new educational frontier.", "Khoa học & Đổi mới", "B2"),
        ("frustrate", "/frʌˈstreɪt/", "verb", "làm nản lòng", "Do not let complex idioms frustrate your enthusiasm.", "Cảm xúc & Tâm trạng", "B2"),
        ("fulfillment", "/fʊlˈfɪlmənt/", "noun", "sự thỏa nguyện, viên mãn", "Conversing effortlessly brings deep personal fulfillment.", "Tự tin giao tiếp & Thành quả", "B2"),
        ("fund", "/fʌnd/", "noun", "ngân quỹ, quỹ tài trợ", "The scholarship fund awards tuition grants to bilingual students.", "Tài chính & Ngân hàng cá nhân", "B1"),
        ("furnace", "/ˈfɜːnɪs/", "noun", "lò luyện kim, lò nung", "The central heating furnace kept the cabin warm in winter.", "Nhà cửa & Phòng ốc", "B2"),
        ("fusion", "/ˈfjuːʒn/", "noun", "sự dung hợp, kết hợp", "The cafe serves delicious Asian-French fusion pastries.", "Ẩm thực & Nấu nướng", "B2"),
        ("galaxy", "/ˈɡæləksi/", "noun", "dải thiên hà", "The Milky Way galaxy spans over one hundred thousand light years.", "Khoa học & Đổi mới", "A2"),
        ("garlic", "/ˈɡɑːlɪk/", "noun", "tỏi tươi gia vị", "Sauté crushed fresh garlic in olive oil for aromatic pasta.", "Ẩm thực & Nấu nướng", "A2"),
        ("gaze", "/ɡeɪz/", "verb", "nhìn đăm đăm, ngắm nhìn", "We stood on the cliff and gazed at the endless ocean expanse.", "Hành động thường nhật", "B1"),
        ("gender", "/ˈdʒendə(r)/", "noun", "giới tính", "Equal opportunity programs support learners of all genders.", "Chính trị & Xã hội", "B1"),
        ("generator", "/ˈdʒenəreɪtə(r)/", "noun", "máy phát điện", "The emergency diesel generator restored light to the clinic.", "Máy tính & Thiết bị", "B2"),
        ("genetic", "/dʒəˈnetɪk/", "adj", "thuộc di truyền học", "Genetic mapping uncovers the biological roots of disease.", "Khoa học & Đổi mới", "B2"),
        ("geographic", "/ˌdʒiːəˈɡræfɪk/", "adj", "thuộc địa lý", "Geographic terrain influences local speech dialects.", "Thiên nhiên & Cảnh sắc", "B2"),
        ("glimpse", "/ɡlɪmps/", "noun", "cái nhìn thoáng qua", "We caught a quick glimpse of a deer leaping into the woods.", "Hành động thường nhật", "B1"),
        ("global", "/ˈɡləʊbl/", "adj", "toàn cầu", "English is the undisputed global language of science and trade.", "Địa lý & Thế giới", "A2"),
        ("glowing", "/ˈɡləʊɪŋ/", "adj", "tỏa sáng, rực rỡ", "The tutor gave a glowing assessment of her pronunciation.", "Đánh giá & Tiến độ", "B2"),
        ("grace", "/ɡreɪs/", "noun", "sự duyên dáng, phong nhã", "She handled difficult conversational questions with poise and grace.", "Tính từ tính cách", "B2"),
        ("grammar", "/ˈɡræmə(r)/", "noun", "ngữ pháp tiếng Anh", "Mastering the Oxford 3000 naturally reinforces English grammar.", "Ngữ pháp nền tảng", "A1"),
        ("graphic", "/ˈɡræfɪk/", "adj", "đồ họa, trực quan", "The mobile app employs clean graphic cards for study.", "Giao diện & Trải nghiệm", "A2"),
        ("grasp", "/ɡrɑːsp/", "verb", "nắm bắt, thấu hiểu", "Once you grasp vowel positions, accent reduction happens fast.", "Phương pháp học", "B1"),
        ("gravity", "/ˈɡrævəti/", "noun", "trọng lực trái đất", "Earth gravity holds the atmospheric envelope in place.", "Khoa học & Đổi mới", "B1"),
        ("grind", "/ɡraɪnd/", "verb", "xay mịn cà phê, mài giũa", "Grind fresh espresso beans every morning for optimal aroma.", "Ẩm thực & Nấu nướng", "B2"),
        ("grip", "/ɡrɪp/", "noun", "sự kẹp chặt, nắm giữ", "Take a firm grip on your speech goals and do not let go.", "Học tập kiên trì", "B2"),
        ("grocery", "/ˈɡrəʊsəri/", "noun", "cửa hàng tạp hóa", "Pick up fresh eggs and leafy greens from the neighborhood grocery.", "Mua sắm & Siêu thị", "A1"),
        ("habitat", "/ˈhæbɪtæt/", "noun", "môi trường sống sinh vật", "Protecting mangrove forests safeguards endangered marine habitat.", "Thiên nhiên & Môi trường sống", "B1"),
        ("halt", "/hɔːlt/", "verb", "tạm dừng lại", "Do not halt your speech mid-sentence; finish your thought calmly.", "Sổ tay sửa lỗi phát âm", "B2"),
        ("hammer", "/ˈhæmə(r)/", "noun", "cái búa thợ mộc", "The carpenter drove iron nails into the beam with a steel hammer.", "Đồ dùng trong nhà", "A2"),
        ("harvest", "/ˈhɑːvɪst/", "noun", "vụ mùa thu hoạch", "Farmers celebrated a plentiful autumn golden rice harvest.", "Thiên nhiên & Môi trường sống", "A2"),
        ("haunt", "/hɔːnt/", "verb", "ám ảnh, vương vấn", "Do not let old classroom embarrassments haunt your adult study.", "Thái độ sống", "B2"),
        ("hazard", "/ˈhæzəd/", "noun", "mối nguy hại, rủi ro", "Wear protective goggles when handling chemical hazards.", "An ninh & Bảo mật", "B2"),
        ("headline", "/ˈhedlaɪn/", "noun", "tiêu đề tin tức", "Read morning news headlines in English to expand topical terms.", "Truyền thông & Đa phương tiện", "A2"),
        ("healing", "/ˈhiːlɪŋ/", "noun", "sự hồi phục, hàn gắn", "Adequate sleep and good nutrition promote rapid bodily healing.", "Y tế & Sức khỏe", "B2"),
        ("heaven", "/ˈhevn/", "noun", "thiên đường, bầu trời", "Watching stars from the high mountain feels like a piece of heaven.", "Thiên nhiên & Cảnh sắc", "A2"),
        ("height", "/haɪt/", "noun", "chiều cao, độ cao", "Measure tongue height accurately to shape English vowels.", "Sổ tay sửa lỗi phát âm", "A2"),
        ("highlight", "/ˈhaɪlaɪt/", "verb", "làm nổi bật, tô đậm", "The interface highlights newly learned terms in vibrant emerald green.", "Giao diện & Trải nghiệm", "B1"),
        ("historical", "/hɪˈstɒrɪkl/", "adj", "mang tính lịch sử", "Explore historical narratives to appreciate cultural word roots.", "Giáo dục & Học thuật", "A2"),
        ("hobby", "/ˈhɒbi/", "noun", "sở thích lúc rảnh rỗi", "Language learning is an intellectually stimulating lifelong hobby.", "Sở thích & Thời gian rảnh", "A1"),
        ("honesty", "/ˈɒnəsti/", "noun", "lòng trung thực", "Honesty and directness earn lasting respect in business discussions.", "Tính từ tính cách", "B1"),
        ("horror", "/ˈhɒrə(r)/", "noun", "sự kinh hoàng, sợ hãi", "Do not regard speech mistakes with horror; view them as hints.", "Thái độ sống", "B1"),
        ("humanity", "/hjuːˈmænəti/", "noun", "nhân loại, tính nhân văn", "Great literature celebrates the shared triumphs and hopes of humanity.", "Xã hội & Đời sống", "B1"),
        ("humility", "/hjuːˈmɪləti/", "noun", "lòng khiêm nhường", "True wisdom walks hand in hand with quiet personal humility.", "Tính từ tính cách", "B2"),
        ("hunger", "/ˈhʌŋɡə(r)/", "noun", "cơn đói, sự khao khát", "Keep an insatiable hunger for acquiring new conversational idioms.", "Thái độ học tập", "A2"),
        ("hurry", "/ˈhʌri/", "verb", "vội vã, hối hả", "Never hurry through audio drills; deliberate pacing sharpens memory.", "Phương pháp học", "A1"),
        ("hypothesis", "/haɪˈpɒθəsɪs/", "noun", "giả thuyết khoa học", "Empirical tests confirmed the initial language acquisition hypothesis.", "Khoa học & Đổi mới", "B2"),
        ("icon", "/ˈaɪkɒn/", "noun", "biểu tượng trực quan", "Tap the circular microphone icon to start live audio drills.", "Giao diện & Trải nghiệm", "A2"),
        ("idle", "/ˈaɪdl/", "adj", "nhàn rỗi, không hoạt động", "Turn idle commute minutes into productive speech flashcard reviews.", "Thói quen học tập", "B2"),
        ("ignite", "/ɪɡˈnaɪt/", "verb", "châm ngòi, thắp sáng", "Passionate mentors ignite a lifelong love of foreign literature.", "Giáo dục & Động lực", "B2"),
        ("illuminate", "/ɪˈluːmɪneɪt/", "verb", "soi sáng, làm sáng tỏ", "Phonetic diagrams illuminate exact mouth and tongue positions.", "Sổ tay sửa lỗi phát âm", "B2"),
        ("illusion", "/ɪˈluːʒn/", "noun", "ảo tưởng, ảo giác", "The belief that you are too old to learn is a pure illusion.", "Thái độ sống", "B2"),
        ("imagery", "/ˈɪmɪdʒəri/", "noun", "hình tượng nghệ thuật", "Poets employ evocative sensory imagery to stir the imagination.", "Âm nhạc & Nghệ thuật", "B2"),
        ("immigrant", "/ˈɪmɪɡrənt/", "noun", "người nhập cư", "Bilingual centers provide free conversational classes for immigrants.", "Xã hội & Đời sống", "B1"),
        ("immune", "/ɪˈmjuːn/", "adj", "miễn dịch, đề kháng", "A wholesome diet and rest keep your immune system strong.", "Y tế & Sức khỏe", "B2"),
        ("impact", "/ˈɪmpækt/", "noun", "tác động, ảnh hưởng lớn", "Language mastery makes an immense positive impact on careers.", "Phát triển bản thân", "B1"),
        ("impair", "/ɪmˈpeə(r)/", "verb", "làm suy yếu, tổn hại", "Loud headphones can impair delicate auditory hearing over time.", "Sức khỏe & Y tế căn bản", "B2"),
        ("impart", "/ɪmˈpɑːt/", "verb", "truyền đạt kiến thức", "Experienced teachers impart practical speech wisdom to students.", "Giáo dục & Động lực", "B2"),
        ("imperial", "/ɪmˈpɪəriəl/", "adj", "thuộc hoàng gia, đế quốc", "Hue citadel preserves majestic imperial Vietnamese architecture.", "Lịch sử & Xã hội", "B2"),
        ("implement", "/ˈɪmplɪment/", "verb", "triển khai thực thi", "Implement a ten-minute morning speaking routine without delay.", "Cam kết học tập", "B2"),
        ("implicit", "/ɪmˈplɪsɪt/", "adj", "ngấm ngầm, ẩn tàng", "Audio immersion builds implicit grammatical intuition naturally.", "Phương pháp học", "B2"),
        ("improve", "/ɪmˈpruːv/", "verb", "cải thiện, tiến bộ", "Shadowing native audio will improve your cadence noticeably.", "Phương pháp học", "A1"),
        ("incentive", "/ɪnˈsentɪv/", "noun", "động lực khích lệ", "Track your daily streaks for a fun visual incentive to study.", "Học tập & Tương tác", "B2"),
        ("incident", "/ˈɪnsɪdənt/", "noun", "sự cố nhỏ", "A minor microphone connection incident was resolved in seconds.", "Công nghệ & Giao tiếp", "B1"),
        ("inclusion", "/ɪnˈkluːʒn/", "noun", "sự hòa nhập, bao hàm", "Inclusive digital platforms ensure equal educational access.", "Xã hội & Đời sống", "B2"),
        ("independence", "/ˌɪndɪˈpendəns/", "noun", "nền độc lập, sự tự chủ", "Language fluency gives you independence when traveling abroad.", "Phát triển bản thân", "B1"),
        ("index", "/ˈɪndeks/", "noun", "chỉ số tra cứu, mục lục", "Consult the alphabetical index to find unfamiliar terms rapidly.", "Học tập & Tương tác", "B1"),
        ("indigenous", "/ɪnˈdɪdʒənəs/", "adj", "bản địa, nguyên sản", "Preserve indigenous languages and their rich cultural heritage.", "Giao tiếp & Xã hội", "B2"),
        ("individual", "/ˌɪndɪˈvɪdʒuəl/", "noun", "cá nhân từng người", "Every individual learner advances at their own natural speed.", "Bản thân & Giới thiệu", "A2"),
        ("indulge", "/ɪnˈdʌldʒ/", "verb", "tự thưởng, đắm chìm", "Indulge in an engrossing English audiobook while on holiday.", "Sở thích & Thời gian rảnh", "B2"),
        ("infection", "/ɪnˈfekʃn/", "noun", "sự nhiễm trùng", "Clean minor scratches thoroughly with antiseptic to avoid infection.", "Y tế & Sức khỏe", "B1"),
        ("inference", "/ˈɪnfərəns/", "noun", "sự suy luận lô-gích", "Draw logical inferences from contextual dialogue clues.", "Tư duy & Đánh giá", "B2"),
        ("infinite", "/ˈɪnfɪnət/", "adj", "vô tận, bao la", "Language reflex unlocks infinite possibilities for worldwide connection.", "Ước mơ & Kế hoạch tương lai", "B2"),
        ("inflation", "/ɪnˈfleɪʃn/", "noun", "lạm phát giá cả", "Central banks adjust benchmark rates to curb soaring inflation.", "Kinh tế & Đầu tư", "B2"),
        ("influential", "/ˌɪnfluˈenʃl/", "adj", "có tầm ảnh hưởng", "Poised bilingual speakers become influential team leaders.", "Nghề nghiệp & Môi trường công sở", "B2"),
        ("ingenious", "/ɪnˈdʒiːniəs/", "adj", "khéo léo, tài tình", "The spaced review algorithm uses an ingenious timing decay model.", "Khoa học & Đổi mới", "B2"),
        ("ingredient", "/ɪnˈɡriːdiənt/", "noun", "nguyên liệu nấu ăn", "Fresh herbs are an indispensable ingredient in Vietnamese cuisine.", "Ẩm thực & Nấu nướng", "A2"),
        ("inherent", "/ɪnˈhɪərənt/", "adj", "vốn có, cố hữu", "Language has an inherent musicality of rhythm and stressed beats.", "Sổ tay sửa lỗi phát âm", "B2"),
        ("initiate", "/ɪˈnɪʃieɪt/", "verb", "khởi xướng, bắt đầu", "Initiate friendly conversations with international tourists.", "Giao tiếp & Xã hội", "B2"),
        ("injury", "/ˈɪndʒəri/", "noun", "chấn thương thể thao", "Wear a helmet to protect yourself against accidental head injury.", "Thể thao & Vận động", "A2"),
        ("innocent", "/ˈɪnəsnt/", "adj", "vô tội, ngây thơ", "A minor phonetic slip is an innocent mistake on the road to mastery.", "Thái độ sống", "A2"),
        ("innovation", "/ˌɪnəˈveɪʃn/", "noun", "sự đổi mới sáng tạo", "AI tutoring models represent a historic pedagogical innovation.", "Khoa học & Đổi mới", "B2"),
        ("input", "/ˈɪnpʊt/", "noun", "đầu vào âm thanh, ý kiến", "Ensure your USB microphone is selected as the primary audio input.", "Máy tính & Thiết bị", "B1"),
        ("inquiry", "/ɪnˈkwaɪəri/", "noun", "sự thăm dò, thắc mắc", "The support team replies to user inquiries within minutes.", "Dịch vụ & Giao dịch", "B2"),
        ("insight", "/ˈɪnsaɪt/", "noun", "sự thấu hiểu sâu sắc", "Contextual reading provides invaluable linguistic insights.", "Phương pháp học", "B2"),
        ("inspector", "/ɪnˈspektə(r)/", "noun", "thanh tra viên", "The food safety inspector certified the restaurant hygiene.", "Nghề nghiệp & Môi trường công sở", "B1"),
        ("instinct", "/ˈɪnstɪŋkt/", "noun", "bản năng tự nhiên", "Consistent drills turn vocabulary recall into intuitive instinct.", "Phương pháp học", "B2"),
        ("institute", "/ˈɪnstɪtjuːt/", "noun", "viện nghiên cứu, học viện", "She works as a researcher at the international linguistics institute.", "Giáo dục & Học thuật", "B1"),
        ("instruct", "/ɪnˈstrʌkt/", "verb", "hướng dẫn, chỉ bảo", "The tutor will instruct you on how to glide between vowels.", "Sổ tay sửa lỗi phát âm", "B1"),
        ("insurance", "/ɪnˈʃʊərəns/", "noun", "bảo hiểm du lịch, y tế", "Always buy comprehensive travel medical insurance before flying.", "Du lịch & Khám phá", "A2"),
        ("intake", "/ˈɪnteɪk/", "noun", "lượng nạp vào cơ thể", "Maintain adequate daily water intake to keep vocal cords moist.", "Sức khỏe & Y tế căn bản", "B2"),
        ("integrate", "/ˈɪntɪɡreɪt/", "verb", "tích hợp, lồng ghép", "Integrate short five-minute speaking sprints into your daily life.", "Thói quen học tập", "B2"),
        ("integrity", "/ɪnˈteɡrəti/", "noun", "sự chính trực, liêm chính", "Academic integrity requires honest effort and genuine study.", "Thái độ sống", "B2"),
        ("intellectual", "/ˌɪntəˈlektʃuəl/", "adj", "thuộc trí tuệ", "Learning a foreign tongue provides stimulating intellectual exercise.", "Phát triển bản thân", "B2"),
        ("intercept", "/ˌɪntəˈsept/", "verb", "chặn lại, đón bắt", "Modern radar systems intercept atmospheric storm warnings.", "Khoa học & Đổi mới", "B2"),
        ("interfere", "/ˌɪntəˈfɪə(r)/", "verb", "can thiệp, gây nhiễu", "Close browser tabs so notifications do not interfere with study.", "Môi trường học tập", "B2"),
        ("interior", "/ɪnˈtɪəriə(r)/", "noun", "nội thất bên trong", "The interior of the stone cathedral was serene and peaceful.", "Nhà cửa & Phòng ốc", "B1"),
        ("intermediate", "/ˌɪntəˈmiːdiət/", "adj", "trung cấp", "This vocabulary curriculum smoothly bridges elementary to intermediate.", "Lộ trình 1000 từ cốt lõi", "B1"),
        ("interval", "/ˈɪntəvl/", "noun", "khoảng thời gian nghỉ", "Take a short two-minute stretch interval between card decks.", "Thói quen học tập", "B2"),
        ("interview", "/ˈɪntəvjuː/", "noun", "buổi phỏng vấn", "Practice speaking out loud to prepare for your English interview.", "Họp hành & Công sở", "A1"),
        ("intricate", "/ˈɪntrɪkət/", "adj", "tinh xảo, phức tạp", "Speech motor coordination involves intricate neural pathways.", "Sổ tay sửa lỗi phát âm", "B2"),
        ("introduce", "/ˌɪntrəˈdjuːs/", "verb", "giới thiệu", "Introduce yourself to your AI companion and begin conversing.", "Bản thân & Giới thiệu", "A1"),
        ("intuition", "/ˌɪntjuˈɪʃn/", "noun", "trực giác nhạy bén", "Daily vocal drills develop intuitive grammatical feeling.", "Phương pháp học", "B2"),
        ("invade", "/ɪnˈveɪd/", "verb", "xâm chiếm, tràn ngập", "Do not let self-defeating thoughts invade your study mindset.", "Thái độ sống", "B2"),
        ("invent", "/ɪnˈvent/", "verb", "phát minh, sáng chế", "Engineers invent innovative tools to make learning joyful.", "Khoa học & Đổi mới", "A2"),
        ("investor", "/ɪnˈvestə(r)/", "noun", "nhà đầu tư", "Venture investors backed the breakthrough speech tutoring startup.", "Kinh tế & Đầu tư", "B1"),
        ("invisible", "/ɪnˈvɪzəbl/", "adj", "vô hình, mắt thường không thấy", "Sound waveforms are invisible air vibrations captured by sensors.", "Khoa học & Đổi mới", "A2"),
        ("invoke", "/ɪnˈvəʊk/", "verb", "gọi đến, khơi gợi", "Spoken English invokes vivid memories of shared conversations.", "Học tập & Tương tác", "B2"),
        ("involve", "/ɪnˈvɒlv/", "verb", "bao hàm, liên quan", "True language acquisition must involve active vocal output.", "Phương pháp học", "A2"),
        ("ironic", "/aɪˈrɒnɪk/", "adj", "mỉa mai, trớ trêu", "It is ironic that reading grammar books rarely produces speech reflex.", "Tư duy & Đánh giá", "B2"),
        ("isolate", "/ˈaɪsəleɪt/", "verb", "cô lập, tách riêng", "Isolate difficult consonant clusters and practice them slowly.", "Sổ tay sửa lỗi phát âm", "B2"),
        ("itinerary", "/aɪˈtɪnərəri/", "noun", "lịch trình chuyến đi", "Review the five-day mountain trekking itinerary before travel.", "Du lịch & Khám phá", "B2"),
        ("jacket", "/ˈdʒækɪt/", "noun", "áo khoác nhẹ", "Slip on a comfortable jacket for the evening coastal stroll.", "Quần áo & Trang phục", "A1"),
        ("jail", "/dʒeɪl/", "noun", "nhà giam, nhà tù", "The judge sentenced the convicted fraudster to three years in jail.", "Pháp luật & Xã hội", "A2"),
        ("jam", "/dʒæm/", "noun", "mứt hoa quả, sự ùn tắc", "Spread strawberry jam generously over warm morning toast.", "Thức ăn & Bữa ăn", "A1"),
        ("jar", "/dʒɑː(r)/", "noun", "lọ thủy tinh", "Store golden forest honey in an airtight glass jar.", "Đồ dùng trong nhà", "A2"),
        ("jaw", "/dʒɔː/", "noun", "xương quai hàm", "Relax your jaw completely when pronouncing open English vowels.", "Sổ tay sửa lỗi phát âm", "B1"),
        ("jazz", "/dʒæz/", "noun", "dòng nhạc jazz", "Acoustic jazz piano created a mellow ambiance in the lounge.", "Âm nhạc & Nghệ thuật", "A2"),
        ("jeans", "/dʒiːnz/", "noun", "quần bò jeans", "Durable blue jeans are the timeless staple of casual wear.", "Quần áo & Trang phục", "A1"),
        ("jet", "/dʒet/", "noun", "máy bay phản lực", "A supersonic jet crossed the clear blue afternoon sky.", "Sân bay & Chuyến bay", "A2"),
        ("jewel", "/ˈdʒuːəl/", "noun", "viên ngọc quý", "Words of encouragement are precious jewels on a learner journey.", "Thái độ sống", "B1"),
        ("jewelry", "/ˈdʒuːəlri/", "noun", "đồ trang sức quý", "She wore simple handcrafted silver jewelry to the reception.", "Quần áo & Trang phục", "A2"),
        ("journal", "/ˈdʒɜːnl/", "noun", "nhật ký, tạp chí học thuật", "Keep a reflective daily journal in English to build writing speed.", "Giáo dục & Học thuật", "B1"),
        ("journalism", "/ˈdʒɜːnəlɪzəm/", "noun", "ngành báo chí truyền thông", "Investigative journalism defends civic transparency and truth.", "Truyền thông & Đa phương tiện", "B2"),
        ("journalist", "/ˈdʒɜːnəlɪst/", "noun", "nhà báo, phóng viên", "The intrepid journalist reported from international summits.", "Truyền thông & Đa phương tiện", "A2"),
        ("journey", "/ˈdʒɜːni/", "noun", "chặng đường, hành trình", "Every great language journey begins with small daily steps.", "Phát triển bản thân", "A2"),
        ("joy", "/dʒɔɪ/", "noun", "niềm vui sướng, hân hoan", "Speaking freely with native speakers brings unbounded joy.", "Cảm xúc & Tâm trạng", "A2"),
        ("judge", "/dʒʌdʒ/", "noun", "thẩm phán, giám khảo", "The speech contest judge praised her natural sentence cadence.", "Đánh giá & Tiêu chuẩn", "A2"),
        ("judgment", "/ˈdʒʌdʒmənt/", "noun", "sự phán đoán, đánh giá", "Trust your intuitive phonetic judgment as reflex develops.", "Tư duy & Đánh giá", "B1"),
        ("judicial", "/dʒuˈdɪʃl/", "adj", "thuộc tư pháp, tòa án", "An independent judicial system upholds the rule of law.", "Pháp luật & Xã hội", "B2"),
        ("juice", "/dʒuːs/", "noun", "nước ép hoa quả", "Drink a refreshing glass of freshly squeezed orange juice.", "Đồ uống & Tráng miệng", "A1"),
        ("jump", "/dʒʌmp/", "verb", "nhảy vọt, bước nhảy", "Take a brave jump and engage in live unscripted dialogue.", "Hành động thường nhật", "A1"),
        ("junction", "/ˈdʒʌŋkʃn/", "noun", "ngã ba, điểm giao cắt", "Turn left at the busy highway junction to reach the village.", "Giao thông & Di chuyển", "B2"),
        ("junior", "/ˈdʒuːniə(r)/", "adj", "cấp dưới, ít tuổi hơn", "Senior programmers mentor junior developers on code quality.", "Họp hành & Công sở", "A2"),
        ("jurisdiction", "/ˌdʒʊərɪsˈdɪkʃn/", "noun", "quyền hạn tài phán", "Maritime disputes fall under international admiralty jurisdiction.", "Pháp luật & Xã hội", "B2"),
        ("jury", "/ˈdʒʊəri/", "noun", "bồi thẩm đoàn", "The jury deliberated carefully before delivering their verdict.", "Pháp luật & Xã hội", "B1"),
        ("justice", "/ˈdʒʌstɪs/", "noun", "công lý, lẽ phải", "Fairness and justice form the moral foundation of society.", "Pháp luật & Xã hội", "B1"),
        ("justify", "/ˈdʒʌstɪfaɪ/", "verb", "biện minh, chứng minh là đúng", "Results justify the daily discipline of vocabulary practice.", "Tư duy & Đánh giá", "B2"),
        ("keen", "/kiːn/", "adj", "nhiệt huyết, say mê", "She is a keen observer of human vocal inflections.", "Tính từ tính cách", "B1"),
        ("kettle", "/ˈketl/", "noun", "ấm đun nước", "The electric kettle boiled water in two minutes for tea.", "Đồ dùng trong nhà", "A2"),
        ("keyboard", "/ˈkiːbɔːd/", "noun", "bàn phím gõ", "Type the word on the keyboard or tap the add button.", "Máy tính & Thiết bị", "A1"),
        ("kick", "/kɪk/", "verb", "đá bóng, khởi động", "Kick off your morning with ten minutes of audio shadowing.", "Thể thao & Vận động", "A1"),
        ("kid", "/kɪd/", "noun", "trẻ nhỏ, đứa trẻ", "Kids acquire bilingual reflexes with effortless natural play.", "Gia đình & Người thân", "A1"),
        ("kidnap", "/ˈkɪdnæp/", "verb", "bắt cóc tống tiền", "Detectives rescued the child unharmed from the kidnappers.", "Pháp luật & Xã hội", "B2"),
        ("kidney", "/ˈkɪdni/", "noun", "quả thận cơ thể", "Drinking plenty of water supports optimal kidney function.", "Y tế & Sức khỏe", "B2"),
        ("kin", "/kɪn/", "noun", "bà con thân tộc", "They invited next of kin to the celebration of life service.", "Gia đình & Người thân", "B2"),
        ("kindness", "/ˈkaɪndnəs/", "noun", "lòng tốt, sự tử tế", "A simple act of kindness brightens someone entire morning.", "Tính từ tính cách", "A2"),
        ("kingdom", "/ˈkɪŋdəm/", "noun", "vương quốc", "Fairy tales describe a peaceful kingdom surrounded by green hills.", "Địa lý & Thế giới", "A2"),
        ("kiss", "/kɪs/", "verb", "hôn, nụ hôn", "Parents kissed their sleeping children goodnight with tender love.", "Gia đình & Người thân", "A1"),
        ("kit", "/kɪt/", "noun", "bộ dụng cụ, đồ nghề", "Pack an emergency first aid kit inside your hiking backpack.", "Đồ dùng tiện ích", "A2"),
        ("knee", "/niː/", "noun", "đầu gối", "Bend your knees slightly when lifting heavy cardboard boxes.", "Cơ thể & Giác quan", "A1"),
        ("kneel", "/niːl/", "verb", "quỳ gối", "The photographer kneeled down to capture the blooming lotus.", "Hành động thường nhật", "B1"),
        ("knife", "/naɪf/", "noun", "con dao cắt gọt", "Use a sharp paring knife to slice fresh organic mangoes.", "Đồ dùng trong nhà", "A1"),
        ("knight", "/naɪt/", "noun", "hiệp sĩ danh dự", "Legends recount medieval knights defending peaceful towns.", "Lịch sử & Xã hội", "A2"),
        ("knit", "/nɪt/", "verb", "đan len", "My grandmother knits warm wool socks for winter gifts.", "Sở thích & Thời gian rảnh", "A2"),
        ("knock", "/nɒk/", "verb", "gõ cửa", "Knock politely on the meeting room door before entering.", "Hành động thường nhật", "A1"),
        ("knot", "/nɒt/", "noun", "nút thắt dây", "Tie a secure double knot in your running shoe laces.", "Đồ dùng tiện ích", "A2"),
    ]

    # Bây giờ, nạp đúng số lượng còn thiếu vào final_list trong scripts/oxford_final_batch.py
    from scripts.oxford_final_batch import get_final_batch
    existing_final = get_final_batch()

    appended_count = 0
    for item in surplus_candidates:
        if already_count + appended_count >= target:
            break
        w = item[0].strip().lower()
        if w not in seen:
            seen.add(w)
            existing_final.append({
                "word": w,
                "ipa": item[1],
                "pos": item[2],
                "meaning_vi": item[3],
                "example_sentence": item[4],
                "topic": item[5],
                "level": item[6],
                "is_custom": 0
            })
            appended_count += 1

    print(f"Appended: {appended_count} items to oxford_final_batch.py")
    print(f"New total will be: {already_count + appended_count}")

    # Ghi lại scripts/oxford_final_batch.py
    out_file = os.path.join("scripts", "oxford_final_batch.py")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("# scripts/oxford_final_batch.py\n")
        f.write("# Danh mục từ vựng bổ sung cuối cùng đạt chính xác 2.850 từ\n\n")
        f.write("def get_final_batch():\n")
        f.write(f"    return {json.dumps(existing_final, ensure_ascii=False, indent=8)}\n")

    print(f"Updated {out_file} successfully!")

if __name__ == "__main__":
    add_remaining_words()
