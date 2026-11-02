"""
upgrade_excel_1000_words.py
Nâng cấp tệp Excel từ 560 từ lên đúng 1000 từ vựng cốt lõi tiếng Anh,
chia đều 100 ngày (10 từ/ngày), bảo lưu các từ đã có, bổ sung đầy đủ ngữ pháp nền tảng.
Tạo 2 sheet:
- Sheet 1: Lộ trình 1000 từ cốt lõi
- Sheet 2: Luyen_Dich_Passages
"""

import sys
import os
import glob
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def get_existing_words(file_path):
    wb = openpyxl.load_workbook(file_path, data_only=True)
    # Check sheet names
    sheet_name = 'Lộ trình 80 Ngày (560 từ)'
    if sheet_name not in wb.sheetnames:
        sheet_name = wb.sheetnames[0]
    sheet = wb[sheet_name]
    
    rows = list(sheet.iter_rows(values_only=True))
    data_rows = []
    # Identify header row
    header_idx = 1
    for idx, r in enumerate(rows[:5]):
        if r and any('từ vựng' in str(c).lower() or 'word' in str(c).lower() for c in r if c):
            header_idx = idx
            break
            
    for r in rows[header_idx + 1:]:
        if not r or len(r) < 5:
            continue
        # Expected: day, stt, topic, word, ipa, pos, meaning, example, note, status
        day = r[0]
        word = r[3] if len(r) > 3 else None
        if not word or not str(word).strip():
            continue
        word_clean = str(word).strip().lower()
        ipa = str(r[4]).strip() if len(r) > 4 and r[4] else ""
        pos = str(r[5]).strip() if len(r) > 5 and r[5] else ""
        meaning = str(r[6]).strip() if len(r) > 6 and r[6] else ""
        example = str(r[7]).strip() if len(r) > 7 and r[7] else ""
        topic = str(r[2]).strip() if len(r) > 2 and r[2] else "Giao tiếp cơ bản"
        
        data_rows.append({
            "word": word_clean,
            "ipa": ipa,
            "pos": pos,
            "meaning": meaning,
            "example": example,
            "topic": topic
        })
    print(f"Loaded {len(data_rows)} existing words from {file_path}")
    return data_rows

# Define essential grammar and foundational vocabulary to add
FOUNDATIONAL_GRAMMAR = [
    # Đại từ nhân xưng & Sở hữu
    {"word": "i", "ipa": "/aɪ/", "pos": "pron.", "meaning": "tôi, mình", "example": "I am learning English.", "topic": "Đại từ & Ngữ pháp nền tảng"},
    {"word": "you", "ipa": "/juː/", "pos": "pron.", "meaning": "bạn, các bạn", "example": "You are a good friend.", "topic": "Đại từ & Ngữ pháp nền tảng"},
    {"word": "we", "ipa": "/wiː/", "pos": "pron.", "meaning": "chúng tôi, chúng ta", "example": "We learn together.", "topic": "Đại từ & Ngữ pháp nền tảng"},
    {"word": "they", "ipa": "/ðeɪ/", "pos": "pron.", "meaning": "họ, chúng nó", "example": "They are happy.", "topic": "Đại từ & Ngữ pháp nền tảng"},
    {"word": "he", "ipa": "/hiː/", "pos": "pron.", "meaning": "anh ấy, cậu ấy", "example": "He speaks clearly.", "topic": "Đại từ & Ngữ pháp nền tảng"},
    {"word": "she", "ipa": "/ʃiː/", "pos": "pron.", "meaning": "cô ấy, chị ấy", "example": "She is very kind.", "topic": "Đại từ & Ngữ pháp nền tảng"},
    {"word": "it", "ipa": "/ɪt/", "pos": "pron.", "meaning": "nó, điều đó", "example": "It is a sunny day.", "topic": "Đại từ & Ngữ pháp nền tảng"},
    {"word": "me", "ipa": "/miː/", "pos": "pron.", "meaning": "tôi (tân ngữ)", "example": "Listen to me, please.", "topic": "Đại từ & Ngữ pháp nền tảng"},
    {"word": "him", "ipa": "/hɪm/", "pos": "pron.", "meaning": "anh ấy (tân ngữ)", "example": "I meet him every day.", "topic": "Đại từ & Ngữ pháp nền tảng"},
    {"word": "her", "ipa": "/hɜːr/", "pos": "pron., det.", "meaning": "cô ấy (tân ngữ / của cô ấy)", "example": "Her voice is sweet.", "topic": "Đại từ & Ngữ pháp nền tảng"},
    {"word": "us", "ipa": "/ʌs/", "pos": "pron.", "meaning": "chúng tôi (tân ngữ)", "example": "Join us for lunch.", "topic": "Đại từ & Ngữ pháp nền tảng"},
    {"word": "them", "ipa": "/ðem/", "pos": "pron.", "meaning": "họ (tân ngữ)", "example": "I know them well.", "topic": "Đại từ & Ngữ pháp nền tảng"},
    {"word": "my", "ipa": "/maɪ/", "pos": "det.", "meaning": "của tôi", "example": "This is my book.", "topic": "Đại từ & Ngữ pháp nền tảng"},
    {"word": "your", "ipa": "/jɔːr/", "pos": "det.", "meaning": "của bạn", "example": "What is your name?", "topic": "Đại từ & Ngữ pháp nền tảng"},
    {"word": "our", "ipa": "/aʊər/", "pos": "det.", "meaning": "của chúng tôi", "example": "Our house is cozy.", "topic": "Đại từ & Ngữ pháp nền tảng"},
    {"word": "their", "ipa": "/ðer/", "pos": "det.", "meaning": "của họ", "example": "Their car is new.", "topic": "Đại từ & Ngữ pháp nền tảng"},
    {"word": "his", "ipa": "/hɪz/", "pos": "det., pron.", "meaning": "của anh ấy", "example": "His job is interesting.", "topic": "Đại từ & Ngữ pháp nền tảng"},
    {"word": "its", "ipa": "/ɪts/", "pos": "det.", "meaning": "của nó", "example": "The cat licked its paw.", "topic": "Đại từ & Ngữ pháp nền tảng"},
    {"word": "this", "ipa": "/ðɪs/", "pos": "pron., det.", "meaning": "cái này, điều này", "example": "This is my friend.", "topic": "Đại từ & Ngữ pháp nền tảng"},
    {"word": "that", "ipa": "/ðæt/", "pos": "pron., det.", "meaning": "cái kia, điều đó", "example": "That sounds great.", "topic": "Đại từ & Ngữ pháp nền tảng"},
    {"word": "these", "ipa": "/ðiːz/", "pos": "pron., det.", "meaning": "những cái này", "example": "These flowers are pretty.", "topic": "Đại từ & Ngữ pháp nền tảng"},
    {"word": "those", "ipa": "/ðoʊz/", "pos": "pron., det.", "meaning": "những cái kia", "example": "Those birds fly high.", "topic": "Đại từ & Ngữ pháp nền tảng"},

    # Động từ To Be
    {"word": "am", "ipa": "/æm/", "pos": "v.", "meaning": "thì, là, ở (đi với I)", "example": "I am ready to learn.", "topic": "Động từ To Be & Trợ động từ"},
    {"word": "is", "ipa": "/ɪz/", "pos": "v.", "meaning": "thì, là, ở (số ít)", "example": "She is a good doctor.", "topic": "Động từ To Be & Trợ động từ"},
    {"word": "are", "ipa": "/ɑːr/", "pos": "v.", "meaning": "thì, là, ở (số nhiều/you)", "example": "They are friendly people.", "topic": "Động từ To Be & Trợ động từ"},
    {"word": "was", "ipa": "/wɑːz/", "pos": "v.", "meaning": "đã là, đã ở (quá khứ số ít)", "example": "I was at home yesterday.", "topic": "Động từ To Be & Trợ động từ"},
    {"word": "were", "ipa": "/wɜːr/", "pos": "v.", "meaning": "đã là, đã ở (quá khứ số nhiều)", "example": "We were very excited.", "topic": "Động từ To Be & Trợ động từ"},
    {"word": "be", "ipa": "/biː/", "pos": "v.", "meaning": "thì, là, ở (nguyên mẫu)", "example": "Be patient and calm.", "topic": "Động từ To Be & Trợ động từ"},
    {"word": "been", "ipa": "/bɪn/", "pos": "v.", "meaning": "đã từng (phân từ 2)", "example": "I have been there before.", "topic": "Động từ To Be & Trợ động từ"},
    {"word": "being", "ipa": "/ˈbiː.ɪŋ/", "pos": "v.", "meaning": "đang hiện diện, đang là", "example": "He is being helpful.", "topic": "Động từ To Be & Trợ động từ"},

    # Trợ động từ & Động từ khiếm khuyết
    {"word": "do", "ipa": "/duː/", "pos": "v., aux.", "meaning": "làm; trợ động từ", "example": "Do you speak English?", "topic": "Động từ To Be & Trợ động từ"},
    {"word": "does", "ipa": "/dʌz/", "pos": "v., aux.", "meaning": "làm (ngôi thứ 3 số ít)", "example": "Does he work here?", "topic": "Động từ To Be & Trợ động từ"},
    {"word": "did", "ipa": "/dɪd/", "pos": "v., aux.", "meaning": "đã làm (quá khứ)", "example": "Did you finish the test?", "topic": "Động từ To Be & Trợ động từ"},
    {"word": "has", "ipa": "/hæz/", "pos": "v., aux.", "meaning": "có, đã (ngôi thứ 3)", "example": "She has a nice dog.", "topic": "Động từ To Be & Trợ động từ"},
    {"word": "had", "ipa": "/hæd/", "pos": "v., aux.", "meaning": "đã có, từng có", "example": "We had a good time.", "topic": "Động từ To Be & Trợ động từ"},
    {"word": "will", "ipa": "/wɪl/", "pos": "aux. v.", "meaning": "sẽ (tương lai)", "example": "I will practice every day.", "topic": "Động từ To Be & Trợ động từ"},
    {"word": "shall", "ipa": "/ʃæl/", "pos": "aux. v.", "meaning": "sẽ, nên (đề xuất)", "example": "Shall we begin our lesson?", "topic": "Động từ To Be & Trợ động từ"},
    {"word": "may", "ipa": "/meɪ/", "pos": "aux. v.", "meaning": "có thể, xin phép", "example": "May I ask a question?", "topic": "Động từ To Be & Trợ động từ"},

    # Mạo từ & Giới từ cơ bản
    {"word": "a", "ipa": "/eɪ, ə/", "pos": "art.", "meaning": "một (mạo từ trước phụ âm)", "example": "I have a new goal.", "topic": "Mạo từ & Giới từ cơ bản"},
    {"word": "an", "ipa": "/æn, ən/", "pos": "art.", "meaning": "một (mạo từ trước nguyên âm)", "example": "She eats an apple.", "topic": "Mạo từ & Giới từ cơ bản"},
    {"word": "the", "ipa": "/ðiː, ðə/", "pos": "art.", "meaning": "cái đó, người đó (xác định)", "example": "The sun is bright.", "topic": "Mạo từ & Giới từ cơ bản"},
    {"word": "for", "ipa": "/fɔːr/", "pos": "prep.", "meaning": "cho, vì, dành cho", "example": "This gift is for you.", "topic": "Mạo từ & Giới từ cơ bản"},
    {"word": "by", "ipa": "/baɪ/", "pos": "prep.", "meaning": "bởi, bằng phương tiện", "example": "We travel by bus.", "topic": "Mạo từ & Giới từ cơ bản"},
    {"word": "about", "ipa": "/əˈbaʊt/", "pos": "prep., adv.", "meaning": "về điều gì, khoảng chừng", "example": "Tell me about your job.", "topic": "Mạo từ & Giới từ cơ bản"},
    {"word": "through", "ipa": "/θruː/", "pos": "prep.", "meaning": "qua, xuyên suốt", "example": "We walked through the park.", "topic": "Mạo từ & Giới từ cơ bản"},
    {"word": "without", "ipa": "/wɪˈðaʊt/", "pos": "prep.", "meaning": "không có, thiếu vắng", "example": "I cannot drink coffee without sugar.", "topic": "Mạo từ & Giới từ cơ bản"},
    {"word": "around", "ipa": "/əˈraʊnd/", "pos": "prep., adv.", "meaning": "xung quanh, vòng quanh", "example": "Look around the room.", "topic": "Mạo từ & Giới từ cơ bản"},
    {"word": "against", "ipa": "/əˈɡenst/", "pos": "prep.", "meaning": "chống lại, dựa vào", "example": "He leaned against the wall.", "topic": "Mạo từ & Giới từ cơ bản"},
]

