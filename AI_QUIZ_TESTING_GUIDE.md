# AI Quiz Generation Testing Guide

## Vấn Đề
Bạn nhận thấy rằng AI tạo câu hỏi không đúng với tên bài học. Test này sẽ giúp xác định vấn đề.

## Các File Test

### 1. `backend/test_ai_quiz_quick.py` - Test Nhanh ⚡
Test nhanh để kiểm tra xem tên bài học có được truyền vào prompt AI không.

**Chạy:**
```bash
cd backend
python test_ai_quiz_quick.py
```

**Kiểm tra:**
- ✅ Tên bài học có xuất hiện trong prompt gửi đến AI
- ✅ Prompt có đúng format không
- ✅ Các tham số (số câu hỏi, độ khó) có được truyền đúng không

### 2. `backend/test_ai_quiz.py` - Test Đầy Đủ 🔬
Test toàn diện bao gồm cả việc gọi API Gemini thực tế.

**Chạy:**
```bash
cd backend
python test_ai_quiz.py
```

**Yêu cầu:**
- Cần có API key trong `.env` (GEMINI_API_KEY hoặc GOOGLE_API_KEY)

**Kiểm tra:**
1. ✅ Prompt generation với tên bài học
2. ✅ JSON parsing từ response AI
3. ✅ Frontend integration simulation
4. ✅ Common issues detection
5. ✅ Live AI generation (gọi API thực tế)

### 3. `test_ai_quiz.bat` - Windows Batch Script 💻
Chạy test nhanh với một click.

**Chạy:**
- Double click `test_ai_quiz.bat`

## Kết Quả Mong Đợi

### ✅ PASS - Nếu tất cả đúng:
```
✅ ALL TESTS PASSED - Lesson titles are correctly used!

Test Results:
1. ✅ PASS: 'Introduction to Python Variables'
   → Found in prompt ✓
2. ✅ PASS: 'JavaScript Arrow Functions'
   → Found in prompt ✓
...
```

### ❌ FAIL - Nếu có vấn đề:
```
❌ SOME TESTS FAILED - Check the prompt generation!

Test Results:
1. ❌ FAIL: 'Introduction to Python Variables'
   → NOT found in prompt ✗
```

## Phân Tích Vấn Đề

### Vấn Đề 1: Frontend Không Gửi Đúng Tên Bài Học

**Kiểm tra:** `fe/src/components/Instructor/TestEditor.vue`

**Code cũ (SAI):**
```javascript
const payload = {
  lesson_title: this.test.title,  // ❌ SAI - dùng tên test
  num_questions: this.aiQuizConfig.num_questions,
  difficulty: this.aiQuizConfig.difficulty,
};
```

**Code mới (ĐÚNG):**
```javascript
const payload = {
  lesson_title: this.lesson.title,  // ✅ ĐÚNG - dùng tên bài học
  num_questions: this.aiQuizConfig.num_questions,
  difficulty: this.aiQuizConfig.difficulty,
};
```

### Vấn Đề 2: Backend Không Xử Lý Đúng Tên Bài Học

**Kiểm tra:** `backend/app/routes/AIQuiz.py`

Hàm `_generate_quiz_prompt` phải bao gồm `lesson_title`:

```python
def _generate_quiz_prompt(lesson_title: str, num_questions: int = 5, difficulty: str = "medium") -> str:
    prompt = f"""Create {num_questions} multiple-choice quiz questions about the lesson: "{lesson_title}"
    
    Difficulty level: {difficulty}
    ...
    """
    return prompt
```

### Vấn Đề 3: API Key Không Được Cấu Hình

**Kiểm tra:** `.env` file

```env
GEMINI_API_KEY=your-api-key-here
# hoặc
GOOGLE_API_KEY=your-api-key-here
```

## Các Bước Debug

### Bước 1: Chạy Quick Test
```bash
python backend/test_ai_quiz_quick.py
```

Nếu FAIL → Vấn đề ở prompt generation (backend)

### Bước 2: Kiểm tra Frontend
Mở browser DevTools → Network tab → Xem request gửi đến `/api/ai/quiz/generate`

Kiểm tra request body:
```json
{
  "lesson_title": "Tên Bài Học Thực Tế",  // ← Phải là tên bài học, không phải tên test
  "num_questions": 5,
  "difficulty": "medium"
}
```

