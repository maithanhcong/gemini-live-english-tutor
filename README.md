# 🎓 Gemini Live English Tutor - Gia Sư Tiếng Anh Tương Tác Trực Tiếp

[![Python Version](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Google Gen AI SDK](https://img.shields.io/badge/Google%20Gen%20AI-2.14%2B-orange.svg)](https://github.com/googleapis/python-genai)
[![SQLite](https://img.shields.io/badge/Database-SQLite3-003B57.svg)](https://www.sqlite.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Gemini Live English Tutor** là ứng dụng web tương tác thời gian thực cao cấp hỗ trợ học tiếng Anh đa phương thức (giọng nói, văn bản, video và luyện dịch ngữ cảnh) được xây dựng dựa trên **Google Gemini Multimodal Live API (Bidirectional WebSocket Streaming)** kết hợp với **FastAPI** và **Vanilla JavaScript**.

---

## 🌟 Tính Năng Nổi Bật (Key Features)

### 1. 🎙️ Đàm thoại hai chiều thời gian thực (Real-time Live Audio)
* Tương tác trò chuyện bằng giọng nói tự nhiên với Gia sư AI có độ trễ cực thấp (< 500ms).
* Xử lý âm thanh chuẩn phòng thu **PCM 24kHz Little Endian**, hỗ trợ ngắt lời tức thời (Barge-in / Interruption handling).
* Sửa lỗi phát âm, ngữ điệu và ngữ pháp theo thời gian thực (Real-time phonetic correction).

### 2. 🔄 Cơ chế dự phòng thông minh (Failover & 4-Key Rotation)
* Tự động luân phiên xoay vòng giữa **4 API Keys** khi gặp mã lỗi `429`, `RESOURCE_EXHAUSTED` hoặc chạm hạn ngạch (Quota).
* Chuỗi Model Live dự phòng theo thứ tự ưu tiên: `gemini-3.8-live` $\to$ `gemini-3-flash-live` $\to$ `gemini-2.5-flash-native-audio` $\to$ `gemini-2.0-flash-exp`.

### 3. 📖 Luyện dịch song ngữ ngữ cảnh (Contextual Passage Practice)
* Tích hợp lộ trình **1000 từ vựng cốt lõi** phân cấp theo chủ đề và cấp bậc CEFR.
* Gemini AI tự động chọn lọc 3-5 từ đang chọn để kiến tạo đoạn văn ngắn 2-3 câu giàu ngữ cảnh tự nhiên.
* Học viên tự dịch sang tiếng Việt trước khi nộp bài để đối chiếu đáp án với gợi ý chuẩn mực của AI.
* Tích hợp bộ nhớ đệm (In-memory Cache) tối ưu token và chi phí API.

### 4. 👥 Phân chia tiến độ đa người dùng (Multi-User Data Isolation)
* Hệ thống tài khoản độc lập lưu trữ trên cơ sở dữ liệu nhẹ **SQLite** (`study_progress.db`).
* Mật khẩu mã hóa bảo mật chuẩn **Salted SHA-256**.
* Tiến độ học từ vựng và lịch sử bài dịch của từng học viên được cách ly hoàn toàn.
* Tự động đồng bộ trạng thái học tập ngược vào cột "Đã học" của file Excel lộ trình.

### 5. 🎯 Đồng bộ ngữ cảnh thông minh (Smart Context Sync)
* Những từ học viên **đã tích chọn** ở Tab Luyện Dịch sẽ được xem là từ đã nắm vững.
* Ở Tab Đàm Thoại Trực Tiếp, Gia sư AI chỉ tập trung khảo sát, phản xạ và luyện phát âm xoay quanh **những từ chưa thuộc**.

### 6. 📱 Giao diện thích ứng hoàn hảo (Responsive Design)
* **Desktop (> 1180px)**: Bố cục 2 cột cố định tiện nghi (460px Sidebar bên trái, bài đọc đối chiếu bên phải).
* **Tablet / iPad (768px – 1180px)**: Bố cục 2 cột co giãn tỷ lệ vàng **36% : 64%**, hỗ trợ xoay ngang/dọc, touch target chuẩn ngón tay $\ge$ 44px.
* **Mobile (< 768px)**: Cột từ vựng giấu kín, thay bằng nút bấm nổi bật duy nhất mở **Bottom Sheet / Modal** trượt từ đáy màn hình kèm backdrop làm mờ trang web.

---

## 🛠️ Ngăn Xếp Công Nghệ (Tech Stack)

* **Backend**: Python 3.12+, FastAPI, Uvicorn, WebSockets, OpenPyXL, HTTPX.
* **AI & LLM**: Google Gen AI Python SDK (`google-genai`), Gemini Multimodal Live API.
* **Database**: SQLite3 (`study_progress.db`) & Microsoft Excel (`.xlsx`).
* **Frontend**: Modern Vanilla HTML5, CSS3 Variables, ES6+ JavaScript, Web Audio API (`AudioWorklet`).
* **Deployment & Tunnel**: Docker, Cloudflare Quick Tunnel (QUIC / HTTP2).

---

## 📁 Cấu Trúc Dự Án (Project Structure)

```text
gemini-live-english-tutor/
├── data/                                # Chứa Excel 1000 từ và knowledge base json/md
│   ├── 1000_core_words_curriculum.xlsx  # Dữ liệu 1000 từ vựng cốt lõi & tiến độ
│   ├── tutor_knowledge_base.json        # Cơ sở tri thức phát âm tiếng Anh cho người Việt
│   └── tutor_knowledge_base.md          # Bản tra cứu Markdown của cẩm nang phát âm
├── docs/                                # Tài liệu hướng dẫn triển khai
│   └── deployment_cloud_run.md          # Hướng dẫn deploy Docker lên Google Cloud Run
├── frontend/                            # Toàn bộ giao diện người dùng (Responsive Web UI)
│   ├── index.html                       # Cấu trúc giao diện 2 Tab (Live & Luyện Dịch)
│   ├── style.css                        # Thiết kế giao diện (Desktop, iPad, Mobile Drawer)
│   ├── main.js                          # Logic điều khiển ứng dụng, Auth & Modal
│   ├── gemini-client.js                 # Client WebSocket trao đổi âm thanh với backend
│   ├── media-handler.js                 # Bộ xử lý Microphone, Camera và loa phát
│   └── pcm-processor.js                 # AudioWorklet xử lý luồng PCM 16/24kHz
├── scripts/                             # Các script migrate dữ liệu, build tri thức, test
│   ├── build_tutor_knowledge.py         # Script tự động trích xuất tri thức từ PDF
│   ├── upgrade_excel_1000_words.py      # Script chuẩn hóa 1000 từ vựng vào file Excel
│   ├── test_multiuser_flow.py           # Test kiểm thử tính năng đăng ký/đăng nhập
│   └── twilio_handler.py                # Twilio voice call handler mở rộng
├── .dockerignore                        # Danh sách loại trừ build Docker
├── .env.example                         # Mẫu cấu hình biến môi trường
├── .gitignore                           # Danh sách loại trừ tệp nhạy cảm
├── ARCHITECTURE.md                      # Tài liệu đặc tả kiến trúc kỹ thuật chi tiết
├── database.py                          # ORM/Quản lý CSDL SQLite đa người dùng & xác thực
├── Dockerfile                           # Cấu hình containerization sản phẩm
├── gemini_live.py                       # Bộ điều khiển phiên kết nối Gemini Live WebSocket
├── main.py                              # Máy chủ FastAPI & WebSocket router (/ws, /api/*)
├── passage_service.py                   # Dịch vụ sinh đoạn văn ngữ cảnh & quản lý Excel
├── README.md                            # Hướng dẫn dự án song ngữ
├── requirements.txt                     # Danh sách thư viện Python phụ thuộc
└── tutor_system_instruction.py          # Bộ sinh System Instruction cá nhân hóa động
```

---

## 🚀 Hướng Dẫn Khởi Chạy (Quick Start Guide)

### 1. Yêu cầu hệ thống
* Python 3.10 trở lên (khuyên dùng Python 3.12).
* Quản lý gói `uv` (hoặc `pip` tiêu chuẩn).
* Ít nhất 1 API Key của Google AI Studio ([Lấy API Key miễn phí tại đây](https://aistudio.google.com/)).

### 2. Cài đặt môi trường
Clone mã nguồn về máy:
```bash
git clone https://github.com/maithanhcong/gemini-live-english-tutor.git
cd gemini-live-english-tutor
```

Cài đặt các gói phụ thuộc:
```bash
# Cách 1: Sử dụng uv (nhanh và ổn định)
uv venv
uv pip install -r requirements.txt

# Cách 2: Sử dụng pip thông thường
python -m venv .venv
source .venv/bin/activate   # Trên Linux/macOS
# hoặc: .venv\Scripts\activate   # Trên Windows
pip install -r requirements.txt
```

### 3. Cấu hình biến môi trường
Sao chép tệp cấu hình mẫu và điền API Key của bạn:
```bash
cp .env.example .env
```
Mở file `.env` và cập nhật:
```env
GEMINI_API_KEYS=AQ.Key1...,AQ.Key2...,AQ.Key3...,AQ.Key4...
MODEL=gemini-3.8-live
PORT=8000
```

### 4. Khởi chạy Web Server
```bash
uv run main.py
# hoặc: python main.py
```
Mở trình duyệt và truy cập:
👉 **[http://localhost:8000](http://localhost:8000)**

### 5. Công khai ra Internet bằng Cloudflare Tunnel (Tùy chọn)
Nếu muốn mở trên điện thoại hoặc chia sẻ cho người khác cùng trải nghiệm:
```bash
cloudflared tunnel --url http://127.0.0.1:8000
```
Truy cập vào liên kết `https://*.trycloudflare.com` hiển thị trên màn hình terminal.

---

## 📡 Danh Sách API Endpoints Chính

| Phương thức | Đường dẫn API | Chức năng |
| :--- | :--- | :--- |
| `WS` | `/ws?token=...` | Kết nối WebSocket âm thanh/video Live hai chiều |
| `POST` | `/api/auth/register` | Đăng ký tài khoản học tập mới |
| `POST` | `/api/auth/login` | Đăng nhập và nhận Bearer Token |
| `GET` | `/api/auth/me` | Lấy thông tin tài khoản hiện tại |
| `GET` | `/api/vocab/sync` | Đọc danh sách từ vựng từ Excel & SQLite |
| `POST` | `/api/vocab/update-selection` | Lưu trạng thái tích chọn từ vựng của học viên |
| `POST` | `/api/passage/generate` | Tạo đoạn văn luyện dịch ngữ cảnh từ từ đã chọn |
| `POST` | `/api/passage/submit` | Nộp bản dịch và nhận kết quả đối chiếu AI |

---

## 📄 Bản Quyền (License)

Dự án được phân phối dưới giấy phép **MIT License**. Bạn được tự do sử dụng, chỉnh sửa và triển khai cho mục đích cá nhân cũng như thương mại.