def generate_1000_list(existing_words):
    # Keep track of words already in list
    seen = set()
    result = []
    
    # First: add foundational grammar
    for item in FOUNDATIONAL_GRAMMAR:
        w = item["word"].lower().strip()
        if w not in seen:
            seen.add(w)
            result.append(item)
            
    # Second: add all existing 560 words (preserving them!)
    for item in existing_words:
        w = item["word"].lower().strip()
        if w not in seen:
            seen.add(w)
            result.append(item)

    print(f"Combined base count: {len(result)}")
    
    # Additional vocabulary categories to reach exactly 1000 words
    additional_pools = [
        # Số đếm bổ sung
        ("Số đếm & Định lượng", [
            ("zero", "/ˈzɪr.oʊ/", "num.", "số 0", "The temperature dropped to zero."),
            ("two", "/tuː/", "num.", "số 2", "I have two brothers."),
            ("four", "/fɔːr/", "num.", "số 4", "A square has four sides."),
            ("six", "/sɪks/", "num.", "số 6", "We meet at six o'clock."),
            ("eight", "/eɪt/", "num.", "số 8", "She slept for eight hours."),
            ("nine", "/naɪn/", "num.", "số 9", "The cat has nine lives."),
            ("ten", "/ten/", "num.", "số 10", "Count from one to ten."),
            ("eleven", "/ɪˈlev.ən/", "num.", "số 11", "He arrived at eleven."),
            ("twelve", "/twelv/", "num.", "số 12", "A year has twelve months."),
            ("thirteen", "/ˌθɜːrˈtiːn/", "num.", "số 13", "She is thirteen years old."),
            ("fourteen", "/ˌfɔːrˈtiːn/", "num.", "số 14", "There are fourteen days in two weeks."),
            ("fifteen", "/ˌfɪfˈtiːn/", "num.", "số 15", "Wait for fifteen minutes."),
            ("sixteen", "/ˌsɪkˈstiːn/", "num.", "số 16", "He drove a sixteen-wheel truck."),
            ("seventeen", "/ˌsev.ənˈtiːn/", "num.", "số 17", "Room number seventeen is ready."),
            ("eighteen", "/ˌeɪˈtiːn/", "num.", "số 18", "You become an adult at eighteen."),
            ("nineteen", "/ˌnaɪnˈtiːn/", "num.", "số 19", "Page nineteen has the answer."),
            ("twenty", "/ˈtwen.ti/", "num.", "số 20", "Twenty students attended class."),
            ("thirty", "/ˈθɜːr.t̬i/", "num.", "số 30", "It takes thirty minutes."),
            ("forty", "/ˈfɔːr.t̬i/", "num.", "số 40", "Life begins at forty."),
            ("fifty", "/ˈfɪf.t̬i/", "num.", "số 50", "The speed limit is fifty."),
            ("sixty", "/ˈsɪk.sti/", "num.", "số 60", "An hour has sixty minutes."),
            ("seventy", "/ˈsev.ən.t̬i/", "num.", "số 70", "He scored seventy points."),
            ("eighty", "/ˈeɪ.t̬i/", "num.", "số 80", "The roadmap lasts for eighty days."),
            ("ninety", "/ˈnaɪn.t̬i/", "num.", "số 90", "Ninety percent of students passed."),
            ("hundred", "/ˈhʌn.drəd/", "num.", "một trăm", "One hundred percent correct!"),
            ("thousand", "/ˈθaʊ.zənd/", "num.", "một nghìn", "A thousand thanks to you."),
            ("million", "/ˈmɪl.jən/", "num.", "một triệu", "The city has one million people."),
            ("billion", "/ˈbɪl.jən/", "num.", "một tỷ", "The world has eight billion people."),
            ("half", "/hæf/", "n., det.", "một nửa", "Half of the work is done."),
            ("quarter", "/ˈkwɔːr.t̬ɚ/", "n.", "một phần tư, 15 phút", "It is a quarter past three."),
            ("double", "/ˈdʌb.əl/", "adj., v.", "gấp đôi", "Double check your answer."),
            ("triple", "/ˈtrɪp.əl/", "adj., v.", "gấp ba", "The company had triple profits."),
        ]),
        
        # Gia đình & Người thân mở rộng
        ("Gia đình & Người thân mở rộng", [
            ("grandfather", "/ˈɡræn.fɑː.ðər/", "n.", "ông nội, ông ngoại", "My grandfather tells great stories."),
            ("grandmother", "/ˈɡræn.mʌð.ər/", "n.", "bà nội, bà ngoại", "My grandmother bakes delicious cakes."),
            ("grandson", "/ˈɡræn.sʌn/", "n.", "cháu trai (của ông bà)", "He loves playing with his grandson."),
            ("granddaughter", "/ˈɡræn.dɑː.t̬ɚ/", "n.", "cháu gái (của ông bà)", "Her granddaughter is a smart student."),
            ("uncle", "/ˈʌŋ.kəl/", "n.", "chú, bác, cậu", "Uncle Tom lives in London."),
            ("aunt", "/ænt/", "n.", "cô, dì, bác gái", "Aunt Mary is very kind."),
            ("cousin", "/ˈkʌz.ən/", "n.", "anh chị em họ", "My cousin visits us in summer."),
            ("nephew", "/ˈnef.juː/", "n.", "cháu trai (con anh/chị/em)", "I bought a toy for my nephew."),
            ("niece", "/niːs/", "n.", "cháu gái (con anh/chị/em)", "My niece draws wonderful pictures."),
            ("husband", "/ˈhʌz.bənd/", "n.", "người chồng", "Her husband is an engineer."),
            ("wife", "/waɪf/", "n.", "người vợ", "His wife is a talented doctor."),
            ("son", "/sʌn/", "n.", "con trai", "Their son is studying abroad."),
            ("daughter", "/ˈdɑː.t̬ɚ/", "n.", "con gái", "She has a five-year-old daughter."),
            ("baby", "/ˈbeɪ.bi/", "n.", "em bé", "The baby is sleeping peacefully."),
            ("kid", "/kɪd/", "n.", "đứa trẻ, con nít", "Kids love playing outdoors."),
            ("neighbor", "/ˈneɪ.bər/", "n.", "hàng xóm", "Our neighbor is very friendly."),
            ("colleague", "/ˈkɑː.liːɡ/", "n.", "đồng nghiệp", "I respect all my colleagues."),
            ("partner", "/ˈpɑːrt.nɚ/", "n.", "đối tác, bạn đồng hành", "They are trusted business partners."),
        ]),
        
        # Thức ăn, Món ăn & Nấu nướng
        ("Ẩm thực & Nấu nướng", [
            ("breakfast", "/ˈbrek.fəst/", "n.", "bữa ăn sáng", "I eat a healthy breakfast."),
            ("lunch", "/lʌntʃ/", "n.", "bữa ăn trưa", "Let's have lunch together."),
            ("dinner", "/ˈdɪn.ɚ/", "n.", "bữa ăn tối", "Dinner is ready on the table."),
            ("snack", "/snæk/", "n.", "món ăn vặt", "Have a fruit snack in the afternoon."),
            ("meal", "/miːl/", "n.", "bữa ăn", "Enjoy your delicious meal!"),
            ("beef", "/biːf/", "n.", "thịt bò", "Grilled beef tastes amazing."),
            ("pork", "/pɔːrk/", "n.", "thịt heo, lợn", "Pork is popular in Vietnamese dishes."),
            ("chicken", "/ˈtʃɪk.ɪn/", "n.", "thịt gà; con gà", "Fried chicken is crunchy."),
            ("seafood", "/ˈsiː.fuːd/", "n.", "hải sản", "Da Nang has fresh seafood."),
            ("shrimp", "/ʃrɪmp/", "n.", "con tôm", "Boiled shrimp with lemon salt is great."),
            ("crab", "/kræb/", "n.", "con cua", "We enjoyed fresh steamed crab."),
            ("carrot", "/ˈker.ət/", "n.", "củ cà rốt", "Carrots are rich in vitamin A."),
            ("onion", "/ˈʌn.jən/", "n.", "củ hành tây", "Cut the onion into small pieces."),
            ("garlic", "/ˈɡɑːr.lɪk/", "n.", "củ tỏi", "Garlic adds aroma to the dish."),
            ("noodle", "/ˈnuː.dəl/", "n.", "mì sợi, bún phở", "Pho is a famous Vietnamese noodle soup."),
            ("salad", "/ˈsæl.əd/", "n.", "món gỏi, sa-lát", "Fresh green salad is good for health."),
            ("pepper", "/ˈpep.ɚ/", "n.", "hạt tiêu; quả ớt chuông", "Black pepper gives a warm spicy taste."),
            ("oil", "/ɔɪl/", "n.", "dầu ăn, dầu thực vật", "Pour cooking oil into the pan."),
            ("butter", "/ˈbʌt̬.ɚ/", "n.", "bơ ăn", "Spread butter on the warm bread."),
            ("cheese", "/tʃiːz/", "n.", "phô mai", "Pizza tastes best with melted cheese."),
            ("apple", "/ˈæp.əl/", "n.", "quả táo", "An apple a day keeps the doctor away."),
            ("banana", "/bəˈnæn.ə/", "n.", "quả chuối", "Bananas are rich in potassium."),
            ("grape", "/ɡreɪp/", "n.", "quả nho", "Sweet purple grapes are chilled."),
            ("strawberry", "/ˈstrɑːˌber.i/", "n.", "quả dâu tây", "Strawberries go well with yogurt."),
            ("watermelon", "/ˈwɑː.t̬ɚˌmel.ən/", "n.", "quả dưa hấu", "Cold watermelon is perfect for hot days."),
            ("lemon", "/ˈlem.ən/", "n.", "quả chanh vàng", "Squeeze fresh lemon into iced tea."),
            ("bowl", "/boʊl/", "n.", "cái bát, cái tô", "Give me a bowl of warm rice."),
            ("plate", "/pleɪt/", "n.", "cái đĩa thức ăn", "Place the fish on the serving plate."),
            ("spoon", "/spuːn/", "n.", "cái thìa, cái muỗng", "Use a spoon to drink the soup."),
            ("fork", "/fɔːrk/", "n.", "cái nĩa", "Hold the fork in your left hand."),
            ("knife", "/naɪf/", "n.", "con dao", "Use a sharp knife to slice bread."),
            ("cup", "/kʌp/", "n.", "chiếc tách, chén", "Would you like a cup of green tea?"),
            ("glass", "/ɡlæs/", "n.", "chiếc ly thủy tinh", "Drink a glass of water every morning."),
            ("bottle", "/ˈbɑː.t̬əl/", "n.", "chiếc chai lọ", "Keep a bottle of water on your desk."),
            ("bake", "/beɪk/", "v.", "nướng bánh", "She loves to bake chocolate cookies."),
            ("boil", "/bɔɪl/", "v.", "luộc, đun sôi", "Boil the water before making tea."),
            ("fry", "/fraɪ/", "v.", "chiên, rán", "Fry the fish until golden crispy."),
            ("mix", "/mɪks/", "v.", "trộn lẫn, pha trộn", "Mix all ingredients in a bowl."),
        ]),

        # Nhà cửa & Đồ nội thất
        ("Nhà cửa & Tiện nghi đời sống", [
            ("apartment", "/əˈpɑːrt.mənt/", "n.", "căn hộ chung cư", "They live in a modern apartment."),
            ("balcony", "/ˈbæl.kə.ni/", "n.", "ban công", "Flowers bloom on the sunny balcony."),
            ("garden", "/ˈɡɑːr.dən/", "n.", "khu vườn", "He waters vegetables in the garden."),
            ("roof", "/ruːf/", "n.", "mái nhà", "Rain tapped softly on the roof."),
            ("wall", "/wɑːl/", "n.", "bức tường", "They painted the wall light blue."),
            ("floor", "/flɔːr/", "n.", "sàn nhà, tầng lầu", "Wooden floor is cool and clean."),
            ("ceiling", "/ˈsiː.lɪŋ/", "n.", "trần nhà", "A ceiling fan cools the room."),
            ("stairs", "/sterz/", "n.", "cầu thang bộ", "Walk slowly up the stairs."),
            ("elevator", "/ˈel.ə.veɪ.t̬ɚ/", "n.", "thang máy", "Take the elevator to the 10th floor."),
            ("furniture", "/ˈfɜːr.nɪ.tʃɚ/", "n.", "đồ nội thất", "Wooden furniture lasts for years."),
            ("sofa", "/ˈsoʊ.fə/", "n.", "ghế sô-pha", "Sit comfortably on the sofa."),
            ("curtain", "/ˈkɜːr.tən/", "n.", "rèm cửa sổ", "Open the curtain to let sunshine in."),
            ("carpet", "/ˈkɑːr.pɪt/", "n.", "tấm thảm trải sàn", "The soft carpet warms the feet."),
            ("refrigerator", "/rɪˈfrɪdʒ.ə.reɪ.t̬ɚ/", "n.", "tủ lạnh", "Store milk inside the refrigerator."),
            ("microwave", "/ˈmaɪ.krə.weɪv/", "n.", "lò vi sóng", "Heat the soup in the microwave."),
            ("sink", "/sɪŋk/", "n.", "bồn rửa bát/rửa tay", "Wash your hands at the sink."),
            ("faucet", "/ˈfɑː.sət/", "n.", "vòi nước", "Turn off the faucet to save water."),
            ("pillow", "/ˈpɪl.oʊ/", "n.", "chiếc gối đầu", "A soft pillow helps you sleep well."),
            ("mattress", "/ˈmæt.rəs/", "n.", "tấm đệm, nệm nằm", "This mattress is firm and comfortable."),
            ("shelf", "/ʃelf/", "n.", "kệ, giá để đồ", "Books are arranged on the shelf."),
            ("drawer", "/drɔːr/", "n.", "ngăn kéo tủ", "Keep your passport in the top drawer."),
            ("closet", "/ˈklɑː.zət/", "n.", "tủ quần áo", "Hang your jacket in the closet."),
            ("broom", "/bruːm/", "n.", "cây chổi quét nhà", "Use the broom to sweep the dust."),
            ("mop", "/mɑːp/", "n., v.", "cây lau nhà; lau sàn", "Mop the kitchen floor after cooking."),
            ("iron", "/aɪrn/", "n., v.", "bàn là; là ủi", "Iron your shirt before the interview."),
        ]),

        # Hoạt động hàng ngày & Thói quen
        ("Hoạt động & Thói quen đời thường", [
            ("shave", "/ʃeɪv/", "v.", "cạo râu", "He shaves his face every morning."),
            ("comb", "/koʊm/", "v., n.", "chải đầu; cái lược", "Comb your hair neatly."),
            ("feed", "/fiːd/", "v.", "cho ăn", "Feed the cat twice a day."),
            ("stretch", "/stretʃ/", "v.", "vươn vai, duỗi cơ", "Stretch your body after waking up."),
            ("exercise", "/ˈek.sɚ.saɪz/", "n., v.", "tập thể dục", "Morning exercise keeps you healthy."),
            ("shower", "/ˈʃaʊ.ɚ/", "n., v.", "tắm vòi sen", "Take a warm shower after work."),
            ("dress", "/dres/", "v., n.", "mặc đồ; váy", "Dress warmly in the cold winter."),
            ("listen", "/ˈlɪs.ən/", "v.", "chú ý lắng nghe", "Listen carefully to the teacher."),
            ("hear", "/hɪr/", "v.", "nghe thấy", "Can you hear the birds singing?"),
            ("see", "/siː/", "v.", "nhìn thấy", "I see a boat in the distance."),
            ("look", "/lʊk/", "v.", "nhìn ngắm, xem xét", "Look at the colorful rainbow."),
            ("watch", "/wɑːtʃ/", "v.", "theo dõi, xem", "Watch an English movie tonight."),
            ("notice", "/ˈnoʊ.t̬ɪs/", "v., n.", "nhận thấy, chú ý", "Did you notice the price change?"),
            ("touch", "/tʌtʃ/", "v., n.", "chạm vào, tiếp xúc", "Do not touch the hot stove."),
            ("smell", "/smel/", "v., n.", "ngửi mùi; hương thơm", "Fresh coffee smells delightful."),
            ("taste", "/teɪst/", "v., n.", "nếm vị; mùi vị", "Taste the soup to check the salt."),
            ("borrow", "/ˈbɑːr.oʊ/", "v.", "vay, mượn", "Can I borrow your pencil?"),
            ("lend", "/lend/", "v.", "cho vay, cho mượn", "He lent me a helpful dictionary."),
            ("rent", "/rent/", "v., n.", "thuê mướn; tiền thuê", "They rent a cozy room near school."),
            ("ride", "/raɪd/", "v.", "cưỡi, lái (xe đạp/máy)", "Ride your bicycle safely."),
            ("swim", "/swɪm/", "v.", "bơi lội", "Swimming strengthens your back."),
            ("fly", "/flaɪ/", "v.", "bay lượn; đi máy bay", "Birds fly south in autumn."),
            ("arrive", "/əˈraɪv/", "v.", "đến nơi", "The train will arrive at five."),
            ("depart", "/dɪˈpɑːrt/", "v.", "khởi hành", "The flight departs on schedule."),
            ("wait", "/weɪt/", "v.", "chờ đợi", "Please wait a moment."),
        ]),

        # Cảm xúc, Thái độ & Tính cách
        ("Cảm xúc, Thái độ & Tính cách", [
            ("glad", "/ɡlæd/", "adj.", "vui mừng", "I am glad to meet you."),
            ("pleased", "/pliːzd/", "adj.", "hài lòng, thỏa mãn", "The teacher is pleased with your progress."),
            ("delighted", "/dɪˈlaɪ.t̬ɪd/", "adj.", "vô cùng vui sướng", "We were delighted by the good news."),
            ("cheerful", "/ˈtʃɪr.fəl/", "adj.", "vui vẻ hoạt bát", "Her cheerful smile brightens the day."),
            ("nervous", "/ˈnɜːr.vəs/", "adj.", "lo lắng bồn chồn", "Take a deep breath if you feel nervous."),
            ("anxious", "/ˈæŋk.ʃəs/", "adj.", "sốt ruột, lo âu", "Do not be anxious about tomorrow."),
            ("worried", "/ˈwɝː.id/", "adj.", "lo lắng trăn trở", "Parents are worried when kids are sick."),
            ("scared", "/skerd/", "adj.", "hoảng sợ", "The thunder scared the little puppy."),
            ("brave", "/breɪv/", "adj.", "dũng cảm, kiên cường", "Brave firefighters saved the cat."),
            ("shy", "/ʃaɪ/", "adj.", "nhút nhát, e dè", "The shy boy hid behind his mother."),
            ("humble", "/ˈhʌm.bəl/", "adj.", "khiêm tốn nhã nhặn", "True leaders remain humble."),
            ("curious", "/ˈkjʊr.i.əs/", "adj.", "tò mò ham học hỏi", "Children are curious about nature."),
            ("eager", "/ˈiː.ɡɚ/", "adj.", "háo hức thiết tha", "Students are eager to learn new words."),
            ("surprised", "/sɚˈpraɪzd/", "adj.", "ngạc nhiên", "I was surprised by the sudden gift."),
            ("amazed", "/əˈmeɪzd/", "adj.", "sửng sốt, thán phục", "We were amazed by his fluent English."),
            ("exhausted", "/ɪɡˈzɑː.stɪd/", "adj.", "kiệt sức mệt lử", "He felt exhausted after running ten miles."),
            ("lazy", "/ˈleɪ.zi/", "adj.", "lười biếng", "Do not be lazy on Sunday mornings."),
            ("free", "/friː/", "adj.", "rảnh rỗi; tự do; miễn phí", "Are you free this weekend?"),
            ("interested", "/ˈɪn.trɪ.stɪd/", "adj.", "thích thú quan tâm", "I am interested in British history."),
            ("confused", "/kənˈfjuːzd/", "adj.", "bối rối, khó hiểu", "Ask for help if you feel confused."),
            ("patient", "/ˈpeɪ.ʃənt/", "adj.", "kiên nhẫn, nhẫn nại", "Be patient with your pronunciation."),
            ("generous", "/ˈdʒen.ər.əs/", "adj.", "hào phóng, rộng lượng", "She is generous with her time."),
            ("cruel", "/ˈkruː.əl/", "adj.", "độc ác, tàn nhẫn", "Do not be cruel to small animals."),
            ("clumsy", "/ˈklʌm.zi/", "adj.", "vụng về, lóng ngóng", "He felt clumsy with chopsticks."),
            ("silly", "/ˈsɪl.i/", "adj.", "ngốc nghếch đáng yêu", "That was a silly small mistake."),
        ]),

        # Công việc, Công sở & Kinh doanh
        ("Nghề nghiệp & Môi trường công sở", [
            ("director", "/daɪˈrek.tɚ/", "n.", "giám đốc, đạo diễn", "The director approved our new project."),
            ("employee", "/ɪmˈplɔɪ.iː/", "n.", "nhân viên", "Every employee receives health insurance."),
            ("staff", "/stæf/", "n.", "đội ngũ nhân viên", "Hotel staff were polite and helpful."),
            ("assistant", "/əˈsɪs.tənt/", "n.", "trợ lý, phụ tá", "The personal assistant scheduled the trip."),
            ("secretary", "/ˈsek.rə.ter.i/", "n.", "thư ký", "The secretary answered client calls."),
            ("accountant", "/əˈkaʊn.tənt/", "n.", "kế toán viên", "The accountant checks balance sheets."),
            ("developer", "/dɪˈvel.ə.pɚ/", "n.", "nhà phát triển phần mềm", "The developer fixed the software bug."),
            ("designer", "/dɪˈzaɪ.nɚ/", "n.", "nhà thiết kế", "The graphic designer made a cool logo."),
            ("professor", "/prəˈfes.ɚ/", "n.", "giáo sư đại học", "Professor Brown lectured on linguistics."),
            ("pharmacist", "/ˈfɑːr.mə.sɪst/", "n.", "dược sĩ", "The pharmacist explained how to take medicine."),
            ("dentist", "/ˈden.t̬ɪst/", "n.", "nha sĩ", "Visit the dentist every six months."),
            ("lawyer", "/ˈlɑː.jɚ/", "n.", "luật sư", "The lawyer reviewed the business contract."),
            ("police", "/pəˈliːs/", "n.", "cảnh sát", "The police officer directed traffic."),
            ("soldier", "/ˈsoʊl.dʒɚ/", "n.", "người lính, bộ đội", "The brave soldier served his country."),
            ("pilot", "/ˈpaɪ.lət/", "n.", "phi công", "The airline pilot welcomed passengers."),
            ("mechanic", "/məˈkæn.ɪk/", "n.", "thợ máy sửa xe", "The mechanic inspected the car engine."),
            ("plumber", "/ˈplʌm.ɚ/", "n.", "thợ sửa ống nước", "The plumber fixed the bathroom pipe."),
            ("electrician", "/ˌɪl.ekˈtrɪʃ.ən/", "n.", "thợ điện", "The electrician repaired the wiring."),
            ("cashier", "/kæʃˈɪr/", "n.", "thu ngân", "Pay the cashier at the counter."),
            ("interview", "/ˈɪn.t̬ɚ.vjuː/", "n., v.", "phỏng vấn xin việc", "Wear a suit for the job interview."),
            ("resume", "/ˈrez.ə.meɪ/", "n.", "sơ yếu lý lịch, CV", "Send your updated resume to HR."),
            ("salary", "/ˈsæl.ɚ.i/", "n.", "lương tháng", "They offered a competitive monthly salary."),
            ("wage", "/weɪdʒ/", "n.", "tiền công theo giờ", "Minimum wage has increased this year."),
            ("bonus", "/ˈboʊ.nəs/", "n.", "tiền thưởng", "Employees received a year-end bonus."),
            ("contract", "/ˈkɑːn.trækt/", "n.", "hợp đồng giao kèo", "Read both pages of the contract carefully."),
            ("career", "/kəˈrɪr/", "n.", "sự nghiệp lâu dài", "Hard work leads to a fruitful career."),
            ("retire", "/rɪˈtaɪr/", "v.", "nghỉ hưu", "He plans to retire at sixty."),
            ("presentation", "/ˌprez.ənˈteɪ.ʃən/", "n.", "bài thuyết trình", "Her slide presentation was persuasive."),
            ("promotion", "/prəˈmoʊ.ʃən/", "n.", "sự thăng chức", "Congratulations on your well-deserved promotion!"),
        ]),

        # Mua sắm, Thương mại & Dịch vụ
        ("Mua sắm & Thương mại", [
            ("supermarket", "/ˈsuː.pɚˌmɑːr.kɪt/", "n.", "siêu thị lớn", "We buy groceries at the supermarket."),
            ("mall", "/mɑːl/", "n.", "trung tâm thương mại", "The shopping mall is crowded on Sundays."),
            ("boutique", "/buːˈtiːk/", "n.", "cửa hàng thời trang nhỏ", "She bought a silk scarf at the boutique."),
            ("pharmacy", "/ˈfɑːr.mə.si/", "n.", "hiệu thuốc tây", "Buy painkiller pills at the pharmacy."),
            ("bookstore", "/ˈbʊk.stɔːr/", "n.", "nhà sách", "I spent two hours browsing the bookstore."),
            ("customer", "/ˈkʌs.tə.mɚ/", "n.", "khách hàng", "Customer satisfaction is our priority."),
            ("product", "/ˈprɑː.dʌkt/", "n.", "sản phẩm hàng hóa", "This product is made from natural herbs."),
            ("goods", "/ɡʊdz/", "n.", "hàng hóa", "Transport goods across provinces."),
            ("brand", "/brænd/", "n.", "thương hiệu nhãn hàng", "Choose a reputable brand name."),
            ("quality", "/ˈkwɑː.lə.t̬i/", "n.", "chất lượng", "Focus on quality rather than quantity."),
            ("discount", "/ˈdɪs.kaʊnt/", "n.", "khoản giảm giá", "Students get a ten percent discount."),
            ("sale", "/seɪl/", "n.", "đợt giảm giá, bán hàng", "The summer sale ends on Friday."),
            ("coupon", "/ˈkuː.pɑːn/", "n.", "phiếu giảm giá", "Apply this coupon code at checkout."),
            ("invoice", "/ˈɪn.vɔɪs/", "n.", "hóa đơn thanh toán", "Please issue a tax invoice for the company."),
            ("refund", "/ˈriː.fʌnd/", "n., v.", "hoàn tiền lại", "You can request a full refund within 7 days."),
            ("exchange", "/ɪksˈtʃeɪndʒ/", "v., n.", "đổi trả hàng", "Exchange the shirt for a smaller size."),
            ("warranty", "/ˈwɔːr.ən.t̬i/", "n.", "chế độ bảo hành", "The laptop comes with a two-year warranty."),
            ("purse", "/pɜːrs/", "n.", "ví cầm tay nữ", "She took coins out of her purse."),
            ("affordable", "/əˈfɔːr.də.bəl/", "adj.", "vừa túi tiền, phải chăng", "This restaurant serves affordable meals."),
            ("bargain", "/ˈbɑːr.ɡɪn/", "n., v.", "món hời; trả giá", "Getting this coat for $20 was a bargain."),
            ("owe", "/oʊ/", "v.", "nợ nần", "I owe you five dollars."),
        ]),

        # Sức khỏe, Y tế & Cơ thể người mở rộng
        ("Y tế & Cơ thể người mở rộng", [
            ("brain", "/breɪn/", "n.", "não bộ", "Exercise stimulates blood flow to the brain."),
            ("forehead", "/ˈfɔːr.hed/", "n.", "trán", "Her mother touched her forehead to check fever."),
            ("eyebrow", "/ˈaɪ.braʊ/", "n.", "lông mày", "He raised an eyebrow in surprise."),
            ("eyelash", "/ˈaɪ.læʃ/", "n.", "lông mi", "Long eyelashes protect the eyes from dust."),
            ("throat", "/θroʊt/", "n.", "cổ họng", "Drink warm honey water for a sore throat."),
            ("neck", "/nek/", "n.", "chiếc cổ", "Wear a woolen scarf around your neck."),
            ("shoulder", "/ˈʃoʊl.dɚ/", "n.", "bờ vai", "He carried the heavy bag on his shoulder."),
            ("chest", "/tʃest/", "n.", "lồng ngực", "Take a deep breath and expand your chest."),
            ("lung", "/lʌŋ/", "n.", "lá phổi", "Fresh air is vital for healthy lungs."),
            ("stomach", "/ˈstʌm.ək/", "n.", "dạ dày, bụng", "Do not exercise on a full stomach."),
            ("elbow", "/ˈel.boʊ/", "n.", "khuỷu tay", "Rest your elbows on the table."),
            ("wrist", "/rɪst/", "n.", "cổ tay", "She wears an elegant watch on her wrist."),
            ("palm", "/pɑːm/", "n.", "lòng bàn tay", "Hold the warm cup in both palms."),
            ("thumb", "/θʌm/", "n.", "ngón tay cái", "Give a thumbs-up to show agreement."),
            ("nail", "/neɪl/", "n.", "móng tay, móng chân; đinh", "Keep your fingernails clean and short."),
            ("thigh", "/θaɪ/", "n.", "bắp đùi", "Cycling builds strong thigh muscles."),
            ("knee", "/niː/", "n.", "đầu gối", "Bend your knees when lifting weights."),
            ("ankle", "/ˈæŋ.kəl/", "n.", "mắt cá chân", "Be careful not to twist your ankle."),
            ("toe", "/toʊ/", "n.", "ngón chân", "Wiggle your toes in the warm sand."),
            ("skin", "/skɪn/", "n.", "làn da", "Sunscreen protects your skin from ultraviolet rays."),
            ("bone", "/boʊn/", "n.", "xương cốt", "Milk provides calcium for strong bones."),
            ("blood", "/blʌd/", "n.", "máu", "Regular blood tests monitor your health."),
            ("muscle", "/ˈmʌs.əl/", "n.", "cơ bắp", "Rest allows your muscles to recover."),
            ("healthy", "/ˈhel.θi/", "adj.", "khỏe mạnh", "A healthy lifestyle brings long happiness."),
            ("illness", "/ˈɪl.nəs/", "n.", "bệnh tật", "Wash hands regularly to prevent illness."),
            ("disease", "/dɪˈziːz/", "n.", "căn bệnh", "Vaccines protect children against diseases."),
            ("headache", "/ˈhed.eɪk/", "n.", "chứng đau đầu", "Dim the lights if you have a headache."),
            ("toothache", "/ˈtuːθ.eɪk/", "n.", "chứng đau răng", "See a dentist immediately for a toothache."),
            ("stomachache", "/ˈstʌm.ək.eɪk/", "n.", "đau bụng, đau bao tử", "Warm ginger tea helps with stomachache."),
            ("sneezing", "/ˈsniː.zɪŋ/", "n.", "hắt hơi", "Sneezing is a symptom of pollen allergy."),
            ("wound", "/wuːnd/", "n.", "vết thương hở", "Clean the wound with antiseptic liquid."),
            ("bandage", "/ˈbæn.dɪdʒ/", "n.", "băng dán vết thương", "Wrap a sterile bandage around the cut."),
            ("thermometer", "/θɚˈmɑː.mə.t̬ɚ/", "n.", "nhiệt kế", "Check body temperature with a thermometer."),
            ("ambulance", "/ˈæm.bjə.ləns/", "n.", "xe cứu thương", "Call an ambulance in medical emergencies."),
            ("patient", "/ˈpeɪ.ʃənt/", "n.", "bệnh nhân", "The doctor examined three patients."),
            ("treatment", "/ˈtriːt.mənt/", "n.", "phương pháp điều trị", "Early treatment ensures complete recovery."),
            ("cure", "/kjʊr/", "n., v.", "chữa khỏi bệnh", "Laughter is a wonderful cure for stress."),
        ]),

        # Thành phố, Giao thông & Phương tiện
        ("Giao thông & Môi trường đô thị", [
            ("capital", "/ˈkæp.ə.t̬əl/", "n.", "thủ đô", "Hanoi is the charming capital of Vietnam."),
            ("countryside", "/ˈkʌn.tri.saɪd/", "n.", "vùng quê nông thôn", "The peaceful countryside has fresh breezes."),
            ("village", "/ˈvɪl.ɪdʒ/", "n.", "ngôi làng", "Traditional crafts flourish in the craft village."),
            ("avenue", "/ˈæv.ə.nuː/", "n.", "đại lộ lớn", "Trees shade both sides of the avenue."),
            ("lane", "/leɪn/", "n.", "làn đường, con ngõ nhỏ", "Stay in the right lane when turning."),
            ("highway", "/ˈhaɪ.weɪ/", "n.", "đường cao tốc", "The highway connects two major cities."),
            ("tunnel", "/ˈtʌn.əl/", "n.", "đường hầm xuyên núi", "The car drove through the mountain tunnel."),
            ("sidewalk", "/ˈsaɪd.wɑːk/", "n.", "vỉa hè đi bộ", "Pedestrians should walk on the sidewalk."),
            ("crosswalk", "/ˈkrɑːs.wɑːk/", "n.", "vạch kẻ qua đường", "Always use the crosswalk to cross safely."),
            ("roundabout", "/ˈraʊnd.ə.baʊt/", "n.", "bùng binh, vòng xoay", "Yield to traffic already in the roundabout."),
            ("intersection", "/ˌɪn.t̬ɚˈsek.ʃən/", "n.", "ngã tư đường", "Slow down near the busy intersection."),
            ("vehicle", "/ˈviː.ə.kəl/", "n.", "phương tiện xe cộ", "Electric vehicles reduce air pollution."),
            ("taxi", "/ˈtæk.si/", "n.", "xe tắc-xi", "Hail a taxi outside the train station."),
            ("subway", "/ˈsʌb.weɪ/", "n.", "tàu điện ngầm", "Take the subway to avoid morning traffic jams."),
            ("metro", "/ˈmet.roʊ/", "n.", "hệ thống đường sắt đô thị", "The new metro line is fast and convenient."),
            ("motorcycle", "/ˈmoʊ.t̬ɚˌsaɪ.kəl/", "n.", "xe gắn máy", "Wear a sturdy helmet when riding a motorcycle."),
            ("scooter", "/ˈskuː.t̬ɚ/", "n.", "xe tay ga", "She commutes to university by scooter."),
            ("truck", "/trʌk/", "n.", "xe tải chở hàng", "The truck delivered fresh produce."),
            ("van", "/væn/", "n.", "xe tải nhỏ, xe bán tải", "The family traveled in a spacious van."),
            ("helicopter", "/ˈhel.əˌkɑːp.tɚ/", "n.", "máy bay trực thăng", "The rescue helicopter landed safely."),
            ("boat", "/boʊt/", "n.", "thuyền nhỏ", "Row a wooden boat on the serene lake."),
            ("ferry", "/ˈfer.i/", "n.", "phà chở khách", "The ferry crosses the river in fifteen minutes."),
            ("harbor", "/ˈhɑːr.bɚ/", "n.", "bến cảng", "Dozens of fishing ships dock in the harbor."),
            ("port", "/pɔːrt/", "n.", "cảng biển quốc tế", "Cargo containers are loaded at the deep-water port."),
            ("visa", "/ˈviː.zə/", "n.", "thị thực nhập cảnh", "Apply for your travel visa a month ahead."),
            ("suitcase", "/ˈsuːt.keɪs/", "n.", "va-li du lịch", "Pack your clothes neatly into the suitcase."),
            ("backpack", "/ˈbæk.pæk/", "n.", "ba-lô đeo lưng", "Put water and a notebook inside your backpack."),
            ("resort", "/rɪˈzɔːrt/", "n.", "khu nghỉ dưỡng", "Relax at a seaside beach resort."),
            ("hostel", "/ˈhɑː.stəl/", "n.", "nhà trọ bình dân", "Backpackers stay at friendly youth hostels."),
            ("reservation", "/ˌrez.ɚˈveɪ.ʃən/", "n.", "việc đặt phòng/bàn trước", "I made a hotel reservation online."),
            ("journey", "/ˈdʒɜːr.ni/", "n.", "hành trình trải nghiệm", "Every long journey starts with a single step."),
            ("tourist", "/ˈtʊr.ɪst/", "n.", "khách du lịch", "Tourists take photos at historical monuments."),
            ("passenger", "/ˈpæs.ən.dʒɚ/", "n.", "hành khách đi xe/tàu", "All passengers must fasten their seatbelts."),
            ("souvenir", "/ˌsuː.vəˈnɪr/", "n.", "quà lưu niệm", "Buy a handcrafted souvenir for your family."),
        ]),

        # Thiên nhiên, Đất trời & Môi trường
        ("Thiên nhiên & Môi trường sống", [
            ("ocean", "/ˈoʊ.ʃən/", "n.", "đại dương bao la", "The Pacific is the largest ocean on Earth."),
            ("sea", "/siː/", "n.", "biển khơi", "The calm sea sparkled under the afternoon sun."),
            ("island", "/ˈaɪ.lənd/", "n.", "hòn đảo", "Phu Quoc is a breathtaking tropical island."),
            ("beach", "/biːtʃ/", "n.", "bãi biển bờ cát", "Walk barefoot on the white sandy beach."),
            ("sand", "/sænd/", "n.", "cát", "Children built sandcastles by the shore."),
            ("forest", "/ˈfɔːr.ɪst/", "n.", "khu rừng rậm", "Tall pine trees grow in the cool forest."),
            ("jungle", "/ˈdʒʌŋ.ɡəl/", "n.", "rừng nhiệt đới nguyên sinh", "Monkeys swing through the dense jungle."),
            ("hill", "/hɪl/", "n.", "ngọn đồi thoai thoải", "Climb the hill to watch the picturesque sunset."),
            ("valley", "/ˈvæl.i/", "n.", "thung lũng xanh", "A tranquil stream flows through the valley."),
            ("desert", "/ˈdez.ɚt/", "n.", "sa mạc khô cằn", "Camels travel across the hot sandy desert."),
            ("stream", "/striːm/", "n.", "con suối nhỏ", "Crystal clear water babbles in the mountain stream."),
            ("waterfall", "/ˈwɑː.t̬ɚ.fɑːl/", "n.", "thác nước hùng vĩ", "Mist rises from the roaring waterfall."),
            ("cave", "/keɪv/", "n.", "hang động bí ẩn", "Son Doong is the largest natural cave in the world."),
            ("cliff", "/klɪf/", "n.", "vách đá dựng đứng", "Seabirds nest safely on the rocky cliff."),
            ("breeze", "/briːz/", "n.", "ngọn gió mát dịu", "A gentle sea breeze cooled the afternoon heat."),
            ("storm", "/stɔːrm/", "n.", "cơn bão giông", "Stay indoors during the severe thunderstorm."),
            ("thunder", "/ˈθʌn.dɚ/", "n.", "tiếng sấm sét rền vang", "Loud thunder rolled across the dark sky."),
            ("lightning", "/ˈlaɪt.nɪŋ/", "n.", "tia chớp chói lòa", "A flash of lightning illuminated the clouds."),
            ("fog", "/fɑːɡ/", "n.", "màn sương mù", "Morning fog blanketed the quiet valley."),
            ("rainbow", "/ˈreɪn.boʊ/", "n.", "cầu vồng rực rỡ", "A vibrant rainbow appeared after the sudden rain."),
            ("dawn", "/dɑːn/", "n.", "bình minh hửng sáng", "Fishermen set sail at early dawn."),
            ("dusk", "/dʌsk/", "n.", "hoàng hôn chạng vạng", "Streetlights flicker on at tranquil dusk."),
        ])
    ]

    for topic_name, word_list in additional_pools:
        for w, ipa, pos, meaning, ex in word_list:
            if len(result) >= 1000:
                break
            w_clean = w.lower().strip()
            if w_clean not in seen:
                seen.add(w_clean)
                result.append({
                    "word": w_clean,
                    "ipa": ipa,
                    "pos": pos,
                    "meaning": meaning,
                    "example": ex,
                    "topic": topic_name
                })
        if len(result) >= 1000:
            break

    # If still below 1000, add remaining common adjectives and adverbs
    extra_common = [
        ("almost", "/ˈɑːl.moʊst/", "adv.", "hầu như, gần như", "I have almost finished my homework.", "Trạng từ mức độ"),
        ("already", "/ɑːlˈred.i/", "adv.", "đã... rồi", "She has already left the office.", "Trạng từ thời gian"),
        ("enough", "/ɪˈnʌf/", "adj., adv.", "đủ đầy", "Do you have enough time to finish?", "Từ định lượng"),
        ("especially", "/ɪˈspeʃ.əl.i/", "adv.", "đặc biệt là", "I love fruit, especially mangoes.", "Trạng từ nhấn mạnh"),
        ("probably", "/ˈprɑː.bə.bli/", "adv.", "có lẽ, có thể", "It will probably rain this evening.", "Trạng từ phỏng đoán"),
        ("together", "/təˈɡeð.ɚ/", "adv.", "cùng nhau", "We work together as a team.", "Trạng từ cách thức"),
        ("suddenly", "/ˈsʌd.ən.li/", "adv.", "đột ngột", "Suddenly, the electricity went out.", "Trạng từ cách thức"),
        ("finally", "/ˈfaɪ.nəl.i/", "adv.", "cuối cùng thì", "We finally arrived at our destination.", "Trạng từ liên kết"),
        ("certainly", "/ˈsɜːr.tən.li/", "adv.", "chắc chắn rồi", "I will certainly help you with pronunciation.", "Trạng từ khẳng định"),
        ("completely", "/kəmˈpliːt.li/", "adv.", "hoàn toàn", "I completely agree with your suggestion.", "Trạng từ mức độ"),
        ("simple", "/ˈsɪm.pəl/", "adj.", "đơn giản", "Keep your sentences simple and clear.", "Tính từ mô tả"),
        ("complex", "/kɑːmˈpleks/", "adj.", "phức tạp", "Break down complex words into syllables.", "Tính từ mô tả"),
        ("modern", "/ˈmɑː.dɚn/", "adj.", "hiện đại", "Our city has modern infrastructure.", "Tính từ mô tả"),
        ("ancient", "/ˈeɪn.ʃənt/", "adj.", "cổ kính", "Visit the ancient temple in the village.", "Tính từ mô tả"),
        ("famous", "/ˈfeɪ.məs/", "adj.", "nổi tiếng", "Ha Long Bay is famous worldwide.", "Tính từ phẩm chất"),
        ("popular", "/ˈpɑː.pjə.lɚ/", "adj.", "phổ biến, được ưa thích", "Soccer is a popular sport in Vietnam.", "Tính từ phẩm chất"),
        ("special", "/ˈspeʃ.əl/", "adj.", "đặc biệt", "Today is a special celebration.", "Tính từ phẩm chất"),
        ("ordinary", "/ˈɔːr.dən.er.i/", "adj.", "bình thường", "It was an ordinary Tuesday afternoon.", "Tính từ mô tả"),
        ("perfect", "/ˈpɝː.fekt/", "adj.", "hoàn hảo", "Practice makes perfect.", "Tính từ phẩm chất"),
        ("correct", "/kəˈrekt/", "adj., v.", "chính xác; sửa đúng", "Your pronunciation is absolutely correct.", "Tính từ phẩm chất"),
        ("accurate", "/ˈæk.jɚ.ət/", "adj.", "chuẩn xác rành mạch", "Use an accurate IPA dictionary.", "Tính từ phẩm chất"),
        ("fluent", "/ˈfluː.ənt/", "adj.", "lưu loát, trôi chảy", "Daily practice makes you a fluent speaker.", "Tính từ phẩm chất"),
        ("effective", "/əˈfek.tɪv/", "adj.", "hiệu quả cao", "Flashcards are an effective study tool.", "Tính từ phẩm chất"),
        ("creative", "/kriˈeɪ.t̬ɪv/", "adj.", "sáng tạo", "She showed a creative approach to art.", "Tính từ tính cách"),
        ("helpful", "/ˈhelp.fəl/", "adj.", "hữu ích, nhiệt tình", "The tutor gave very helpful advice.", "Tính từ tính cách"),
        ("valuable", "/ˈvæl.jə.bəl/", "adj.", "quý giá", "Time is our most valuable asset.", "Tính từ phẩm chất"),
        ("bright", "/braɪt/", "adj.", "tươi sáng, thông minh", "A bright smile welcomes every guest.", "Tính từ mô tả"),
        ("smooth", "/smuːð/", "adj.", "êm dịu, mượt mà", "Her voice sounds smooth and natural.", "Tính từ mô tả"),
        ("rough", "/rʌf/", "adj.", "gồ ghề; thô ráp", "The boat sailed through rough waters.", "Tính từ mô tả"),
        ("sharp", "/ʃɑːrp/", "adj.", "sắc bén; nhạy bén", "He has a sharp mind for puzzles.", "Tính từ mô tả"),
        ("dull", "/dʌl/", "adj.", "cùn; tẻ nhạt", "The movie was dull and sleepy.", "Tính từ mô tả"),
        ("loud", "/laʊd/", "adj., adv.", "to tiếng", "Speak in a clear, loud voice.", "Tính từ mô tả"),
        ("silent", "/ˈsaɪ.lənt/", "adj.", "im lặng, thanh tịnh", "The library remained quiet and silent.", "Tính từ mô tả"),
        ("deep", "/diːp/", "adj.", "sâu thẳm", "Take a deep breath before speaking.", "Tính từ mô tả"),
        ("shallow", "/ˈʃæl.oʊ/", "adj.", "nông cạn", "Wade in the shallow water.", "Tính từ mô tả"),
        ("wide", "/waɪd/", "adj.", "rộng rãi", "Open your mouth wide for the /æ/ vowel.", "Tính từ mô tả"),
        ("narrow", "/ˈner.oʊ/", "adj.", "hẹp", "The lane is too narrow for two cars.", "Tính từ mô tả"),
        ("thick", "/θɪk/", "adj.", "dày dặn", "Wear a thick winter coat today.", "Tính từ mô tả"),
        ("thin", "/θɪn/", "adj.", "mỏng manh; gầy", "Slice the bread into thin pieces.", "Tính từ mô tả"),
        ("rich", "/rɪtʃ/", "adj.", "giàu có; đậm đà", "Vietnam is rich in cultural heritage.", "Tính từ mô tả"),
        ("poor", "/pʊr/", "adj.", "nghèo nàn; tội nghiệp", "Poor pronunciation leads to misunderstandings.", "Tính từ mô tả"),
        ("safe", "/seɪf/", "adj.", "an toàn", "Wear a helmet to stay safe.", "Tính từ tính chất"),
        ("dangerous", "/ˈdeɪn.dʒɚ.əs/", "adj.", "nguy hiểm", "Driving too fast is dangerous.", "Tính từ tính chất"),
        ("clean", "/kliːn/", "adj., v.", "sạch sẽ", "Keep the classroom clean and tidy.", "Tính từ mô tả"),
        ("dirty", "/ˈdɝː.t̬i/", "adj.", "bẩn thỉu", "Wash dirty hands with warm water.", "Tính từ mô tả"),
        ("fresh", "/freʃ/", "adj.", "tươi mới", "Eat fresh vegetables every day.", "Tính từ mô tả"),
        ("sweet", "/swiːt/", "adj.", "ngọt ngào", "Honey tastes naturally sweet.", "Tính từ vị giác"),
        ("sour", "/saʊər/", "adj.", "chua gắt", "Lemons have a sour refreshing taste.", "Tính từ vị giác"),
        ("bitter", "/ˈbɪt̬.ɚ/", "adj.", "đắng ngắt", "Dark chocolate has a pleasant bitter taste.", "Tính từ vị giác"),
        ("salty", "/ˈsɑːl.t̬i/", "adj.", "mặn mà", "Do not add too much salty fish sauce.", "Tính từ vị giác"),
        ("soft", "/sɑːft/", "adj.", "mềm mại; êm ái", "A soft pillow gives sweet dreams.", "Tính từ cảm giác"),
        ("hard", "/hɑːrd/", "adj., adv.", "cứng; chăm chỉ", "Work hard to achieve your dreams.", "Tính từ tính chất"),
        ("light", "/laɪt/", "adj., n.", "nhẹ nhàng; ánh sáng", "A light backpack is easy to carry.", "Tính từ tính chất"),
        ("heavy", "/ˈhev.i/", "adj.", "nặng nề", "Lift heavy boxes with caution.", "Tính từ tính chất"),
        ("true", "/truː/", "adj.", "đúng đắn, thật sự", "A true friend is always supportive.", "Tính từ tính chất"),
        ("false", "/fɑːls/", "adj.", "sai lệch", "Check whether the statement is true or false.", "Tính từ tính chất"),
        ("honest", "/ˈɑː.nɪst/", "adj.", "thành thật, chính trực", "An honest student never cheats on exams.", "Tính từ tính cách"),
        ("polite", "/pəˈlaɪt/", "adj.", "lịch thiệp, nhã nhặn", "Always say 'please' to be polite.", "Tính từ tính cách"),
        ("rude", "/ruːd/", "adj.", "thô lỗ, mất lịch sự", "Interrupting others is considered rude.", "Tính từ tính cách"),
        ("smile", "/smaɪl/", "v., n.", "mỉm cười; nụ cười", "Smile when you greet others.", "Hành động & Biểu cảm"),
        ("laugh", "/læf/", "v., n.", "cười lớn; tiếng cười", "The comedy made everyone laugh.", "Hành động & Biểu cảm"),
        ("cry", "/kraɪ/", "v., n.", "khóc; tiếng khóc", "Do not cry over small matters.", "Hành động & Biểu cảm"),
        ("shout", "/ʃaʊt/", "v., n.", "la hét, quát to", "Do not shout in the quiet library.", "Hành động & Biểu cảm"),
        ("whisper", "/ˈwɪs.pɚ/", "v., n.", "thì thầm, nói nhỏ", "She whispered the secret in my ear.", "Hành động & Biểu cảm"),
        ("climb", "/klaɪm/", "v.", "leo trèo, leo núi", "Climb the mountain with safe boots.", "Vận động & Thể chất"),
        ("fall", "/fɑːl/", "v., n.", "ngã, rơi; mùa thu", "Leaves fall gently in autumn.", "Vận động & Thể chất"),
        ("lift", "/lɪft/", "v., n.", "nâng lên; thang máy", "Lift weights with proper posture.", "Vận động & Thể chất"),
        ("throw", "/θroʊ/", "v.", "ném, quăng", "Throw the ball to your teammate.", "Vận động & Thể chất"),
        ("catch", "/kætʃ/", "v.", "bắt lấy, đón lấy", "Catch the train on platform two.", "Vận động & Thể chất"),
        ("release", "/rɪˈliːs/", "v., n.", "thả ra; phát hành", "Release your stress through meditation.", "Hành động & Tâm lý"),
        ("repair", "/rɪˈper/", "v., n.", "sửa chữa, bảo trì", "Repair the broken bicycle tire.", "Hành động kỹ thuật"),
        ("build", "/bɪld/", "v.", "xây dựng, kiến tạo", "Build a solid foundation in vocabulary.", "Hành động kiến tạo"),
        ("destroy", "/dɪˈstrɔɪ/", "v.", "phá hủy, tiêu diệt", "Do not destroy the natural habitat.", "Hành động & Tự nhiên"),
        ("create", "/kriˈeɪt/", "v.", "tạo ra, sáng tạo", "Create an enjoyable study routine.", "Hành động kiến tạo"),
        ("invent", "/ɪnˈvent/", "v.", "phát minh", "Scientists invent helpful technologies.", "Khoa học & Đổi mới"),
        ("discover", "/dɪˈskʌv.ɚ/", "v.", "khám phá, tìm ra", "Discover new English expressions.", "Học tập & Khám phá"),
        ("explore", "/ɪkˈsplɔːr/", "v.", "thám hiểm, tìm hiểu", "Explore the beautiful old city.", "Du lịch & Khám phá"),
        ("search", "/sɜːrtʃ/", "v., n.", "tìm kiếm, tra cứu", "Search for the word in the dictionary.", "Tra cứu & Công nghệ"),
        ("find", "/faɪnd/", "v.", "tìm thấy", "I hope you find your lost keys.", "Hành động thường nhật"),
        ("lose", "/luːz/", "v.", "đánh mất, thua cuộc", "Never lose hope in difficult times.", "Hành động thường nhật"),
        ("hide", "/haɪd/", "v.", "trốn, giấu kín", "The shy cat hides under the bed.", "Hành động thường nhật"),
        ("show", "/ʃoʊ/", "v., n.", "cho xem; buổi biểu diễn", "Show me your pronunciation homework.", "Giao tiếp & Chia sẻ"),
        ("cover", "/ˈkʌv.ɚ/", "v., n.", "che phủ; bìa sách", "Cover the dish to keep it warm.", "Hành động thường nhật"),
        ("reveal", "/rɪˈviːl/", "v.", "tiết lộ, hé lộ", "The results reveal steady progress.", "Giao tiếp & Chia sẻ"),
        ("lock", "/lɑːk/", "v., n.", "khóa cửa; ổ khóa", "Lock the front door before sleeping.", "An ninh gia đình"),
        ("unlock", "/ʌnˈlɑːk/", "v.", "mở khóa", "Unlock the door with your smart card.", "An ninh gia đình"),
        ("start", "/stɑːrt/", "v., n.", "bắt đầu, khởi đầu", "Let's start Day 01 together.", "Hành trình học tập"),
        ("begin", "/bɪˈɡɪn/", "v.", "bắt đầu", "A new journey begins today.", "Hành trình học tập"),
        ("continue", "/kənˈtɪn.juː/", "v.", "tiếp tục, duy trì", "Continue practicing every single day.", "Học tập kiên trì"),
        ("pause", "/pɑːz/", "v., n.", "tạm dừng", "Pause the audio to repeat the phrase.", "Học tập & Tương tác"),
        ("cancel", "/ˈkæn.səl/", "v.", "hủy bỏ", "Cancel the booking free of charge.", "Dịch vụ & Giao dịch"),
        ("change", "/tʃeɪndʒ/", "v., n.", "thay đổi; tiền lẻ", "Small daily habits change your life.", "Phát triển bản thân"),
        ("improve", "/ɪmˈpruːv/", "v.", "cải thiện, tiến bộ", "Shadowing will improve your accent.", "Phát triển bản thân"),
        ("develop", "/dɪˈvel.əp/", "v.", "phát triển, mở rộng", "Develop strong listening reflexes.", "Phát triển bản thân"),
        ("grow", "/ɡroʊ/", "v.", "lớn lên, phát triển", "Plants grow fast in the spring rain.", "Thiên nhiên & Phát triển"),
        ("connect", "/kəˈnekt/", "v.", "kết nối", "Connect your microphone to start talking.", "Công nghệ & Giao tiếp"),
        ("disconnect", "/ˌdɪs.kəˈnekt/", "v.", "ngắt kết nối", "Disconnect the charger when battery is full.", "Công nghệ & Giao dịch"),
        ("combine", "/kəmˈbaɪn/", "v.", "kết hợp, phối hợp", "Combine audio listening with speaking.", "Phương pháp học"),
        ("separate", "/ˈsep.ər.eɪt/", "v., adj.", "tách rời, riêng biệt", "Separate syllables when pronouncing long words.", "Phương pháp học"),
        ("divide", "/dɪˈvaɪd/", "v.", "chia nhỏ, phân chia", "Divide your study time into 15-minute blocks.", "Phương pháp học"),
        ("calculate", "/ˈkæl.kjə.leɪt/", "v.", "tính toán", "Calculate the total cost before shopping.", "Tư duy & Số học"),
        ("measure", "/ˈmeʒ.ɚ/", "v., n.", "đo lường; biện pháp", "Measure your speaking fluency regularly.", "Tư duy & Đánh giá"),
        ("weigh", "/weɪ/", "v.", "cân trọng lượng", "Weigh your luggage before the flight.", "Du lịch & Số lượng"),
        ("count", "/kaʊnt/", "v.", "đếm số lượng", "Count your blessings every day.", "Thái độ sống"),
        ("add", "/æd/", "v.", "thêm vào, bổ sung", "Add fresh lemon to your tea.", "Hành động thường nhật"),
        ("subtract", "/səbˈtrækt/", "v.", "trừ đi, bớt", "Subtract the discount from the total price.", "Tư duy & Mua sắm"),
        ("trust", "/trʌst/", "v., n.", "tin cậy; lòng tin", "Trust the process of language learning.", "Tâm lý & Quan hệ"),
        ("respect", "/rɪˈspekt/", "v., n.", "tôn trọng, kính trọng", "Respect your teacher and classmates.", "Đạo đức & Quan hệ"),
        ("admire", "/ədˈmaɪr/", "v.", "ngưỡng mộ, khâm phục", "I admire your dedication to learning.", "Tâm lý & Cảm xúc"),
        ("encourage", "/ɪnˈkɝː.ɪdʒ/", "v.", "động viên, khích lệ", "Teachers encourage students to speak out.", "Giáo dục & Động lực"),
        ("inspire", "/ɪnˈspaɪr/", "v.", "truyền cảm hứng", "Great stories inspire young minds.", "Giáo dục & Động lực"),
        ("motivate", "/ˈmoʊ.t̬ə.veɪt/", "v.", "tạo động lực phấn đấu", "Set clear goals to motivate yourself.", "Giáo dục & Động lực"),
        ("celebrate", "/ˈsel.ə.breɪt/", "v.", "ăn mừng, kỷ niệm", "Celebrate every small milestone you reach.", "Thành quả & Niềm vui"),
        ("congratulate", "/kənˈɡrætʃ.ə.leɪt/", "v.", "chúc mừng", "I congratulate you on finishing 100 days!", "Giao tiếp lịch thiệp"),
        ("appreciate", "/əˈpriː.ʃi.eɪt/", "v.", "trân trọng, cảm kích", "I appreciate your patient feedback.", "Giao tiếp lịch thiệp"),
        ("apologize", "/əˈpɑː.lə.dʒaɪz/", "v.", "xin lỗi chân thành", "Apologize when you arrive late.", "Giao tiếp lịch thiệp"),
        ("forgive", "/fɚˈɡɪv/", "v.", "tha thứ, bỏ qua", "Forgive yourself for making speaking mistakes.", "Thái độ học tập"),
        ("promise", "/ˈprɑː.mɪs/", "v., n.", "hứa hẹn; lời hứa", "I promise to practice 10 words daily.", "Cam kết học tập"),
        ("remind", "/rɪˈmaɪnd/", "v.", "nhắc nhở", "Set an alarm to remind your study hour.", "Thói quen học tập"),
        ("suggest", "/səɡˈdʒest/", "v.", "gợi ý, đề xuất", "Can you suggest a good English podcast?", "Giao tiếp & Tư vấn"),
        ("recommend", "/ˌrek.əˈmend/", "v.", "giới thiệu, khuyên dùng", "I recommend this vocabulary roadmap.", "Giao tiếp & Tư vấn"),
        ("inform", "/ɪnˈfɔːrm/", "v.", "thông báo, cho hay", "Inform your tutor if you need to slow down.", "Giao tiếp lớp học"),
        ("confirm", "/kənˈfɝːm/", "v.", "xác nhận lại", "Confirm your attendance before Monday.", "Giao tiếp công việc"),
        ("participate", "/pɑːrˈtɪs.ə.peɪt/", "v.", "tham gia đóng góp", "Participate actively in conversation.", "Giao tiếp lớp học"),
        ("succeed", "/səkˈsiːd/", "v.", "thành công đạt mục tiêu", "Consistency helps you succeed in English.", "Thành tựu & Đích đến"),
        ("conclude", "/kənˈkluːd/", "v.", "kết luận, kết thúc", "Let's conclude today's productive lesson.", "Học tập & Tổng kết"),
    ]

    for item in extra_common:
        if len(result) >= 1000:
            break
        w_clean = item[0].lower().strip()
        if w_clean not in seen:
            seen.add(w_clean)
            result.append({
                "word": w_clean,
                "ipa": item[1],
                "pos": item[2],
                "meaning": item[3],
                "example": item[4],
                "topic": item[5]
            })

    # Cut off at exactly 1000 items
    result = result[:1000]
    assert len(result) == 1000, f"Expected 1000 words but got {len(result)}"
    print(f"Final curated count: {len(result)} words!")
    return result

