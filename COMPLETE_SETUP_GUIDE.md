# Complete Setup & Testing Guide - AI Quiz Feature

## 📋 Prerequisites

- Python 3.8+
- Node.js 14+
- MySQL 5.7+
- Gemini API Key (from Google AI Studio)

## 🔧 Backend Setup

### 1. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create or update `.env` file in `backend/` directory:

```env
# Database
DATABASE_URL=mysql+pymysql://root:123@localhost:3306/CodeCourse

# Flask
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
FLASK_DEBUG=1

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://localhost:8080

# Gemini API
GEMINI_API_KEY=your-gemini-api-key-here

# Server
HOST=0.0.0.0
PORT=5000
```

### 3. Get Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click "Create API key"
3. Copy the key and add it to `.env` as `GEMINI_API_KEY`

### 4. Start Backend Server

```bash
cd backend
python app.py
```

Expected output:
```
 * Running on http://0.0.0.0:5000
 * Debug mode: on
```

## 🎨 Frontend Setup

### 1. Install Node Dependencies

```bash
cd fe
npm install
```

### 2. Start Frontend Server

```bash
cd fe
npm run dev
```

Expected output:
```
  VITE v5.x.x
  ➜  Local:   http://localhost:5173/
```

## ✅ Testing the AI Quiz Feature

### Test Flow

#### Step 1: Login as Instructor

1. Go to `http://localhost:5173`
2. Click "Đăng Nhập" (Login)
3. Enter instructor credentials:
   - Email: `instructor@example.com`
   - Password: `password123`

#### Step 2: Navigate to Lessons

1. Click "Khóa Học Của Tôi" (My Courses)
2. Select a course
3. Click on "Chỉnh sửa bài học" (Edit Lesson) for any lesson

#### Step 3: Generate AI Quiz

1. Scroll down in the lesson editor
2. Find the button "Tạo câu hỏi bằng AI" (Create Questions with AI)
3. Click it to open the AI Quiz modal

#### Step 4: Configure Quiz Settings

The modal should show:
- Lesson title
- Number of questions input field
- Difficulty level dropdown
- Topic/Subject input field

Configure settings:
- Number of questions: 5
- Difficulty: Medium
- Topic: JavaScript

Click "Tạo Quiz" (Create Quiz) button

#### Step 5: Review Generated Questions

Wait for questions to be generated (usually 5-10 seconds)

You should see:
- Question text
- Multiple choice options
- Correct answer highlighted
- Action buttons (Edit, Regenerate)

#### Step 6: Save Questions

Click "Lưu Câu Hỏi" (Save Questions)

### ✨ Expected Behavior

**When you click "Lưu Câu Hỏi":**

✅ **Immediate:**
- Modal closes instantly
- No alert/notification shown
- No loading spinner remains

✅ **Within 1-2 seconds:**
- Tests list reloads automatically
- New test appears in the lessons table with title: `{LessonTitle} - Quiz (AI)`
- Questions count shown: "5 câu hỏi" (or actual count)

### 📊 Verification Checklist

- [ ] Backend server running without errors
- [ ] Frontend loads successfully
- [ ] Login works correctly
- [ ] Can navigate to lesson editor
- [ ] "Tạo câu hỏi bằng AI" button visible
- [ ] AI modal opens properly
- [ ] Questions generate successfully
- [ ] Questions display with all options
- [ ] Modal closes immediately when saving
- [ ] No error alerts shown
- [ ] New test appears in list
- [ ] Test has correct number of questions

## 🐛 Troubleshooting

### Issue: "GEMINI_API_KEY not configured"

**Solution:**
1. Go to `backend/.env`
2. Add: `GEMINI_API_KEY=your-actual-key`
3. Restart backend server

### Issue: Backend returns HTML instead of JSON

**Check:**
1. Are there any Python syntax errors?
   ```bash
   python -m py_compile app/routes/AIQuiz.py
   python -m py_compile app/routes/Instructor.py
   ```

