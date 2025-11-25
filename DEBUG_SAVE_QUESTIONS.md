# Debug Guide: "Unexpected token '<'" Error

## 🔍 Nguyên Nhân

Lỗi này xảy ra khi JavaScript nhận về HTML thay vì JSON từ server:
```
Unexpected token '<', "<!doctype "... is not valid JSON
```

### Có nghĩa là:
- Backend trả về **HTML error page** (500 error page)
- Thay vì JSON response
- Thường do endpoint không tồn tại hoặc lỗi trong backend

---

## 🧪 Cách Debug

### 1. Kiểm tra Browser Console
1. Mở `Chrome DevTools` (F12)
2. Tab `Console` - xem console.log messages
3. Tab `Network` - xem requests/responses

### 2. Kiểm tra Backend Logs
Chạy backend và xem output trong terminal:
```bash
cd backend
python app.py
```

### 3. Test API Manually
```bash
curl -X POST http://localhost:5000/api/lessons/1/tests \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Quiz",
    "timeLimitMinutes": 15,
    "attemptsAllowed": 1,
    "isPlacement": false
  }'
```

---

## ✅ Giải Pháp

### Bước 1: Kiểm Tra Endpoint

**Endpoint tạo Test:**
```
POST /api/lessons/<lesson_id>/tests
```

**Expected Response (201):**
```json
{
  "id": 123,
  "lesson_id": 5,
  "title": "Vòng lặp for trong Python - Quiz (AI)",
  "is_placement": false,
  "time_limit_minutes": 15,
  "attempts_allowed": 1,
  "created_at": "2025-11-22T...",
  "updated_at": "2025-11-22T..."
}
```

**Endpoint tạo Question:**
```
POST /api/tests/<test_id>/questions
```

**Request Body:**
```json
{
  "type": "single_choice",
  "content": "Câu hỏi ở đây",
  "points": 1,
  "choices": [
    {
      "content": "Option A",
      "is_correct": true,
      "sort_order": 0
    },
    {
      "content": "Option B",
      "is_correct": false,
      "sort_order": 1
    }
  ]
}
```

### Bước 2: Kiểm Tra Backend Routes

Trong `backend/app/routes/Instructor.py`, đảm bảo có:
```python
@instructor_bp.route("/api/lessons/<int:lesson_id>/tests", methods=['POST'])
def create_test(lesson_id):
    ...

@instructor_bp.route("/api/tests/<int:test_id>/questions", methods=['POST'])
def create_question(test_id):
    ...
```

### Bước 3: Kiểm Tra URL Trong Frontend

Trong `CourseLessons.vue`, URLs phải là:
```javascript
// Tạo test
`http://localhost:5000/api/lessons/${lesson.id}/tests`

// Tạo question
`http://localhost:5000/api/tests/${testId}/questions`
```

### Bước 4: Kiểm Tra Request Body Format

**Đúng:**
```javascript
const qPayload = {
  type: 'single_choice',
  content: q.question,      // ← 'content' không phải 'question'
  points: 1,
  choices: [
    {
      content: opt,
      is_correct: q.correctAnswer === idx,
      sort_order: idx
    }
  ]
};
```

**Sai:**
```javascript
// ❌ WRONG - gửi 'question' thay vì 'content'
const qPayload = {
  question: q.question,
  options: q.options,
  correctAnswer: q.correctAnswer,
  explanation: q.explanation
};
```

---

## 📊 Debugging Steps

### Step 1: Check Console Logs
Mở **Browser DevTools → Console** khi lưu câu hỏi
- Xem `Creating test with payload: ...`
- Xem `Test response status: ...`
- Xem lỗi nào

### Step 2: Check Network Tab
Mở **Browser DevTools → Network**
- Tìm request `POST` tới `/api/lessons/*/tests`
- Click vào → xem `Response` tab
- Nếu là HTML error page → có vấn đề backend

### Step 3: Check Backend Logs
Trong terminal backend:
```bash
ERROR: Failed to create test: ...
```

Hoặc:
```bash
ERROR: Test response status: 500
```

### Step 4: Test Endpoint Directly
```bash
# Test create_test endpoint
curl -X POST http://localhost:5000/api/lessons/1/tests \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","timeLimitMinutes":15}'

# Test create_question endpoint  
curl -X POST http://localhost:5000/api/tests/1/questions \
  -H "Content-Type: application/json" \
  -d '{
    "type":"single_choice",
    "content":"Question?",
    "choices":[{"content":"A","is_correct":true}]
  }'
```

---

## 🚨 Common Issues

### Issue 1: 404 - Lesson Not Found
**Error:** `{"message":"Bài học không tồn tại"}`
- Kiểm tra `lesson.id` có đúng không
- Kiểm tra bài học có tồn tại trong DB không

### Issue 2: 404 - Test Not Found
**Error:** `{"message":"Bài test không tồn tại"}`
- Kiểm tra `testId` được trả về từ create_test
- Kiểm tra Test đã lưu vào DB chưa

### Issue 3: 400 - Missing Required Field
**Error:** `{"message":"Thiếu nội dung câu hỏi (content)"}`
- Đảm bảo gửi `"content"` field (không phải `"question"`)
- Field không được trống

### Issue 4: 500 - Database Error
**Error:** `{"message":"Lỗi khi tạo test: ..."}`
- Check backend logs
- Thường là lỗi constraint, foreign key, etc.

---

## ✅ Checklist

- [ ] Backend running (`python app.py`)
- [ ] Routes được import đúng trong `app.py`
- [ ] URL endpoints đúng
- [ ] Request body fields đúng (`content` không phải `question`)
- [ ] Choices format đúng
- [ ] Lessons tồn tại trong DB
- [ ] Không có JWT requirement cho endpoints
- [ ] CORS được configure

---

## 💡 Quick Fix

Nếu vẫn có vấn đề, chạy:

```python
# backend/debug_test.py
import requests
import json

# Test 1: Create test
res = requests.post(
    'http://localhost:5000/api/lessons/1/tests',
    json={'title': 'Debug Test', 'timeLimitMinutes': 10}
)
print("Create Test:", res.status_code, res.json())

# Test 2: Create question
if res.status_code == 201:
    test_id = res.json()['id']
    res2 = requests.post(
        f'http://localhost:5000/api/tests/{test_id}/questions',
        json={
            'type': 'single_choice',
            'content': 'Test?',
            'choices': [
                {'content': 'A', 'is_correct': True}
            ]
        }
    )
    print("Create Question:", res2.status_code, res2.json())
```

Chạy: `python debug_test.py`