def write_upgraded_workbook(words_1000, target_path):
    wb = openpyxl.Workbook()
    # Remove default sheet
    wb.remove(wb.active)

    # 1. Sheet 1: Lộ trình 1000 từ cốt lõi
    ws1 = wb.create_sheet(title="Lộ trình 1000 từ cốt lõi")
    
    # Headers
    headers1 = [
        "STT", 
        "Ngày học", 
        "Chủ đề", 
        "Từ vựng", 
        "Phiên âm IPA", 
        "Từ loại", 
        "Nghĩa tiếng Việt", 
        "Ví dụ câu ngắn", 
        "Đã học"
    ]
    ws1.append(headers1)

    # Style Header
    header_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    thin_border = Border(
        left=Side(style='thin', color='D9D9D9'),
        right=Side(style='thin', color='D9D9D9'),
        top=Side(style='thin', color='D9D9D9'),
        bottom=Side(style='thin', color='D9D9D9')
    )

    for col_idx, h in enumerate(headers1, start=1):
        cell = ws1.cell(row=1, column=col_idx)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    ws1.row_dimensions[1].height = 28

    # Populate 1000 words into 100 days (10 words/day)
    # Default first 80 words as TRUE (marked as learned), rest as FALSE
    for i, w in enumerate(words_1000, start=1):
        day_num = ((i - 1) // 10) + 1
        day_str = f"Ngày {day_num:02d}"
        is_learned = True if i <= 100 else False
        
        row_vals = [
            i,
            day_str,
            w["topic"],
            w["word"],
            w["ipa"],
            w["pos"],
            w["meaning"],
            w["example"],
            is_learned
        ]
        ws1.append(row_vals)
        
        row_idx = i + 1
        # Zebra striping for readability
        zebra_fill = PatternFill(start_color="F9FAFB", end_color="F9FAFB", fill_type="solid") if i % 2 == 0 else PatternFill(fill_type=None)
        
        for col_idx in range(1, 10):
            c = ws1.cell(row=row_idx, column=col_idx)
            c.border = thin_border
            if zebra_fill.fill_type:
                c.fill = zebra_fill
            if col_idx in [1, 2, 6, 9]:
                c.alignment = Alignment(horizontal="center", vertical="center")
            elif col_idx in [4, 5]:
                c.alignment = Alignment(horizontal="left", vertical="center")
                if col_idx == 4:
                    c.font = Font(bold=True)
            else:
                c.alignment = Alignment(horizontal="left", vertical="center")

    # Enable filter on Header
    ws1.auto_filter.ref = f"A1:I{len(words_1000) + 1}"

    # Auto column width
    for col in ws1.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws1.column_dimensions[col_letter].width = max(max_len + 3, 10)

    # 2. Sheet 2: Luyen_Dich_Passages
    ws2 = wb.create_sheet(title="Luyen_Dich_Passages")
    headers2 = [
        "Thời gian sinh",
        "Các từ đã học được sử dụng",
        "Đoạn văn tiếng Anh (2-3 câu)",
        "Bản dịch gợi ý tiếng Việt",
        "Bản dịch thực hành của tôi"
    ]
    ws2.append(headers2)

    header2_fill = PatternFill(start_color="2C3E50", end_color="2C3E50", fill_type="solid")
    for col_idx, h in enumerate(headers2, start=1):
        cell = ws2.cell(row=1, column=col_idx)
        cell.fill = header2_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")

    ws2.row_dimensions[1].height = 26
    ws2.column_dimensions['A'].width = 22
    ws2.column_dimensions['B'].width = 30
    ws2.column_dimensions['C'].width = 50
    ws2.column_dimensions['D'].width = 50
    ws2.column_dimensions['E'].width = 50

    # Add a sample introductory row
    ws2.append([
        "2026-11-01 16:30:00",
        "hello, friend, welcome, learn",
        "Hello my friend! Welcome to our English class. We will learn new words together.",
        "Xin chào người bạn của tôi! Chào mừng bạn đến với lớp học tiếng Anh. Chúng ta sẽ cùng nhau học các từ mới.",
        "Xin chào bạn tôi! Chào mừng tới lớp học tiếng Anh. Chúng ta sẽ cùng học từ mới."
    ])

    wb.save(target_path)
    print(f"Successfully saved 1000-word workbook with 2 sheets to: {target_path}")

def run():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, ".."))
    data_dir = os.path.join(project_root, "data")
    os.makedirs(data_dir, exist_ok=True)

    candidates = [
        os.path.join(data_dir, "1000_core_words_curriculum.xlsx"),
        "d:\\el\\1000_core_words_curriculum.xlsx",
        "d:\\el\\Lo_Trinh_80_Ngay_560_Tu_Vung_Phat_Am_Co_Ban.xlsx",
    ]
    existing_file = None
    for c in candidates:
        if os.path.exists(c):
            existing_file = c
            break

    if not existing_file:
        matches = glob.glob(os.path.join(data_dir, "*.xlsx")) or glob.glob("d:\\el\\*Lo_Trinh*.xlsx")
        if matches:
            existing_file = matches[0]

    existing_words = get_existing_words(existing_file) if existing_file else []
    words_1000 = generate_1000_list(existing_words)
    
    # Save to primary data/ directory
    primary_target = os.path.join(data_dir, "1000_core_words_curriculum.xlsx")
    write_upgraded_workbook(words_1000, primary_target)

    # Save to external folder if exists
    if os.path.exists("d:\\el"):
        write_upgraded_workbook(words_1000, "d:\\el\\1000_core_words_curriculum.xlsx")

    print(f"Excel upgrade completed successfully! Primary saved to: {primary_target}")

if __name__ == "__main__":
    run()