2. Check backend console for error messages
3. Verify blueprints are registered (run this in terminal):
   ```bash
   python -c "from app import app; print([b for b in app.blueprints])"
   ```

### Issue: Questions don't generate

**Check:**
1. Is Gemini API key valid?
2. Check browser console (F12) for errors
3. Check backend console for error messages
4. Try generating with simpler topic/settings

### Issue: Modal doesn't close after saving

**Check:**
1. Are there JavaScript errors? (Open DevTools)
2. Check if questions were actually saved in backend
3. Try refreshing the page

## 📡 API Endpoints Reference

### Create Test
```
POST /api/lessons/<lesson_id>/tests
Content-Type: application/json

{
  "title": "Test Title",
  "timeLimitMinutes": 15,
  "attemptsAllowed": 1,
  "isPlacement": false
}

Response: { "id": 123, ... }
```

### Create Question
```
POST /api/tests/<test_id>/questions
Content-Type: application/json

{
  "type": "single_choice",
  "content": "Question text?",
  "points": 1,
  "choices": [
    {
      "content": "Option 1",
      "is_correct": false,
      "sort_order": 0
    },
    {
      "content": "Option 2",
      "is_correct": true,
      "sort_order": 1
    }
  ]
}

Response: { "id": 456, ... }
```

### Generate Questions (Gemini)
```
POST /api/ai/generate-questions
Content-Type: application/json

{
  "topic": "JavaScript",
  "numQuestions": 5,
  "difficulty": "medium"
}

Response: [
  {
    "question": "...",
    "options": ["opt1", "opt2", ...],
    "correctAnswer": 0
  },
  ...
]
```

## 🔍 Debug Mode

### Check Network Requests

1. Open browser DevTools (F12)
2. Go to Network tab
3. Generate questions and save
4. You should see:
   - `POST /api/lessons/{id}/tests` → 201
   - `POST /api/tests/{id}/questions` → 201 (multiple)

### Check Backend Logs

Look for messages like:
```
Creating test with payload: {...}
Test response status: 201
Created test with ID: 123
Creating question with payload: {...}
Question saved successfully
```

### Check Database

```sql
-- Check if test was created
SELECT * FROM Test ORDER BY created_at DESC LIMIT 1;

-- Check if questions were saved
SELECT * FROM Question ORDER BY created_at DESC LIMIT 5;

-- Check choices
SELECT * FROM Choice ORDER BY created_at DESC LIMIT 10;
```

## 📝 Quick Test Script

Save this as `test_ai_quiz.js` in frontend directory:

```javascript
// Test AI endpoints
async function testAIQuiz() {
  try {
    // Generate questions
    const genRes = await fetch('http://localhost:5000/api/ai/generate-questions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        topic: 'JavaScript',
        numQuestions: 3,
        difficulty: 'easy'
      })
    });
    
    console.log('Generate Response:', genRes.status);
    const questions = await genRes.json();
    console.log('Generated Questions:', questions);
    
    // Create test
    const testRes = await fetch('http://localhost:5000/api/lessons/1/tests', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: 'Test Quiz',
        timeLimitMinutes: 10,
        attemptsAllowed: 1
      })
    });
    
    console.log('Test Creation Response:', testRes.status);
    const test = await testRes.json();
    console.log('Created Test:', test);
    
  } catch (e) {
    console.error('Error:', e);
  }
}

testAIQuiz();
```

## 🎯 Performance Notes

- Question generation: 3-10 seconds (depends on Gemini API response time)
- Saving questions: < 1 second per question
- Modal close: Instant (no animation)
- List reload: < 1 second

## 📚 Additional Resources

- Gemini API Documentation: https://ai.google.dev/tutorials/python_quickstart
- Flask Documentation: https://flask.palletsprojects.com/
- Vue.js Documentation: https://vuejs.org/
- SQLAlchemy Documentation: https://docs.sqlalchemy.org/

---

**Created**: 2024
**Last Updated**: Current
**Status**: ✅ Ready for testing
