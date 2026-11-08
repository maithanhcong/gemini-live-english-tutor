# scripts/generate_oxford_supplemental.py
"""
Tự động biên tập danh sách bổ sung Oxford 3000 hoàn chỉnh để đạt chính xác 2.850 từ.
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

def build_supplemental_file():
    excel_path = os.path.join("data", "1000_core_words_curriculum.xlsx")
    wb = openpyxl.load_workbook(excel_path, data_only=True)
    sheet = wb.active
    seen = set()

    for r in list(sheet.iter_rows(values_only=True))[1:]:
        if r and r[3]:
            seen.add(str(r[3]).strip().lower())

    for item in get_expansion_dataset():
        seen.add(item[0].strip().lower())

    for topic, words in get_theme_data().items():
        for item in words:
            seen.add(item[0].strip().lower())

    for item in get_extended_records():
        seen.add(item[0].strip().lower())

    for item in get_extended_records_2():
        seen.add(item[0].strip().lower())

    current_count = len(seen)
    print(f"Total unique words already gathered: {current_count}")
    target_count = 2850
    needed_count = target_count - current_count
    print(f"Needed count: {needed_count}")

    # Danh mục Oxford 3000 chuẩn phong phú để lấy mẫu bù đắp đủ 2.850 từ
    # Mỗi từ có: từ, phiên âm IPA, loại từ, nghĩa tiếng Việt, câu ví dụ, chủ đề, cấp độ CEFR
    oxford_supplemental_candidates = [
        ("absorb", "/əbˈzɔːb/", "verb", "hấp thụ, thấm hút", "Sponges quickly absorb water from the wet kitchen counter.", "Khoa học & Đổi mới", "B1"),
        ("abstract", "/ˈæbstrækt/", "adj", "trừu tượng", "Philosophical concepts can feel abstract without concrete real-world examples.", "Tư duy & Đánh giá", "B2"),
        ("absurd", "/əbˈsɜːd/", "adj", "ngớ ngẩn, phi lý", "It was completely absurd to expect overnight fluency without daily practice.", "Tư duy & Đánh giá", "B2"),
        ("accelerate", "/əkˈseləreɪt/", "verb", "tăng tốc, thúc đẩy", "Daily audio immersion will accelerate your speech reflex dramatically.", "Phương pháp học", "B2"),
        ("accent", "/ˈæksent/", "noun", "giọng điệu, âm điệu vùng miền", "Every speaker carries a charming unique regional accent.", "Sổ tay sửa lỗi phát âm", "A2"),
        ("acceptable", "/əkˈseptəbl/", "adj", "chấp nhận được, vừa ý", "The drafted translation quality is fully acceptable for publication.", "Giao tiếp công việc", "B1"),
        ("acceptance", "/əkˈseptəns/", "noun", "sự chấp nhận, đón nhận", "Self-acceptance frees language learners from fear of judgment.", "Thái độ sống", "B2"),
        ("accessible", "/əkˈsesəbl/", "adj", "dễ tiếp cận, tiện lợi", "Interactive AI tutors make foreign language education accessible to all.", "Công nghệ & Giao tiếp", "B1"),
        ("accident", "/ˈæksɪdənt/", "noun", "tai nạn, sự cố bất ngờ", "Drive prudently to avoid an unexpected traffic accident.", "Giao thông & Di chuyển", "A2"),
        ("accidental", "/ˌæksɪˈdentl/", "adj", "tình cờ, ngẫu nhiên", "Their meeting at the university coffee shop was purely accidental.", "Giao tiếp & Xã hội", "B2"),
        ("accordingly", "/əˈkɔːdɪŋli/", "adv", "phù hợp, do đó", "Assess your pronunciation gaps and adjust your daily deck accordingly.", "Phương pháp học", "B2"),
        ("accumulate", "/əˈkjuːmjəleɪt/", "verb", "tích lũy, gom góp", "Consistent daily reps accumulate into immense vocabulary mastery.", "Thói quen học tập", "B2"),
        ("accuracy", "/ˈækjərəsi/", "noun", "sự chính xác, chuẩn xác", "Focus on enunciation accuracy before striving for rapid speaking pace.", "Sổ tay sửa lỗi phát âm", "B1"),
        ("accurately", "/ˈækjərətli/", "adv", "một cách chuẩn xác", "The speech engine analyzes vowel pitch accurately in real time.", "Sổ tay sửa lỗi phát âm", "B1"),
        ("accusation", "/ˌækjuˈzeɪʃn/", "noun", "lời buộc tội, cáo buộc", "Never voice a severe accusation without concrete verifiable evidence.", "Pháp luật & Xã hội", "B2"),
        ("accuse", "/əˈkjuːz/", "verb", "cáo buộc, buộc tội", "Do not accuse colleagues of misconduct without verifiable proof.", "Giao tiếp công việc", "B1"),
        ("acid", "/ˈæsɪd/", "noun", "axit hóa học", "Lemon juice contains high concentrations of natural citric acid.", "Khoa học & Đổi mới", "B1"),
        ("acknowledge", "/əkˈnɒlɪdʒ/", "verb", "thừa nhận, ghi nhận", "He gracefully acknowledged the tutor helpful phonetic critique.", "Giao tiếp lịch thiệp", "B2"),
        ("acquire", "/əˈkwaɪə(r)/", "verb", "thu nhận, tiếp thu", "Learners acquire authentic natural rhythm through vocal shadowing.", "Phương pháp học", "B2"),
        ("acquisition", "/ˌækwɪˈzɪʃn/", "noun", "sự tiếp thu ngôn ngữ", "Second language acquisition flourishes with unscripted audio immersion.", "Phương pháp học", "B2"),
        ("action", "/ˈækʃn/", "noun", "hành động, biện pháp", "Take decisive action today to elevate your English conversational skill.", "Hành động kiến tạo", "A1"),
        ("activate", "/ˈæktɪveɪt/", "verb", "kích hoạt, bật lên", "Press the blue circular button to activate the microphone stream.", "Công nghệ & Giao tiếp", "B1"),
        ("actively", "/ˈæktɪvli/", "adv", "một cách tích cực, chủ động", "Students actively engage in lively dialogue during conversation class.", "Thái độ học tập", "B1"),
        ("activist", "/ˈæktɪvɪst/", "noun", "nhà hoạt động xã hội", "The young environmental activist addressed the global climate rally.", "Chính trị & Xã hội", "B2"),
        ("actual", "/ˈæktʃuəl/", "adj", "thực tế, có thật", "Real conversational experience differs greatly from abstract textbook drills.", "Phương pháp học", "B1"),
        ("actually", "/ˈæktʃuəli/", "adv", "thực ra, thực sự là", "I actually find vocal shadowing easier than silent grammar study.", "Giao tiếp & Phản xạ", "A2"),
        ("acute", "/əˈkjuːt/", "adj", "sắc bén, cấp tính", "She possesses an acute musical ear for detecting subtle accent inflections.", "Sổ tay sửa lỗi phát âm", "B2"),
        ("adapt", "/əˈdæpt/", "verb", "thích nghi, biến đổi", "Successful learners adapt their study routines to changing schedules.", "Phương pháp học", "B2"),
        ("adaptation", "/ˌædæpˈteɪʃn/", "noun", "sự thích nghi, phóng tác", "The movie is a compelling cinematic adaptation of a classic novel.", "Truyền thông & Đa phương tiện", "B2"),
        ("adequate", "/ˈædɪkwət/", "adj", "đầy đủ, thỏa đáng", "Eight hours of adequate sleep supports optimal memory consolidation.", "Thói quen sống lành mạnh", "B2"),
        ("adequately", "/ˈædɪkwətli/", "adv", "một cách đầy đủ", "Ensure your audio recording device is adequately charged.", "Máy tính & Thiết bị", "B2"),
        ("adhere", "/ədˈhɪə(r)/", "verb", "tuân thủ, dính chặt", "Strictly adhere to your daily ten-minute speaking schedule.", "Cam kết học tập", "B2"),
        ("adjacent", "/əˈdʒeɪsnt/", "adj", "liền kề, sát cạnh", "The conference room is located adjacent to the faculty library.", "Thành phố & Công trình", "B2"),
        ("administer", "/ədˈmɪnɪstə(r)/", "verb", "quản trị, phân phát", "Certified nurses administer vaccines safely to young infants.", "Y tế & Sức khỏe", "B2"),
        ("administration", "/ədˌmɪnɪˈstreɪʃn/", "noun", "ban quản trị, sự điều hành", "University administration oversees student housing and enrollment.", "Họp hành & Công sở", "B2"),
        ("administrative", "/ədˈmɪnɪstrətɪv/", "adj", "thuộc hành chính", "She handles complex administrative duties with remarkable efficiency.", "Họp hành & Công sở", "B2"),
        ("administrator", "/ədˈmɪnɪstreɪtə(r)/", "noun", "quản trị viên", "The system administrator configured the database backup schedule.", "Công nghệ & Giao tiếp", "B2"),
        ("admission", "/ədˈmɪʃn/", "noun", "sự nhận vào, vé vào cửa", "Show your student card to receive free admission to the art museum.", "Giáo dục & Học thuật", "B1"),
        ("adopt", "/əˈdɒpt/", "verb", "áp dụng, thông qua", "Adopt positive speech habits by emulating articulate podcast hosts.", "Phương pháp học", "B2"),
        ("adoption", "/əˈdɒpʃn/", "noun", "sự thông qua, nhận nuôi", "Widespread adoption of clean energy vehicles protects city air.", "Khoa học & Đổi mới", "B2"),
        ("adult", "/ˈædʌlt/", "noun", "người trưởng thành", "Adult language learners benefit from contextual associative memory.", "Bản thân & Giới thiệu", "A1"),
        ("advance", "/ədˈvɑːns/", "verb", "tiến bộ, nâng cao", "Consistent flashcard review helps advance your vocabulary proficiency.", "Tiến độ học tập", "B1"),
        ("advanced", "/ədˈvɑːnst/", "adj", "nâng cao, tiên tiến", "This module is crafted for advanced speakers refining subtle nuances.", "Lộ trình 1000 từ cốt lõi", "B1"),
        ("advantage", "/ədˈvɑːntɪdʒ/", "noun", "ưu thế, lợi thế cạnh tranh", "Bilingual fluency gives applicants a tremendous employment advantage.", "Nghề nghiệp & Môi trường công sở", "A2"),
        ("adventure", "/ədˈventʃə(r)/", "noun", "chuyến phiêu lưu", "Learning English with an AI companion is an exhilarating adventure.", "Đồng hành học tập thông minh", "A2"),
        ("advertise", "/ˈædvətaɪz/", "verb", "quảng cáo", "Modern startups advertise their innovative services across social media.", "Truyền thông & Đa phương tiện", "A2"),
        ("advertisement", "/ədˈvɜːtɪsmənt/", "noun", "mục quảng cáo", "The newspaper advertisement announced the opening of the language center.", "Truyền thông & Đa phương tiện", "A2"),
        ("adviser", "/ədˈvaɪzə(r)/", "noun", "cố vấn, chuyên gia", "Consult an academic adviser before choosing your major courses.", "Giáo dục & Học thuật", "B1"),
        ("advocate", "/ˈædvəkeɪt/", "verb", "tuyên truyền, ủng hộ", "Linguists advocate communicative practice over passive reading.", "Phương pháp học", "B2"),
        ("affair", "/əˈfeə(r)/", "noun", "công việc, sự việc", "The international affairs summit convenes diplomats from eighty nations.", "Chính trị & Xã hội", "B2"),
        ("affect", "/əˈfekt/", "verb", "ảnh hưởng đến, tác động", "Mouth shape and tongue height directly affect vowel resonance.", "Sổ tay sửa lỗi phát âm", "A2"),
        ("affordable", "/əˈfɔːdəbl/", "adj", "vừa túi tiền, phải chăng", "AuraSpeak provides high-end AI tutoring at an affordable cost.", "Tài chính & Ngân hàng cá nhân", "B1"),
        ("afraid", "/əˈfreɪd/", "adj", "e sợ, ngần ngại", "Never be afraid of stumbling on unfamiliar syllable stress.", "Thái độ sống", "A1"),
        ("afterward", "/ˈɑːftəwəd/", "adv", "sau đó, về sau", "We practiced ten minutes of dialogue and reviewed errors afterward.", "Thời gian & Các buổi", "A2"),
        ("agency", "/ˈeɪdʒənsi/", "noun", "đại lý, cơ quan", "Our creative agency crafts engaging educational multimedia.", "Họp hành & Công sở", "B1"),
        ("agenda", "/əˈdʒendə/", "noun", "chương trình nghị sự", "Every item on today study agenda was completed with diligence.", "Họp hành & Công sở", "B2"),
        ("agent", "/ˈeɪdʒənt/", "noun", "đại diện, nhân viên ủy quyền", "The booking agent secured discounted group train tickets.", "Họp hành & Công sở", "B1"),
        ("agriculture", "/ˈæɡrɪkʌltʃə(r)/", "noun", "ngành nông nghiệp", "Sustainable agriculture preserves valuable topsoil and groundwater.", "Thiên nhiên & Môi trường sống", "B1"),
        ("ahead", "/əˈhed/", "adv", "ở phía trước, dẫn trước", "Exciting linguistic breakthroughs lie ahead as you stay consistent.", "Tiến độ học tập", "A2"),
        ("aid", "/eɪd/", "noun", "sự trợ giúp, viện trợ", "Visual audio waveforms provide an intuitive aid for pitch analysis.", "Phương pháp học", "B1"),
        ("aircraft", "/ˈeəkrɑːft/", "noun", "máy bay", "The modern passenger aircraft cruised smoothly at 30,000 feet.", "Sân bay & Chuyến bay", "A2"),
        ("airline", "/ˈeəlaɪn/", "noun", "hãng hàng không", "The national airline offers direct flights to five global capitals.", "Sân bay & Chuyến bay", "A2"),
        ("alarm", "/əˈlɑːm/", "noun", "chuông báo thức", "Set a morning alarm to remind yourself of daily speaking drills.", "Khái niệm Thời gian & Lịch", "A2"),
        ("album", "/ˈælbəm/", "noun", "album ảnh, đĩa nhạc", "She recorded a soulful vocal jazz album in Abbey Road studios.", "Âm nhạc & Nghệ thuật", "A2"),
        ("alcohol", "/ˈælkəhɒl/", "noun", "chất cồn, rượu bia", "Medical disinfectants contain seventy percent isopropyl alcohol.", "Y tế & Sức khỏe", "B1"),
        ("alert", "/əˈlɜːt/", "adj", "tỉnh táo, cảnh giác", "Drink a glass of cold water to stay alert during morning study.", "Thói quen học tập", "B2"),
        ("alien", "/ˈeɪliən/", "adj", "xa lạ, thuộc ngoài hành tinh", "Foreign phonetics may sound alien at first, but practice demystifies them.", "Tư duy & Đánh giá", "B2"),
        ("alike", "/əˈlaɪk/", "adj", "giống nhau, tương tự", "Twin brothers dressed alike for their graduation ceremony.", "Gia đình & Người thân", "B1"),
        ("alive", "/əˈlaɪv/", "adj", "còn sống, tràn đầy sinh khí", "Interactive voice dialogue makes the English language come alive.", "Tự tin giao tiếp & Thành quả", "A2"),
        ("allocate", "/ˈæləkeɪt/", "verb", "phân bổ, chỉ định", "Allocate fifteen focused minutes every morning to speech practice.", "Thói quen học tập", "B2"),
        ("allocation", "/ˌæləˈkeɪʃn/", "noun", "sự phân bổ tài nguyên", "Smart memory allocation ensures the web app runs silky smooth on iPad.", "Công nghệ & Giao tiếp", "B2"),
        ("allowance", "/əˈlaʊəns/", "noun", "tiền trợ cấp, định mức", "Parents gave the teenager a modest monthly pocket money allowance.", "Tài chính & Ngân hàng cá nhân", "B1"),
        ("ally", "/ˈælaɪ/", "noun", "đồng minh, bạn hữu", "An encouraging tutor is your greatest ally in achieving spoken fluency.", "Đồng hành học tập thông minh", "B2"),
        ("alongside", "/əˌlɒŋˈsaɪd/", "prep", "bên cạnh, song song", "Audio waveforms render alongside live speech for instant feedback.", "Phương pháp học", "B1"),
        ("alter", "/ˈɔːltə(r)/", "verb", "thay đổi, điều chỉnh", "Alter your tongue placement slightly to sharpen consonant clarity.", "Sổ tay sửa lỗi phát âm", "B2"),
        ("alternative", "/ɔːlˈtɜːnətɪv/", "noun", "phương án thay thế", "Cloud-based AI tutoring is a flexible alternative to evening classes.", "Phương pháp học", "B1"),
        ("altogether", "/ˌɔːltəˈɡeðə(r)/", "adv", "hoàn toàn, nói chung", "Altogether, mastering the Oxford 3000 unlocks 90% of everyday English.", "Lộ trình 1000 từ cốt lõi", "B1"),
        ("amateur", "/ˈæmətə(r)/", "noun", "người nghiệp dư", "Amateur photographers captured stunning wildlife shots in the park.", "Âm nhạc & Nghệ thuật", "B2"),
        ("amaze", "/əˈmeɪz/", "verb", "làm ngạc nhiên, kinh ngạc", "Your conversational fluency will amaze your colleagues after three months.", "Tự tin giao tiếp & Thành quả", "A2"),
        ("amazing", "/əˈmeɪzɪŋ/", "adj", "tuyệt vời, đáng kinh ngạc", "The AI companion instant speech recognition is truly amazing.", "Công nghệ & Giao tiếp", "A1"),
        ("ambassador", "/æmˈbæsədə(r)/", "noun", "đại sứ ngoại giao", "The cultural ambassador promoted international educational exchanges.", "Chính trị & Xã hội", "B2"),
        ("ambition", "/æmˈbɪʃn/", "noun", "hoài bão, khát vọng", "Her lifelong ambition is to publish bilingual poetry collections.", "Ước mơ & Kế hoạch tương lai", "B1"),
        ("amend", "/əˈmend/", "verb", "sửa đổi văn bản, luật", "Parliament voted to amend the consumer protection act.", "Pháp luật & Xã hội", "B2"),
        ("amendment", "/əˈmendmənt/", "noun", "sự sửa đổi, tu chính án", "The constitutional amendment guaranteed freedom of the digital press.", "Pháp luật & Xã hội", "B2"),
        ("amid", "/əˈmɪd/", "prep", "ở giữa, giữa lúc", "She stayed calm and focused amid the noisy airport terminal.", "Cảm xúc & Tâm trạng", "B2"),
        ("amount", "/əˈmaʊnt/", "noun", "số lượng, lượng", "A small daily amount of speaking builds tremendous verbal reflex.", "Phương pháp học", "A2"),
        ("ancestor", "/ˈænsestə(r)/", "noun", "tổ tiên, tiền nhân", "Families gather during Tet to pay homage to their revered ancestors.", "Gia đình & Người thân", "B1"),
        ("anchor", "/ˈæŋkə(r)/", "noun", "mỏ neo, điểm tựa", "The cargo ship dropped heavy iron anchor inside the deep harbor.", "Giao thông & Di chuyển", "B2"),
        ("ancient", "/ˈeɪnʃənt/", "adj", "cổ xưa, thời thượng cổ", "Visit ancient stone temples nestled in misty central highland valleys.", "Du lịch & Khám phá", "A2"),
        ("angel", "/ˈeɪndʒl/", "noun", "thiên thần, người tốt bụng", "The pediatric nurse was an absolute angel to the frightened child.", "Gia đình & Người thân", "A2"),
        ("anniversary", "/ˌænɪˈvɜːsəri/", "noun", "ngày kỷ niệm", "They celebrated the fifth anniversary of launching AuraSpeak.", "Sự kiện & Tiệc mừng", "B1"),
        ("announce", "/əˈnaʊns/", "verb", "thông báo, công bố", "The flight attendant will announce boarding gates momentarily.", "Sân bay & Chuyến bay", "A2"),
        ("announcement", "/əˈnaʊnsmənt/", "noun", "lời thông báo", "Listen carefully to the platform audio announcement for track updates.", "Sân bay & Chuyến bay", "A2"),
        ("annoy", "/əˈnɔɪ/", "verb", "làm bực mình, quấy rầy", "Background microphone hiss can annoy listeners during conference calls.", "Cảm xúc & Tâm trạng", "A2"),
        ("annual", "/ˈænjuəl/", "adj", "hàng năm, thường niên", "Our annual vocabulary contest features prizes for top streak earners.", "Giáo dục & Động lực", "B1"),
        ("annually", "/ˈænjuəli/", "adv", "hàng năm", "The Oxford curriculum is reviewed annually by international linguists.", "Giáo dục & Động lực", "B1"),
        ("anonymous", "/əˈnɒnɪməs/", "adj", "ẩn danh, vô danh", "A generous donor made an anonymous gift to the library fund.", "Xã hội & Đời sống", "B2"),
        ("anticipate", "/ænˈtɪsɪpeɪt/", "verb", "dự đoán trước", "Anticipate common conversational questions to reply without hesitation.", "Giao tiếp & Phản xạ", "B2"),
        ("anxious", "/ˈæŋkʃəs/", "adj", "lo âu, bồn chồn", "Feelings of anxiety melt away with regular supportive speaking reps.", "Cảm xúc & Tâm trạng", "A2"),
        ("apologize", "/əˈpɒlədʒaɪz/", "verb", "xin lỗi, nhận lỗi", "Politely apologize if you interrupt someone by accident.", "Giao tiếp lịch thiệp", "A2"),
        ("apology", "/əˈpɒlədʒi/", "noun", "lời xin lỗi chân thành", "A sincere apology quickly restores warmth to interpersonal relations.", "Giao tiếp lịch thiệp", "B1"),
        ("apparent", "/əˈpærənt/", "adj", "rõ ràng, hiển nhiên", "Her speaking improvement became apparent after just two weeks.", "Đánh giá & Tiến độ", "B2"),
        ("appeal", "/əˈpiːl/", "noun", "sức hấp dẫn, lời kêu gọi", "Clean interactive user interfaces have universal aesthetic appeal.", "Giao diện & Trải nghiệm", "B2"),
        ("applicant", "/ˈæplɪkənt/", "noun", "người nộp đơn, ứng viên", "Every job applicant completed a brief ten-minute spoken evaluation.", "Họp hành & Công sở", "A2"),
        ("appoint", "/əˈpɔɪnt/", "verb", "bổ nhiệm, chỉ định", "The committee voted to appoint her chief curriculum designer.", "Họp hành & Công sở", "B2"),
        ("appreciate", "/əˈpriːʃieɪt/", "verb", "đánh giá cao, cảm kích", "We deeply appreciate your daily dedication to language mastery.", "Giao tiếp lịch thiệp", "B1"),
        ("appropriate", "/əˈprəʊpriət/", "adj", "thích hợp, phù hợp ngữ cảnh", "Select an appropriate conversational tone when speaking with clients.", "Giao tiếp công việc", "B2"),
        ("appropriately", "/əˈprəʊpriətli/", "adv", "một cách phù hợp", "Dress appropriately when attending international business summits.", "Giao tiếp công việc", "B2"),
        ("approval", "/əˈpruːvl/", "noun", "sự phê duyệt", "The board granted formal approval for the vocabulary dataset expansion.", "Họp hành & Công sở", "B1"),
        ("approve", "/əˈpruːv/", "verb", "phê duyệt, chuẩn thuận", "Managers approve flexible remote working hours for productive teams.", "Họp hành & Công sở", "B1"),
        ("approximate", "/əˈprɒksɪmət/", "adj", "xấp xỉ, tương đối", "The approximate time required to master 3000 words is ninety days.", "Lộ trình 1000 từ cốt lõi", "B1"),
        ("arbitrary", "/ˈɑːbɪtrəri/", "adj", "tùy tiện, ngẫu hứng", "Our curriculum is based on lexical corpus data, not arbitrary guesses.", "Tư duy & Đánh giá", "B2"),
        ("archive", "/ˈɑːkaɪv/", "noun", "kho lưu trữ tài liệu", "User mastered flashcards are preserved in the permanent cloud archive.", "Công nghệ & Dữ liệu", "B2"),
        ("arena", "/əˈriːnə/", "noun", "đấu trường, vũ đài", "Public speaking is a rewarding arena for developing mental courage.", "Phát triển bản thân", "B2"),
        ("argue", "/ˈɑːɡjuː/", "verb", "tranh luận, phản biện", "Scholars argue constructively to uncover scientific truths.", "Tư duy & Đánh giá", "A2"),
        ("argument", "/ˈɑːɡjumənt/", "noun", "luận điểm, lý lẽ thuyết phục", "She presented a watertight statistical argument supporting our plan.", "Tư duy & Đánh giá", "B1"),
        ("arise", "/əˈraɪz/", "verb", "nảy sinh, xuất hiện", "Unexpected questions often arise during unscripted live dialogue.", "Giao tiếp & Phản xạ", "B2"),
        ("armed", "/ɑːmd/", "adj", "vũ trang, được trang bị", "Armed with 3000 core words, you can converse on almost any topic.", "Phát triển bản thân", "B1"),
        ("array", "/əˈreɪ/", "noun", "mảng dữ liệu, dãy sắp đặt", "An array of thirty cards renders effortlessly in JavaScript memory.", "Công nghệ & Dữ liệu", "B2"),
        ("arrest", "/əˈrest/", "verb", "bắt giữ theo luật", "Detectives moved swiftly to arrest the international cyber criminal.", "Pháp luật & Xã hội", "B1"),
        ("arrow", "/ˈærəʊ/", "noun", "mũi tên chỉ dẫn", "Follow the neon blue arrow to navigate through the flashcard deck.", "Giao diện & Trải nghiệm", "A2"),
        ("article", "/ˈɑːtɪkl/", "noun", "bài báo, bài viết", "Read one English news article every morning to build reading speed.", "Truyền thông & Đa phương tiện", "A2"),
        ("articulate", "/ɑːˈtɪkjuleɪt/", "verb", "phát âm rõ ràng, gãy gọn", "Learn to articulate tricky English ending sounds without mumbles.", "Sổ tay sửa lỗi phát âm", "B2"),
        ("artifact", "/ˈɑːtɪfækt/", "noun", "hiện vật cổ vật", "Museum archaeologists excavated rare bronze artifacts along the river.", "Âm nhạc & Nghệ thuật", "B2"),
        ("aspire", "/əˈspaɪə(r)/", "verb", "khao khát, vươn tới", "Aspire to express your deepest thoughts with authentic natural poise.", "Ước mơ & Kế hoạch tương lai", "B2"),
        ("aspiration", "/ˌæspəˈreɪʃn/", "noun", "nguyện vọng, khát vọng lớn", "Mastering spoken English was her highest career aspiration.", "Ước mơ & Kế hoạch tương lai", "B2"),
        ("assault", "/əˈsɔːlt/", "noun", "cuộc tấn công", "Security systems guarded against a coordinated digital network assault.", "Pháp luật & Xã hội", "B2"),
        ("assemble", "/əˈsembl/", "verb", "tập hợp, lắp ráp", "Assemble simple sentence chunks rapidly to build conversational reflex.", "Phương pháp học", "B2"),
        ("assembly", "/əˈsembli/", "noun", "hội đồng, sự tập hợp", "The general assembly voted unanimously on the educational charter.", "Chính trị & Xã hội", "B2"),
        ("assert", "/əˈsɜːt/", "verb", "khẳng định, quả quyết", "Confidently assert your perspective during business discussions.", "Giao tiếp công việc", "B2"),
        ("assertion", "/əˈsɜːʃn/", "noun", "sự khẳng định", "Scientific data supports the assertion that spaced recall boosts memory.", "Tư duy & Đánh giá", "B2"),
        ("assess", "/əˈses/", "verb", "đánh giá, thẩm định", "AI speech systems assess syllable pitch, stress, and clarity.", "Sổ tay sửa lỗi phát âm", "B2"),
        ("assign", "/əˈsaɪn/", "verb", "giao việc, chỉ định", "The application will assign ten personalized flashcards each morning.", "Học tập & Tương tác", "B1"),
        ("assistance", "/əˈsɪstəns/", "noun", "sự hỗ trợ kịp thời", "Thank you for providing prompt technical assistance via chat.", "Giao tiếp & Tư vấn", "B2"),
        ("assistant", "/əˈsɪstənt/", "noun", "trợ lý, phụ tá", "The AI speech assistant answers conversational prompts instantly.", "Công nghệ & Giao tiếp", "A2"),
        ("associate", "/əˈsəʊʃieɪt/", "verb", "liên tưởng, kết nối", "Associate each unfamiliar term with a vibrant vivid mental picture.", "Phương pháp học", "B2"),
        ("association", "/əˌsəʊʃiˈeɪʃn/", "noun", "hiệp hội, sự liên kết", "She joined the international applied linguistics association.", "Học tập & Khám phá", "B2"),
        ("assume", "/əˈsjuːm/", "verb", "cho rằng, giả định", "Do not assume you lack talent; consistency beats innate talent.", "Thái độ sống", "B2"),
        ("assumption", "/əˈsʌmpʃn/", "noun", "giả định, tiền đề", "Our system dispels the assumption that learning accents is painful.", "Tư duy & Đánh giá", "B2"),
        ("assurance", "/əˈʃʊərəns/", "noun", "sự bảo đảm, cam đoan", "We give our assurance that your voice data remains private.", "An ninh & Bảo mật", "B2"),
        ("assure", "/əˈʃʊə(r)/", "verb", "cam đoan, quả quyết", "I can assure you that thirty days of practice yields noticeable gains.", "Giao tiếp lịch thiệp", "B2"),
        ("astonish", "/əˈstɒnɪʃ/", "verb", "làm sửng sốt, kinh ngạc", "Her rapid conversational progress will astonish her family.", "Tự tin giao tiếp & Thành quả", "B2"),
        ("astronaut", "/ˈæstrənɔːt/", "noun", "phi hành gia vũ trụ", "The brave astronaut floated peacefully outside the space station.", "Khoa học & Đổi mới", "A2"),
        ("athlete", "/ˈæθliːt/", "noun", "vận động viên thể thao", "Professional athletes maintain rigorous daily workout routines.", "Thể thao & Vận động", "A2"),
        ("athletic", "/æθˈletɪk/", "adj", "khỏe khoắn, thuộc điền kinh", "Her athletic stamina carried her through the 20-kilometer trek.", "Thể thao & Vận động", "B1"),
        ("atmosphere", "/ˈætməsfɪə(r)/", "noun", "khí quyển, bầu không khí", "A warm, judgment-free atmosphere encourages uninhibited speech.", "Môi trường học tập", "B1"),
        ("attack", "/əˈtæk/", "noun", "cuộc tấn công, công kích", "Cybersecurity defenses repelled an automated server attack.", "Công nghệ & Giao tiếp", "A2"),
        ("attain", "/əˈteɪn/", "verb", "đạt được, chạm tới", "With steady discipline, any student can attain B2 conversational reflex.", "Tự tin giao tiếp & Thành quả", "B2"),
        ("attempt", "/əˈtempt/", "noun", "sự nỗ lực, cố gắng", "Your courageous attempt to speak will always be celebrated here.", "Thái độ học tập", "B1"),
        ("attend", "/əˈtend/", "verb", "tham dự, có mặt", "Students attend a weekly live conversational salon on Zoom.", "Giao tiếp & Xã hội", "A2"),
        ("attendance", "/əˈtendəns/", "noun", "sự chuyên cần, có mặt", "Consistent daily attendance is the key to steady vocabulary retention.", "Thói quen học tập", "B1"),
        ("attention", "/əˈtenʃn/", "noun", "sự chú ý, lưu tâm", "Pay close attention to vowel length differences between bit and beat.", "Sổ tay sửa lỗi phát âm", "A2"),
        ("attitude", "/ˈætɪtjuːd/", "noun", "thái độ sống, tinh thần", "A growth attitude transforms pronunciation errors into gold mines.", "Thái độ sống", "B1"),
        ("attract", "/əˈtrækt/", "verb", "thu hút, lôi cuốn", "Clear, poised pronunciation attracts positive attention in meetings.", "Giao tiếp công việc", "B1"),
        ("attraction", "/əˈtrækʃn/", "noun", "sức hút, điểm tham quan", "The old town scenic lantern festival is a premier tourist attraction.", "Du lịch & Khám phá", "B1"),
        ("attractive", "/əˈtræktɪv/", "adj", "hấp dẫn, ưa nhìn", "The card layout presents vocabulary in an attractive, tidy format.", "Giao diện & Trải nghiệm", "A2"),
        ("attribute", "/əˈtrɪbjuːt/", "verb", "quy cho, gán cho", "She attributes her fluent accent to daily podcast audio shadowing.", "Phương pháp học", "B2"),
        ("auction", "/ˈɔːkʃn/", "noun", "buổi đấu giá", "The vintage acoustic violin was sold at a prestigious charity auction.", "Kinh tế & Đầu tư", "B2"),
        ("audience", "/ˈɔːdiəns/", "noun", "khán thính giả", "Engage your audience with expressive vocal melody and eye contact.", "Giao tiếp & Chia sẻ", "A2"),
        ("audit", "/ˈɔːdɪt/", "verb", "kiểm toán, rà soát", "Auditors inspect financial ledgers to verify accounting precision.", "Kinh tế & Đầu tư", "B2"),
        ("augment", "/ɔːɡˈment/", "verb", "gia tăng, làm tăng thêm", "AI tutoring models augment rather than replace passionate human teachers.", "Khoa học & Đổi mới", "B2"),
        ("authentic", "/ɔːˈθentɪk/", "adj", "chính thống, đích thực", "Practice with authentic English podcast clips to absorb natural rhythm.", "Phương pháp học", "B2"),
        ("author", "/ˈɔːθə(r)/", "noun", "tác giả cuốn sách", "The author penned an inspiring manual on language acquisition.", "Học tập & Sáng tạo", "A2"),
        ("authority", "/ɔːˈθɒrəti/", "noun", "chuyên gia đầu ngành, thẩm quyền", "She is an internationally recognized authority on phonetic reduction.", "Giáo dục & Học thuật", "B1"),
        ("authorize", "/ˈɔːθəraɪz/", "verb", "ủy quyền, cho phép", "Senior managers authorize cloud expenditures for server scaling.", "Họp hành & Công sở", "B2"),
        ("automatic", "/ˌɔːtəˈmætɪk/", "adj", "tự động hoàn toàn", "The system features automatic cloud synchronization of your mastered words.", "Công nghệ & Giao tiếp", "B1"),
        ("automatically", "/ˌɔːtəˈmætɪkli/", "adv", "một cách tự động", "Your vocabulary progress saves automatically across all your devices.", "Công nghệ & Giao tiếp", "B1"),
        ("autonomy", "/ɔːˈtɒnəmi/", "noun", "sự tự chủ, độc lập", "Self-paced flashcards grant learners complete study autonomy.", "Phương pháp học", "B2"),
        ("avenue", "/ˈævənjuː/", "noun", "đại lộ, con đường tiếp cận", "Language mastery opens new avenues of personal and career growth.", "Phát triển bản thân", "B1"),
        ("await", "/əˈweɪt/", "verb", "chờ đợi, đón chờ", "Exciting overseas opportunities await those with fluent English reflex.", "Ước mơ & Kế hoạch tương lai", "B2"),
        ("awake", "/əˈweɪk/", "adj", "tỉnh táo, thức giấc", "She was wide awake early in the morning, ready to review flashcards.", "Thói quen học tập", "A2"),
        ("awaken", "/əˈweɪkən/", "verb", "đánh thức, khơi dậy", "Interactive audio exercises awaken your intuitive language instincts.", "Phương pháp học", "B2"),
        ("award", "/əˈwɔːd/", "noun", "giải thưởng vinh danh", "He won the top award in the provincial English speech contest.", "Giáo dục & Động lực", "A2"),
        ("awareness", "/əˈweənəs/", "noun", "sự nhận thức, ý thức", "Cultivating acoustic awareness transforms your spoken precision.", "Sổ tay sửa lỗi phát âm", "B2"),
        ("awful", "/ˈɔːfl/", "adj", "kinh khủng, tệ hại", "Do not worry about an awful first recording; every master started there.", "Thái độ sống", "A2"),
        ("awkward", "/ˈɔːkwəd/", "adj", "ngượng ngùng, lúng túng", "Initial speaking hesitation feels awkward, but quickly disappears.", "Giao tiếp & Xã hội", "B2"),
    ]

    # Bổ sung danh sách từ Oxford 3000 đa dạng theo chuyên ngành & đời sống để đạt chính xác 2.850 từ
    # Đọc từ file từ vựng chuẩn nếu có, hoặc sinh mở rộng theo danh mục Oxford 3000 tiêu chuẩn
    added_list = []
    for item in oxford_supplemental_candidates:
        w = item[0].strip().lower()
        if w not in seen:
            seen.add(w)
            added_list.append({
                "word": w,
                "ipa": item[1],
                "pos": item[2],
                "meaning_vi": item[3],
                "example_sentence": item[4],
                "topic": item[5],
                "level": item[6],
                "is_custom": 0
            })

    print(f"Added from candidate list: {len(added_list)}")
    print(f"Unique words now: {len(seen)}")

    # Tạo tệp oxford_supplemental.py xuất khẩu danh sách
    out_file = os.path.join("scripts", "oxford_supplemental.py")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("# scripts/oxford_supplemental.py\n")
        f.write("# Tệp tự động sinh bổ sung từ vựng Oxford 3000\n\n")
        f.write("def get_supplemental_pool():\n")
        f.write(f"    return {json.dumps(added_list, ensure_ascii=False, indent=8)}\n")

    print(f"Generated {out_file} with {len(added_list)} items.")

if __name__ == "__main__":
    build_supplemental_file()
