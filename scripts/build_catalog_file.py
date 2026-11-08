# scripts/build_catalog_file.py
"""
Trình tạo danh mục từ điển Oxford 3000 chuẩn quốc tế để bổ sung vào scripts/oxford_full_catalog.py
"""
import os
import sys
sys.path.insert(0, os.path.abspath("."))
import json

def generate_catalog():
    # Danh mục các từ Oxford 3000 thực tế phân loại theo chủ đề phong phú
    catalog_raw = [
        # Nhóm Nghề nghiệp, Hành chính & Doanh nghiệp
        ("applicant", "/ˈæplɪkənt/", "noun", "ứng viên xin việc", "Every qualified applicant receives an initial screening call.", "Họp hành & Công sở", "A2"),
        ("apprentice", "/əˈprentɪs/", "noun", "người học việc", "The master carpenter trained a young eager apprentice.", "Họp hành & Công sở", "B2"),
        ("boardroom", "/ˈbɔːdruːm/", "noun", "phòng họp ban giám đốc", "The board of directors convened in the 20th-floor boardroom.", "Họp hành & Công sở", "B2"),
        ("bonus", "/ˈbəʊnəs/", "noun", "tiền thưởng thành tích", "Employees received a performance bonus at year-end.", "Họp hành & Công sở", "B1"),
        ("briefcase", "/ˈbriːfkeɪs/", "noun", "cặp đựng tài liệu", "He placed his laptop and contracts into a leather briefcase.", "Họp hành & Công sở", "A2"),
        ("clerk", "/klɑːk/", "noun", "nhân viên văn phòng, thư ký", "The municipal clerk stamped the official registration form.", "Họp hành & Công sở", "A2"),
        ("clientele", "/ˌkliːənˈtel/", "noun", "tập khách hàng quen", "The upscale restaurant caters to an international clientele.", "Họp hành & Công sở", "B2"),
        ("collaborate", "/kəˈlæbəreɪt/", "verb", "hợp tác, cộng tác", "Designers and engineers collaborate on product prototypes.", "Họp hành & Công sở", "B1"),
        ("collaboration", "/kəˌlæbəˈreɪʃn/", "noun", "sự hợp tác", "Effective cross-functional collaboration accelerates delivery.", "Họp hành & Công sở", "B2"),
        ("collaborative", "/kəˈlæbərətɪv/", "adj", "mang tính cộng tác", "We foster a collaborative work environment with open desks.", "Họp hành & Công sở", "B2"),
        ("colleague", "/ˈkɒliːɡ/", "noun", "đồng nghiệp", "I shared the updated project notes with my design colleague.", "Họp hành & Công sở", "A2"),
        ("commence", "/kəˈmens/", "verb", "bắt đầu, khai mạc", "The keynote presentation will commence promptly at nine.", "Họp hành & Công sở", "B2"),
        ("compensation", "/ˌkɒmpenˈseɪʃn/", "noun", "thù lao, bồi thường", "The executive compensation package includes stock options.", "Họp hành & Công sở", "B2"),
        ("competence", "/ˈkɒmpɪtəns/", "noun", "năng lực chuyên môn", "Demonstrate your technical competence in the live interview.", "Họp hành & Công sở", "B2"),
        ("competent", "/ˈkɒmpɪtənt/", "adj", "có đủ năng lực, thành thạo", "She is a highly competent bilingual product manager.", "Họp hành & Công sở", "B1"),
        ("compliance", "/kəmˈplaɪəns/", "noun", "sự tuân thủ quy chuẩn", "Ensure strict compliance with workplace safety protocols.", "Họp hành & Công sở", "B2"),
        ("conduct", "/kənˈdʌkt/", "verb", "tiến hành, chỉ đạo", "Conduct regular surveys to gauge employee satisfaction.", "Họp hành & Công sở", "B2"),
        ("conference", "/ˈkɒnfərəns/", "noun", "hội nghị chuyên đề", "The annual software conference hosted three thousand attendees.", "Họp hành & Công sở", "B1"),
        ("contractor", "/kənˈtræktə(r)/", "noun", "nhà thầu độc lập", "We hired an independent contractor to build the cloud backend.", "Họp hành & Công sở", "B1"),
        ("corporate", "/ˈkɔːpərət/", "adj", "thuộc doanh nghiệp, công ty", "She climbed the corporate ladder through exceptional diligence.", "Họp hành & Công sở", "B2"),
        ("credential", "/krəˈdenʃl/", "noun", "chứng chỉ chuyên môn", "Check the verified credentials of all freelance applicants.", "Họp hành & Công sở", "B2"),
        ("cubicle", "/ˈkjuːbɪkl/", "noun", "ngăn làm việc văn phòng", "He decorated his office cubicle with family photographs.", "Họp hành & Công sở", "B1"),
        ("deadline", "/ˈdedlaɪn/", "noun", "hạn chót hoàn thành", "Submit your finalized report before the Friday noon deadline.", "Họp hành & Công sở", "B1"),
        ("delegate", "/ˈdelɪɡeɪt/", "verb", "ủy quyền, giao phó", "Effective managers delegate routine tasks to trusted teams.", "Họp hành & Công sở", "B2"),
        ("delegation", "/ˌdelɪˈɡeɪʃn/", "noun", "phái đoàn, sự ủy thác", "An international trade delegation visited the high-tech zone.", "Họp hành & Công sở", "B2"),
        ("demote", "/dɪˈməʊt/", "verb", "giáng chức, hạ bậc", "He was demoted after repeatedly ignoring safety regulations.", "Họp hành & Công sở", "B2"),
        ("director", "/dəˈrektə(r)/", "noun", "giám đốc, đạo diễn", "The managing director presented the quarterly financial outlook.", "Họp hành & Công sở", "A2"),
        ("dismiss", "/dɪsˈmɪs/", "verb", "sa thải, giải tán", "The board decided to dismiss the underperforming executive.", "Họp hành & Công sở", "B2"),
        ("efficiency", "/ɪˈfɪʃnsi/", "noun", "hiệu suất công việc", "Automating repetitive data entry dramatically boosts efficiency.", "Họp hành & Công sở", "B2"),
        ("eligible", "/ˈelɪdʒəbl/", "adj", "đủ tư cách, đủ điều kiện", "Employees are eligible for paid parental leave after one year.", "Họp hành & Công sở", "B2"),
        ("employ", "/ɪmˈplɔɪ/", "verb", "thuê mướn nhân sự", "Tech enterprises employ remote workers across multiple continents.", "Họp hành & Công sở", "A2"),
        ("employee", "/ɪmˈplɔɪiː/", "noun", "nhân viên, người làm công", "Every employee receives free access to language training tools.", "Họp hành & Công sở", "A2"),
        ("employer", "/ɪmˈplɔɪə(r)/", "noun", "người sử dụng lao động, công ty", "Top employers prioritize communicative agility and teamwork.", "Họp hành & Công sở", "A2"),
        ("enterprise", "/ˈentəpraɪz/", "noun", "doanh nghiệp quy mô lớn", "Global enterprises require robust cybersecurity infrastructure.", "Họp hành & Công sở", "B2"),
        ("evaluate", "/ɪˈvæljueɪt/", "verb", "đánh giá thành tích", "Managers evaluate team performance during quarterly reviews.", "Họp hành & Công sở", "B2"),
        ("executive", "/ɪɡˈzekjətɪv/", "noun", "giám đốc điều hành", "The chief executive delivered an inspiring keynote address.", "Họp hành & Công sở", "B1"),
        ("expertise", "/ˌekspɜːˈtiːz/", "noun", "chuyên môn sâu", "Her technical expertise in acoustic filtering is respected.", "Họp hành & Công sở", "B2"),
        ("flexible", "/ˈfleksəbl/", "adj", "linh hoạt, mềm dẻo", "Modern startups offer flexible working hours for engineers.", "Họp hành & Công sở", "B1"),
        ("freelance", "/ˈfriːlɑːns/", "adj", "làm nghề tự do", "She works as a freelance graphic designer and copywriter.", "Họp hành & Công sở", "B1"),
        ("grievance", "/ˈɡriːvəns/", "noun", "khiếu nại nơi làm việc", "Employees may file a confidential workplace grievance online.", "Họp hành & Công sở", "B2"),
        ("headquarters", "/ˌhedˈkwɔːtəz/", "noun", "trụ sở chính", "The corporate headquarters is situated in downtown Tokyo.", "Họp hành & Công sở", "B1"),
        ("hierarchy", "/ˈhaɪərɑːki/", "noun", "hệ thống cấp bậc", "The flat organizational hierarchy encourages candid feedback.", "Họp hành & Công sở", "B2"),
        ("incentive", "/ɪnˈsentɪv/", "noun", "động lực khích lệ, tiền thưởng", "Performance bonuses provide a strong financial incentive.", "Họp hành & Công sở", "B2"),
        ("intern", "/ˈɪntɜːn/", "noun", "thực tập sinh", "The engineering intern developed an automated testing script.", "Họp hành & Công sở", "B1"),
        ("internship", "/ˈɪntɜːnʃɪp/", "noun", "kỳ thực tập", "Summer internships give undergraduates hands-on industry exposure.", "Họp hành & Công sở", "B1"),
        ("interview", "/ˈɪntəvjuː/", "noun", "cuộc phỏng vấn xin việc", "Prepare concise answers before attending the panel interview.", "Họp hành & Công sở", "A1"),
        ("leadership", "/ˈliːdəʃɪp/", "noun", "kỹ năng lãnh đạo", "Authentic leadership inspires team members to reach their best.", "Họp hành & Công sở", "B1"),
        ("management", "/ˈmænɪdʒmənt/", "noun", "ban quản lý, quản trị", "Senior management approved the budget for office renovation.", "Họp hành & Công sở", "A2"),
        ("mentor", "/ˈmentɔː(r)/", "noun", "người cố vấn nghề nghiệp", "Her career mentor provided invaluable pragmatic guidance.", "Họp hành & Công sở", "B2"),
        ("negotiate", "/nɪˈɡəʊʃieɪt/", "verb", "thương lượng, đàm phán", "Negotiate contract terms politely to reach a win-win consensus.", "Họp hành & Công sở", "B1"),
        ("negotiation", "/nɪˌɡəʊʃiˈeɪʃn/", "noun", "cuộc đàm phán", "The trade negotiations concluded with a historic bilateral treaty.", "Họp hành & Công sở", "B2"),
        ("occupy", "/ˈɒkjupaɪ/", "verb", "chiếm giữ, đảm nhận vị trí", "She occupies the position of senior international counsel.", "Họp hành & Công sở", "B1"),
        ("overtime", "/ˈəʊvətaɪm/", "noun", "giờ làm thêm", "Employees working overtime receive time-and-a-half compensation.", "Họp hành & Công sở", "A2"),
        ("partner", "/ˈpɑːtnə(r)/", "noun", "đối tác làm ăn", "They became equal business partners in the software venture.", "Họp hành & Công sở", "A2"),
        ("partnership", "/ˈpɑːtnəʃɪp/", "noun", "quan hệ đối tác", "The strategic partnership accelerated global distribution.", "Họp hành & Công sở", "B1"),
        ("payroll", "/ˈpeɪrəʊl/", "noun", "bảng lương nhân viên", "The accounting team processes monthly payroll on the 25th.", "Họp hành & Công sở", "B2"),
        ("pension", "/ˈpenʃn/", "noun", "lương hưu trí", "He retired at sixty-five and enjoys a comfortable state pension.", "Họp hành & Công sở", "B1"),
        ("personnel", "/ˌpɜːsəˈnel/", "noun", "nhân sự công ty", "All sales personnel must complete annual compliance training.", "Họp hành & Công sở", "B2"),
        ("position", "/pəˈzɪʃn/", "noun", "vị trí công việc", "She applied for the bilingual customer relations position.", "Họp hành & Công sở", "A2"),
        ("presentation", "/ˌpreznˈteɪʃn/", "noun", "bài thuyết trình", "He rehearsed his slides thoroughly before the client presentation.", "Họp hành & Công sở", "A2"),
        ("probation", "/prəˈbeɪʃn/", "noun", "thời gian thử việc", "New hires undergo a ninety-day professional probation period.", "Họp hành & Công sở", "B2"),
        ("profession", "/prəˈfeʃn/", "noun", "nghề nghiệp chuyên môn", "Teaching is an honorable and profoundly impactful profession.", "Họp hành & Công sở", "B1"),
        ("professional", "/prəˈfeʃənl/", "adj", "chuyên nghiệp, chuẩn mực", "Maintain a polite, professional tone in all business emails.", "Họp hành & Công sở", "A2"),
        ("promotion", "/prəˈməʊʃn/", "noun", "sự thăng chức", "Her exceptional dedication earned her a well-deserved promotion.", "Họp hành & Công sở", "B1"),
        ("recruit", "/rɪˈkruːt/", "verb", "tuyển dụng nhân sự", "The engineering firm plans to recruit fifty graduates this fall.", "Họp hành & Công sở", "B1"),
        ("recruitment", "/rɪˈkruːtmənt/", "noun", "công tác tuyển dụng", "The human resources team launched a global recruitment drive.", "Họp hành & Công sở", "B2"),
        ("resignation", "/ˌrezɪɡˈneɪʃn/", "noun", "sự từ chức, đơn từ chức", "He submitted his formal resignation to pursue doctoral studies.", "Họp hành & Công sở", "B2"),
        ("resume", "/ˈrezjumeɪ/", "noun", "sơ yếu lý lịch, CV", "Tailor your resume highlighting relevant bilingual capabilities.", "Họp hành & Công sở", "A2"),
        ("retire", "/rɪˈtaɪə(r)/", "verb", "nghỉ hưu", "He plans to retire to a quiet seaside cottage next year.", "Họp hành & Công sở", "A2"),
        ("retirement", "/rɪˈtaɪəmənt/", "noun", "sự nghỉ hưu", "Save early to guarantee a peaceful, secure retirement.", "Họp hành & Công sở", "B1"),
        ("roster", "/ˈrɒstə(r)/", "noun", "bảng phân công trực nhật", "Check the updated shift roster on the employee notice board.", "Họp hành & Công sở", "B2"),
        ("salary", "/ˈsæləri/", "noun", "tiền lương tháng", "She negotiated a ten percent salary increment upon promotion.", "Họp hành & Công sở", "A2"),
        ("severance", "/ˈsevərəns/", "noun", "trợ cấp thôi việc", "Departing staff received a generous six-month severance package.", "Họp hành & Công sở", "B2"),
        ("shift", "/ʃɪft/", "noun", "ca làm việc", "Nurses rotate between morning, afternoon, and night shifts.", "Họp hành & Công sở", "A2"),
        ("staff", "/stɑːf/", "noun", "đội ngũ nhân viên", "The friendly hotel staff made our holiday unforgettable.", "Họp hành & Công sở", "A2"),
        ("stakeholder", "/ˈsteɪkhəʊldə(r)/", "noun", "các bên liên quan", "Consult major community stakeholders before finalizing the roadmap.", "Họp hành & Công sở", "B2"),
        ("supervisor", "/ˈsuːpəvaɪzə(r)/", "noun", "người giám sát, quản đốc", "Consult your direct supervisor before ordering new hardware.", "Họp hành & Công sở", "B1"),
        ("telecommute", "/ˌtelɪkəˈmjuːt/", "verb", "làm việc từ xa qua mạng", "Many programmers prefer to telecommute three days a week.", "Họp hành & Công sở", "B2"),
        ("tenure", "/ˈtenjə(r)/", "noun", "nhiệm kỳ, biên chế học thuật", "The distinguished professor was granted lifetime university tenure.", "Họp hành & Công sở", "B2"),
        ("trainee", "/ˌtreɪˈniː/", "noun", "học viên thực tập", "Experienced pilots mentor incoming airline trainees.", "Họp hành & Công sở", "A2"),
        ("turnover", "/ˈtɜːnəʊvə(r)/", "noun", "tỷ lệ thay thế nhân viên", "Fostering psychological safety lowers costly staff turnover.", "Họp hành & Công sở", "B2"),
        ("vacancy", "/ˈveɪkənsi/", "noun", "vị trí tuyển dụng còn trống", "The clinic advertised a vacancy for a pediatric specialist.", "Họp hành & Công sở", "B1"),
        ("workplace", "/ˈwɜːkpleɪs/", "noun", "nơi làm việc, công sở", "A positive workplace culture fuels creativity and loyalty.", "Họp hành & Công sở", "A2"),
    ]

    # Chúng ta sinh thêm từ vựng Oxford 3000 chuẩn quốc tế để đạt đúng chỉ tiêu
    # Danh mục phong phú: từ A đến Z của Oxford 3000
    from scripts.oxford_lexicon_data import get_lexicon_list
    lexicon = get_lexicon_list()

    all_catalog = []
    seen = set()

    for item in catalog_raw:
        w = item[0].strip().lower()
        if w not in seen:
            seen.add(w)
            all_catalog.append({
                "word": w,
                "ipa": item[1],
                "pos": item[2],
                "meaning_vi": item[3],
                "example_sentence": item[4],
                "topic": item[5],
                "level": item[6],
                "is_custom": 0
            })

    for item in lexicon:
        w = item["word"].strip().lower()
        if w not in seen:
            seen.add(w)
            all_catalog.append(item)

    print(f"Generated Catalog Total Items: {len(all_catalog)}")

    out_file = os.path.join("scripts", "oxford_full_catalog.py")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("# scripts/oxford_full_catalog.py\n")
        f.write("# Toàn bộ danh mục từ vựng chuẩn Oxford 3000\n\n")
        f.write("def get_catalog_words():\n")
        f.write(f"    return {json.dumps(all_catalog, ensure_ascii=False, indent=8)}\n")

    print(f"Wrote {len(all_catalog)} items to {out_file}")

if __name__ == "__main__":
    generate_catalog()
