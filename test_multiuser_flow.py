import httpx
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "http://127.0.0.1:8000"

def test_multiuser_flow():
    client = httpx.Client(base_url=BASE_URL, timeout=10)

    print("=== [BƯỚC 1] ĐĂNG KÝ VÀ KIỂM TRA TÀI KHOẢN 1 (user_alpha) ===")
    import time
    timestamp = int(time.time())
    u1 = f"user_alpha_{timestamp}"
    p1 = "pass1234"

    res = client.post("/api/auth/register", json={"username": u1, "password": p1})
    assert res.status_code == 200, f"Register u1 failed: {res.text}"
    data1 = res.json()
    print("User 1 Register Response:", data1)
    assert data1["status"] == "success"
    token1 = data1["token"]
    assert token1, "User 1 must receive a token"

    # Kiểm tra /api/auth/me với token 1
    me1 = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token1}"}).json()
    print("User 1 Me:", me1)
    assert me1["status"] == "authenticated"
    assert me1["user"]["username"] == u1
    assert me1["mastered_count"] == 0

    # User 1 tích chọn 3 từ: 'apple', 'banana', 'orange'
    words_u1 = ["apple", "banana", "orange"]
    up1 = client.post(
        "/api/vocab/update-selection",
        headers={"Authorization": f"Bearer {token1}"},
        json={"selected_words": words_u1}
    ).json()
    print("User 1 Update Selection:", up1)
    assert up1["status"] == "success"
    assert up1["selected_count"] == 3

    # Kiểm tra danh sách từ của User 1 qua /api/vocab/sync
    sync1 = client.get("/api/vocab/sync", headers={"Authorization": f"Bearer {token1}"}).json()
    print("User 1 Sync Words Count:", sync1["learned_count"])
    assert set(sync1["selected_words"]) == set(words_u1)

    print("\n=== [BƯỚC 2] ĐĂNG XUẤT TÀI KHOẢN 1 ===")
    logout1 = client.post("/api/auth/logout", headers={"Authorization": f"Bearer {token1}"}).json()
    print("User 1 Logout:", logout1)
    assert logout1["status"] == "success"

    # Kiểm tra lại /api/auth/me với token cũ -> phải unauthenticated
    me1_after = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token1}"}).json()
    print("User 1 After Logout Me:", me1_after)
    assert me1_after["status"] == "unauthenticated"

    print("\n=== [BƯỚC 3] ĐĂNG KÝ VÀ KIỂM TRA TÀI KHOẢN 2 (user_beta) ===")
    u2 = f"user_beta_{timestamp}"
    p2 = "pass5678"

    res2 = client.post("/api/auth/register", json={"username": u2, "password": p2})
    assert res2.status_code == 200, f"Register u2 failed: {res2.text}"
    data2 = res2.json()
    print("User 2 Register Response:", data2)
    assert data2["status"] == "success"
    token2 = data2["token"]

    # Kiểm tra /api/auth/me với token 2
    me2 = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token2}"}).json()
    print("User 2 Me:", me2)
    assert me2["mastered_count"] == 0

    # Kiểm tra danh sách từ của User 2 ban đầu -> Phải hoàn toàn rỗng, KHÔNG bị lẫn từ của User 1!
    sync2_initial = client.get("/api/vocab/sync", headers={"Authorization": f"Bearer {token2}"}).json()
    print("User 2 Initial Selected Words:", sync2_initial["selected_words"])
    assert len(sync2_initial["selected_words"]) == 0, "User 2 ban đầu không được chứa từ của User 1!"

    # User 2 tích chọn 2 từ hoàn toàn khác: 'cat', 'dog'
    words_u2 = ["cat", "dog"]
    up2 = client.post(
        "/api/vocab/update-selection",
        headers={"Authorization": f"Bearer {token2}"},
        json={"selected_words": words_u2}
    ).json()
    print("User 2 Update Selection:", up2)
    assert up2["selected_count"] == 2

    # User 2 nộp bài dịch
    sub2 = client.post(
        "/api/passage/submit-translation",
        headers={"Authorization": f"Bearer {token2}"},
        json={
            "used_words": "cat, dog",
            "english_passage": "The cat and dog are sleeping together.",
            "vietnamese_translation": "Con mèo và con chó đang ngủ cùng nhau.",
            "my_translation": "Mèo và chó ngủ chung."
        }
    ).json()
    print("User 2 Submit Translation:", sub2)
    assert sub2["status"] == "success"

    # Kiểm tra lịch sử dịch của User 2
    hist2 = client.get("/api/passage/history", headers={"Authorization": f"Bearer {token2}"}).json()
    print("User 2 Translation History Count:", len(hist2["history"]))
    assert len(hist2["history"]) >= 1

    print("\n=== [BƯỚC 4] ĐĂNG NHẬP LẠI TÀI KHOẢN 1 VÀ XÁC NHẬN DỮ LIỆU ĐỘC LẬP HOÀN TOÀN ===")
    login1 = client.post("/api/auth/login", json={"username": u1, "password": p1}).json()
    print("User 1 Re-login:", login1)
    assert login1["status"] == "success"
    token1_new = login1["token"]

    sync1_check = client.get("/api/vocab/sync", headers={"Authorization": f"Bearer {token1_new}"}).json()
    print("User 1 Words After User 2 Actions:", sync1_check["selected_words"])
    assert set(sync1_check["selected_words"]) == set(words_u1), "User 1 vẫn phải giữ nguyên chính xác danh sách từ ban đầu!"
    assert "cat" not in sync1_check["selected_words"], "Từ của User 2 tuyệt đối KHÔNG được xuất hiện trong User 1!"
    assert "dog" not in sync1_check["selected_words"], "Từ của User 2 tuyệt đối KHÔNG được xuất hiện trong User 1!"

    hist1_check = client.get("/api/passage/history", headers={"Authorization": f"Bearer {token1_new}"}).json()
    print("User 1 Translation History Count:", len(hist1_check["history"]))
    assert len(hist1_check["history"]) == 0, "Lịch sử dịch của User 2 không được rò rỉ sang User 1!"

    print("\n🎉🎉🎉 TOÀN BỘ KIỂM TRA BẢO MẬT & CÔ LẬP TIẾN ĐỘ ĐA NGƯỜI DÙNG (DATA ISOLATION) THÀNH CÔNG 100%! 🎉🎉🎉")

if __name__ == "__main__":
    test_multiuser_flow()
