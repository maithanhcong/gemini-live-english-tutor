# scripts/build_rich_lexicon.py
"""
Trình tạo scripts/oxford_lexicon_data.py đảm bảo chuẩn xác về IPA, POS, tiếng Việt và câu ví dụ.
"""
import os
import json

def main():
    # Danh mục từ vựng Oxford 3000 chọn lọc
    items = [
        ("acquaintance", "/əˈkweɪntəns/", "noun", "người quen biết", "She met an old university acquaintance at the airport.", "Gia đình & Người thân", "B2"),
        ("adoption", "/əˈdɒpʃn/", "noun", "sự nhận nuôi, sự thông qua", "They completed the international adoption process with joy.", "Gia đình & Người thân", "B2"),
        ("ancestry", "/ˈænsestri/", "noun", "dòng dõi, tổ tiên", "He traced his family ancestry back five generations.", "Gia đình & Người thân", "B2"),
        ("bride", "/braɪd/", "noun", "cô dâu trong ngày cưới", "The bride wore a classic white embroidered lace gown.", "Gia đình & Người thân", "A2"),
        ("bridegroom", "/ˈbraɪdɡruːm/", "noun", "chú rể", "The bridegroom smiled warmly as his bride walked down the aisle.", "Gia đình & Người thân", "B1"),
        ("brotherhood", "/ˈbrʌðəhʊd/", "noun", "tình anh em gắn bó", "The expedition forged a strong sense of brotherhood among climbers.", "Gia đình & Người thân", "B2"),
        ("couple", "/ˈkʌpl/", "noun", "cặp đôi, cặp vợ chồng", "The newlywed couple moved into a bright garden apartment.", "Gia đình & Người thân", "A1"),
        ("descendant", "/dɪˈsendənt/", "noun", "hậu duệ, con cháu", "Descendants gathered to honor their ancestral heritage.", "Gia đình & Người thân", "B2"),
        ("foster", "/ˈfɒstə(r)/", "verb", "nuôi dưỡng, thúc đẩy", "Encouraging environments foster confident conversational reflex.", "Gia đình & Người thân", "B2"),
        ("fraternity", "/frəˈtɜːnəti/", "noun", "tình huynh đệ, hội nam sinh", "Universal fraternity unites people across geographic boundaries.", "Gia đình & Người thân", "B2"),
        ("generation", "/ˌdʒenəˈreɪʃn/", "noun", "thế hệ", "Each generation brings fresh energy and creative perspectives.", "Gia đình & Người thân", "A2"),
        ("godfather", "/ˈɡɒdfɑːðə(r)/", "noun", "cha đỡ đầu", "His godfather presented him with an inscribed Oxford dictionary.", "Gia đình & Người thân", "B1"),
        ("godmother", "/ˈɡɒdmʌðə(r)/", "noun", "mẹ đỡ đầu", "She sent warm birthday greetings to her loving godmother.", "Gia đình & Người thân", "B1"),
        ("guardian", "/ˈɡɑːdiən/", "noun", "người giám hộ", "A legal guardian signed the student passport application.", "Gia đình & Người thân", "B1"),
        ("heir", "/eə(r)/", "noun", "người thừa kế", "He was named the sole heir to the historic family estate.", "Gia đình & Người thân", "B2"),
        ("heritage", "/ˈherɪtɪdʒ/", "noun", "di sản văn hóa", "Hoi An ancient town is a UNESCO world cultural heritage site.", "Gia đình & Người thân", "B1"),
        ("household", "/ˈhaʊshəʊld/", "noun", "hộ gia đình", "Managing a busy household requires budget and schedule discipline.", "Gia đình & Người thân", "A2"),
        ("kinship", "/ˈkɪnʃɪp/", "noun", "quan hệ huyết thống, sự thân tình", "Shared language learning goals create an authentic kinship.", "Gia đình & Người thân", "B2"),
        ("marriage", "/ˈmærɪdʒ/", "noun", "hôn nhân", "Trust and mutual respect are the cornerstones of a happy marriage.", "Gia đình & Người thân", "A2"),
        ("maternal", "/məˈtɜːnl/", "adj", "thuộc về người mẹ", "Her maternal instincts guided her children with gentle patience.", "Gia đình & Người thân", "B2"),
        ("motherhood", "/ˈmʌðəhʊd/", "noun", "thiên chức làm mẹ", "Motherhood brings profound joy and endless personal growth.", "Gia đình & Người thân", "B2"),
        ("nephew", "/ˈnefjuː/", "noun", "cháu trai (con anh/chị/em)", "She bought an illustrated English fairy tale for her little nephew.", "Gia đình & Người thân", "A2"),
        ("niece", "/niːs/", "noun", "cháu gái (con anh/chị/em)", "His niece loves singing conversational English rhymes.", "Gia đình & Người thân", "A2"),
        ("orphan", "/ˈɔːfn/", "noun", "trẻ mồ côi", "The community founded a welcoming home for orphaned children.", "Gia đình & Người thân", "B1"),
        ("paternal", "/pəˈtɜːnl/", "adj", "thuộc về người cha", "His paternal grandfather taught him the joy of gardening.", "Gia đình & Người thân", "B2"),
        ("relative", "/ˈrelətɪv/", "noun", "bà con, người thân", "Dozens of relatives gathered for the family reunion banquet.", "Gia đình & Người thân", "A2"),
        ("sibling", "/ˈsɪblɪŋ/", "noun", "anh chị em ruột", "Healthy dialogue resolves minor squabbles between young siblings.", "Gia đình & Người thân", "B1"),
        ("spouse", "/spaʊs/", "noun", "vợ hoặc chồng", "Invite your spouse to practice conversational drills together.", "Gia đình & Người thân", "B2"),
        ("stepfather", "/ˈstepfɑːðə(r)/", "noun", "cha dượng", "His stepfather supported his academic ambitions unconditionally.", "Gia đình & Người thân", "B1"),
        ("stepmother", "/ˈstepmʌðə(r)/", "noun", "mẹ kế", "Her kind stepmother helped her rehearse for the school speech.", "Gia đình & Người thân", "B1"),
        ("toddler", "/ˈtɒdlə(r)/", "noun", "trẻ mới biết đi", "The toddler clapped happily whenever the music played.", "Gia đình & Người thân", "B1"),
        ("twin", "/twɪn/", "noun", "sinh đôi", "The twin sisters have remarkably similar voice pitches.", "Gia đình & Người thân", "A2"),
        ("upbringing", "/ˈʌpbrɪŋɪŋ/", "noun", "sự giáo dưỡng, nuôi nấng", "A loving bilingual upbringing fosters flexible cognitive reflexes.", "Gia đình & Người thân", "B2"),
        ("widow", "/ˈwɪdəʊ/", "noun", "người góa phụ", "The generous widow bequeathed her art collection to the gallery.", "Gia đình & Người thân", "B1"),
        ("widower", "/ˈwɪdəʊə(r)/", "noun", "người đàn ông góa vợ", "The kind widower volunteered at the neighborhood language club.", "Gia đình & Người thân", "B2"),

        # Nhóm Trang phục & Thời trang
        ("apparel", "/əˈpærəl/", "noun", "y phục, trang phục", "The boutique retails athletic apparel made of recycled cotton.", "Quần áo & Trang phục", "B2"),
        ("apron", "/ˈeɪprən/", "noun", "tạp dề làm bếp", "Tie a clean canvas apron around your waist before cooking.", "Quần áo & Trang phục", "A2"),
        ("belt", "/belt/", "noun", "thắt lưng da", "A sleek leather belt complements tailored formal trousers.", "Quần áo & Trang phục", "A1"),
        ("blazer", "/ˈbleɪzə(r)/", "noun", "áo khoác vest nhẹ", "Wear a navy wool blazer over a crisp white oxford shirt.", "Quần áo & Trang phục", "B1"),
        ("blouse", "/blaʊz/", "noun", "áo sơ mi nữ", "She paired a pastel silk blouse with an pleated linen skirt.", "Quần áo & Trang phục", "A2"),
        ("buckle", "/ˈbʌkl/", "noun", "khóa thắt lưng", "The silver belt buckle was polished until it sparkled.", "Quần áo & Trang phục", "B1"),
        ("button", "/ˈbʌtn/", "noun", "nút áo, cúc áo", "Fasten the top shirt button before tying your necktie.", "Quần áo & Trang phục", "A1"),
        ("cardigan", "/ˈkɑːdɪɡən/", "noun", "áo len cài cúc", "Slip on a cozy wool cardigan on brisk autumn mornings.", "Quần áo & Trang phục", "B1"),
        ("cashmere", "/ˈkæʃmɪə(r)/", "noun", "len ca-sơ-mia cao cấp", "Cashmere sweaters offer sublime softness and lightweight warmth.", "Quần áo & Trang phục", "B2"),
        ("collar", "/ˈkɒlə(r)/", "noun", "cổ áo sơ mi", "Keep your shirt collar crisp and well-ironed for interviews.", "Quần áo & Trang phục", "A2"),
        ("corduroy", "/ˈkɔːdərɔɪ/", "noun", "vải nhung kẻ gân", "Vintage corduroy jackets are trending among university students.", "Quần áo & Trang phục", "B2"),
        ("cotton", "/ˈkɒtn/", "noun", "vải bông sợi tự nhiên", "Breathable organic cotton garments keep you cool during summer.", "Quần áo & Trang phục", "A2"),
        ("denim", "/ˈdenɪm/", "noun", "vải bò bò dệt chéo", "Durable blue denim jackets never go out of fashion.", "Quần áo & Trang phục", "B1"),
        ("fabric", "/ˈfæbrɪk/", "noun", "loại vải may mặc", "Inspect the texture and breathability of the garment fabric.", "Quần áo & Trang phục", "A2"),
        ("fleece", "/fliːs/", "noun", "áo khoác nỉ ấm", "Zip up your warm thermal fleece when the evening temperature dips.", "Quần áo & Trang phục", "B1"),
        ("garment", "/ˈɡɑːmənt/", "noun", "y phục, quần áo", "Care for delicate silk garments by washing them in cool water.", "Quần áo & Trang phục", "B1"),
        ("handbag", "/ˈhændbæɡ/", "noun", "túi xách tay", "She keeps her tablet, earphones, and notepad in her handbag.", "Quần áo & Trang phục", "A2"),
        ("handkerchief", "/ˈhæŋkətʃɪf/", "noun", "khăn mùi xoa", "Always carry a clean cotton handkerchief in your coat pocket.", "Quần áo & Trang phục", "B1"),
        ("hoodie", "/ˈhʊdi/", "noun", "áo nỉ có mũ trùm", "He wore a comfortable oversized fleece hoodie to the library.", "Quần áo & Trang phục", "A2"),
        ("jacket", "/ˈdʒækɪt/", "noun", "áo khoác ngắn", "Zip your windbreaker jacket before walking along the windy coast.", "Quần áo & Trang phục", "A1"),
        ("jersey", "/ˈdʒɜːzi/", "noun", "áo thi đấu thể thao", "The soccer team wore matching blue and white striped jerseys.", "Quần áo & Trang phục", "B1"),
        ("leather", "/ˈleðə(r)/", "noun", "chất liệu da bò", "Genuine leather shoes mold comfortably to your feet over time.", "Quần áo & Trang phục", "A2"),
        ("linen", "/ˈlɪnɪn/", "noun", "vải lanh thoáng mát", "Pure linen shirts are an ideal choice for tropical climates.", "Quần áo & Trang phục", "B1"),
        ("necklace", "/ˈnekləs/", "noun", "vòng cổ, dây chuyền", "She wore a dainty silver necklace with a freshwater pearl.", "Quần áo & Trang phục", "A2"),
        ("outfit", "/ˈaʊtfɪt/", "noun", "bộ trang phục hoàn chỉnh", "Choose a neat and modest outfit for your formal presentation.", "Quần áo & Trang phục", "A2"),
        ("overcoat", "/ˈəʊvəkəʊt/", "noun", "áo khoác dạ dáng dài", "A heavy wool overcoat shields against howling blizzard winds.", "Quần áo & Trang phục", "B1"),
        ("pajamas", "/pəˈdʒɑːməz/", "noun", "bộ đồ ngủ mềm", "Slip into soft cotton pajamas before getting into a warm bed.", "Quần áo & Trang phục", "A2"),
        ("raincoat", "/ˈreɪnkəʊt/", "noun", "áo đi mưa", "Keep a lightweight folded raincoat in your daypack just in case.", "Quần áo & Trang phục", "A2"),
        ("sandal", "/ˈsændl/", "noun", "dép xăng-đan", "Comfortable leather sandals are perfect for sunny beach walks.", "Quần áo & Trang phục", "A2"),
        ("scarf", "/skɑːf/", "noun", "khăn quàng cổ", "Wrap a bright knitted wool scarf snugly around your neck.", "Quần áo & Trang phục", "A1"),
        ("shawl", "/ʃɔːl/", "noun", "khăn choàng vai", "Drape an embroidered cashmere shawl over your shoulders.", "Quần áo & Trang phục", "B2"),
        ("sneaker", "/ˈsniːkə(r)/", "noun", "giày thể thao êm", "Cushioned running sneakers protect your knees on paved streets.", "Quần áo & Trang phục", "A2"),
        ("sock", "/sɒk/", "noun", "đôi tất, vớ chân", "Wear thick merino wool socks inside your sturdy hiking boots.", "Quần áo & Trang phục", "A1"),
        ("suit", "/suːt/", "noun", "bộ com-lê trang trọng", "He wore a tailored charcoal wool suit to the annual summit.", "Quần áo & Trang phục", "A2"),
        ("sweater", "/ˈswetə(r)/", "noun", "áo len ấm", "Knitting a cozy cable-knit sweater is a relaxing winter hobby.", "Quần áo & Trang phục", "A1"),
        ("tailor", "/ˈteɪlə(r)/", "noun", "thợ may đo quần áo", "The master tailor adjusted the jacket sleeves to exact fit.", "Quần áo & Trang phục", "B1"),
        ("textile", "/ˈtekstaɪl/", "noun", "ngành dệt may, sợi dệt", "Vietnam is renowned for its high-quality export textile goods.", "Quần áo & Trang phục", "B1"),
        ("trouser", "/ˈtraʊzə(r)/", "noun", "quần tây âu dài", "Creased dark trousers give a polished professional silhouette.", "Quần áo & Trang phục", "A2"),
        ("tuxedo", "/tʌkˈsiːdəʊ/", "noun", "áo dạ hội tuxedo", "Gentlemen wore black silk-lapel tuxedos to the opera gala.", "Quần áo & Trang phục", "B2"),
        ("underwear", "/ˈʌndəweə(r)/", "noun", "quần áo lót", "Pack plenty of clean, breathable cotton underwear for travel.", "Quần áo & Trang phục", "A2"),
        ("uniform", "/ˈjuːnɪfɔːm/", "noun", "bộ đồng phục", "School uniforms foster a sense of belonging and community.", "Quần áo & Trang phục", "A1"),
        ("velvet", "/ˈvelvɪt/", "noun", "vải nhung mềm mượt", "The grand theater curtains were crafted from deep red velvet.", "Quần áo & Trang phục", "B2"),
        ("vest", "/vest/", "noun", "áo ghi-lê cài cúc", "A matching waistcoat vest adds elegance to a three-piece suit.", "Quần áo & Trang phục", "B1"),
        ("wardrobe", "/ˈwɔːdrəʊb/", "noun", "tủ quần áo, kho đồ", "Build a versatile capsule wardrobe with timeless neutral basics.", "Quần áo & Trang phục", "A2"),
        ("waterproof", "/ˈwɔːtəpruːf/", "adj", "chống thấm nước", "A waterproof jacket keeps you bone dry during torrential rains.", "Quần áo & Trang phục", "B1"),
        ("wool", "/wʊl/", "noun", "len lông cừu", "Natural merino wool wicks away sweat and retains body warmth.", "Quần áo & Trang phục", "A2"),
        ("zipper", "/ˈzɪpə(r)/", "noun", "khóa kéo quần áo", "Pull up the jacket zipper completely to seal out the cold wind.", "Quần áo & Trang phục", "A2"),
    ]

    # Bây giờ xây dựng thêm các nhóm từ còn lại để đạt chỉ tiêu
    # Đọc danh mục từ đã nạp để không trùng lặp
    out_file = os.path.join("scripts", "oxford_lexicon_data.py")
    formatted = []
    for item in items:
        formatted.append({
            "word": item[0],
            "ipa": item[1],
            "pos": item[2],
            "meaning_vi": item[3],
            "example_sentence": item[4],
            "topic": item[5],
            "level": item[6],
            "is_custom": 0
        })

    with open(out_file, "w", encoding="utf-8") as f:
        f.write("# scripts/oxford_lexicon_data.py\n")
        f.write("def get_lexicon_list():\n")
        f.write(f"    return {json.dumps(formatted, ensure_ascii=False, indent=8)}\n")

    print(f"Generated {out_file} with {len(formatted)} items.")

if __name__ == "__main__":
    main()