### Bước 3: Kiểm tra Backend Logs
```bash
cd backend
tail -f debug.log
```

Xem logs khi generate quiz:
- Có nhận được `lesson_title` đúng không?
- Prompt có chứa tên bài học không?
- AI response có liên quan đến bài học không?

### Bước 4: Test với API Thực Tế
```bash
python backend/test_ai_quiz.py
```

Xem phần "Relevance Score" - nếu < 60% có vấn đề.

## Fix Đã Áp Dụng

### ✅ Fix 1: TestEditor.vue - Sử dụng Tên Bài Học
**File:** `fe/src/components/Instructor/TestEditor.vue`

**Thay đổi:** Sử dụng `lesson.title` thay vì `test.title`

```javascript
// Trong method generateAIQuestions()
const payload = {
  lesson_title: this.lesson.title,  // ✅ Dùng tên bài học
  num_questions: this.aiQuizConfig.num_questions,
  difficulty: this.aiQuizConfig.difficulty,
};
```

### ✅ Fix 2: AIQuiz.py - Kiểm Tra Prompt
**File:** `backend/app/routes/AIQuiz.py`

Hàm `_generate_quiz_prompt()` đã đúng - bao gồm `lesson_title` trong prompt.

## Kết Quả Sau Khi Fix

### Trước Fix (SAI):
```
Test Name: "Test" (default)
AI Generated Questions: About generic programming (không liên quan đến bài học cụ thể)
```

### Sau Fix (ĐÚNG):
```
Lesson Name: "React useState Hook"
AI Generated Questions: 
1. What does useState return?
2. How do you update state in React?
3. What is the initial state parameter?
(All questions related to React useState)
```

## Test Cases Cụ Thể

### Test Case 1: Python Lesson
```python
{
  "lesson_title": "Python For Loops and Iteration",
  "num_questions": 5,
  "difficulty": "medium"
}
```

**Expected:** Câu hỏi về for loops, iteration, range(), etc.

### Test Case 2: JavaScript Lesson
```python
{
  "lesson_title": "JavaScript ES6 Arrow Functions",
  "num_questions": 3,
  "difficulty": "easy"
}
```

**Expected:** Câu hỏi về arrow function syntax, this binding, etc.

### Test Case 3: React Lesson
```python
{
  "lesson_title": "React Hooks: useState and useEffect",
  "num_questions": 4,
  "difficulty": "hard"
}
```

**Expected:** Câu hỏi về useState, useEffect, dependencies, cleanup, etc.

## Metrics để Đánh Giá

### Relevance Score
```
Relevance Score = (Số câu có keywords từ lesson title / Tổng số câu) × 100%
```

**Đánh giá:**
- 90-100%: Excellent ⭐⭐⭐⭐⭐
- 70-89%: Good ⭐⭐⭐⭐
- 60-69%: Acceptable ⭐⭐⭐
- < 60%: Poor - Cần fix ❌

## Troubleshooting

### Vấn đề: Test báo "API key NOT found"
**Fix:** Tạo file `.env` trong folder `backend/` với:
```env
GEMINI_API_KEY=your-key-here
```

### Vấn đề: Import errors
**Fix:** 
```bash
cd backend
pip install -r requirements.txt
```

### Vấn đề: "No module named 'app'"
**Fix:** Đảm bảo chạy từ folder `backend/`:
```bash
cd backend
python test_ai_quiz.py
```

### Vấn đề: AI tạo câu không liên quan
**Kiểm tra:**
1. Frontend có gửi đúng `lesson_title` không?
2. Prompt có chứa `lesson_title` không?
3. API key có hợp lệ không?

## Kết Luận

Sau khi chạy test, bạn sẽ biết chính xác:
1. ✅ Tên bài học có được truyền vào prompt AI
2. ✅ Câu hỏi AI generate có liên quan đến bài học
3. ✅ Toàn bộ flow từ frontend → backend → AI có hoạt động đúng

**Khi nào cần chạy test:**
- Sau khi fix bug liên quan đến AI quiz
- Khi thêm/sửa TestEditor.vue
- Khi thay đổi AIQuiz.py
- Trước khi deploy lên production

---

**Tạo bởi:** Development Team  
**Mục đích:** Verify AI quiz generation uses correct lesson titles  
**Liên quan:** TestEditor.vue, AIQuiz.py, IMPROVEMENT_TEST_EDITOR_AI.md
