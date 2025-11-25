# Hướng dẫn Cài Đặt AI Quiz Generator

## 🔧 Backend Setup

### 1. Cài Đặt Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Cấu Hình Environment Variables
Tạo file `.env` trong thư mục `backend/` với nội dung:

```env
# Gemini API Configuration
# Lấy API key từ: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your_actual_api_key_here

# Database Configuration
DATABASE_URL=mysql+mysqlconnector://root:@localhost/codecourse

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
```

**⚠️ QUAN TRỌNG:**
- Đi tới https://makersuite.google.com/app/apikey
- Đăng nhập bằng tài khoản Google
- Nhấn "Create API Key"
- Sao chép key và dán vào `GEMINI_API_KEY` trong `.env`

### 3. Chạy Backend
```bash
python app.py
# hoặc
flask run
```

Backend sẽ chạy tại: `http://localhost:5000`

---

## 🎨 Frontend Setup

### 1. Cài Đặt Dependencies (nếu chưa)
```bash
cd fe
npm install
```

### 2. Chạy Frontend
```bash
npm run dev
```

Frontend sẽ chạy tại: `http://localhost:5173` (hoặc port khác)

---

## 🧪 Kiểm Tra API

### Test Endpoint Generate Quiz
```bash
curl -X POST http://localhost:5000/api/ai/quiz/generate \
  -H "Content-Type: application/json" \
  -d '{
    "lesson_title": "Vòng lặp for trong Python",
    "num_questions": 3,
    "difficulty": "medium"
  }'
```

### Expected Response:
```json
{
  "lesson_title": "Vòng lặp for trong Python",
  "questions": [
    {
      "question": "...",
      "options": ["...", "...", "...", "..."],
      "correctAnswer": 0,
      "explanation": "..."
    }
  ],
  "count": 3,
  "requested_count": 3,
  "difficulty": "medium",
  "model": "gemini-2.5-flash",
  "error": null
}
```

---

## 🚨 Troubleshooting

### "Failed to fetch"
**Nguyên nhân:** API không chạy hoặc URL sai

**Giải pháp:**
1. Kiểm tra backend có đang chạy: `http://localhost:5000`
2. Kiểm tra frontend URL đúng: `http://localhost:5000/api/ai/quiz/generate`
3. Kiểm tra CORS được cấu hình trong `app/__init__.py`

### "Missing GEMINI_API_KEY"
**Nguyên nhân:** Environment variable không được đặt

**Giải pháp:**
1. Tạo file `.env` trong thư mục `backend/`
2. Thêm: `GEMINI_API_KEY=your_key_here`
3. Restart Flask

### "Failed to parse AI response"
**Nguyên nhân:** API trả về response không đúng format

**Giải pháp:**
1. Kiểm tra logs trong terminal backend
2. Thử regenerate câu hỏi
3. Kiểm tra API key có hợp lệ không

### Lỗi Rate Limit
**Nguyên nhân:** Vượt quá giới hạn API calls

**Giải pháp:**
1. Chờ 1 phút trước khi thử lại
2. Nâng cấp plan Gemini API

---

## 📚 API Endpoints

### 1. Generate Quiz
```
POST /api/ai/quiz/generate
```
**Body:**
- `lesson_title` (required): Tiêu đề bài học
- `num_questions` (optional, default=5): Số câu (1-20)
- `difficulty` (optional, default="medium"): easy|medium|hard
- `model` (optional): Tên model Gemini

**Response:** Quiz questions trong JSON format

---

### 2. Generate Batch Quiz
```
POST /api/ai/quiz/generate-batch
```
**Body:**
```json
{
  "lessons": [
    {"id": 1, "title": "Biến và Kiểu dữ liệu"},
    {"id": 2, "title": "Vòng lặp for"}
  ],
  "num_questions": 5,
  "difficulty": "medium"
}
```

---

### 3. Validate Answer
```
POST /api/ai/quiz/validate
```
**Body:**
- `user_answer`: Index của đáp án (0-3)
- `correct_answer`: Index đáp án đúng

---

### 4. Enhance Question
```
POST /api/ai/quiz/enhance
```
**Body:**
- `question`: Nội dung câu hỏi
- `options`: Mảng 4 đáp án
- `action`: simplify|enhance|rephrase

---

## 🎯 Workflow Sử Dụng

1. **Mở Quản Lý Khóa Học** → Instructor/CourseLessons
2. **Chọn Bài Học** → Expand lesson → Mở Test Section
3. **Nhấn "Tạo bằng AI"** → Modal mở ra
4. **Cấu hình:**
   - Số câu hỏi (1-20)
   - Độ khó (Easy/Medium/Hard)
5. **Nhấn "Tạo Câu Hỏi"** → AI tạo câu hỏi
6. **Preview & Edit:**
   - Xem câu hỏi + đáp án
   - Xóa câu hỏi không phù hợp
   - Tạo lại câu hỏi đơn
7. **Nhấn "Lưu Câu Hỏi"** → Tạo Test mới với các câu hỏi

---

## 📝 Notes

- API key được giữ bí mật trong `.env` (không commit lên git)
- Mỗi API call tốn quota của Gemini
- Test auto-generate thời gian làm (~3 phút/câu)
- Câu hỏi được shuffle để tránh pattern

---

**💡 Gặp vấn đề?** Check logs trong terminal backend hoặc browser console.
