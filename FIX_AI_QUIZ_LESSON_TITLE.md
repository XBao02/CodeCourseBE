# FIX: AI Quiz Generation Using Wrong Title

## Problem Description

AI quiz generation was **not using the lesson title** when generating questions. Instead, it was using the test title (or default "Lesson Quiz"), resulting in generic or irrelevant questions.

## Root Cause Analysis

### Flow Overview
1. **Frontend (TestEditor.vue)** → Calls `/api/tests/<test_id>` to get test details
2. **Backend API** → Returns test data (title, questions, etc.)
3. **Frontend** → Expects `lessonTitle` field in response
4. **Frontend** → Uses `lessonTitle` when calling AI generation endpoint
5. **Backend (AIQuiz.py)** → Generates questions based on lesson title

### The Bug 🐛

**Backend API `/api/tests/<test_id>` was NOT returning `lessonTitle`:**

```python
# ❌ BEFORE (Missing lessonTitle)
res = {
    'id': test.id,
    'title': test.title,
    'timeLimitMinutes': test.time_limit_minutes or 0,
    'attemptsAllowed': test.attempts_allowed or 1,
    'isPlacement': bool(test.is_placement)
}
```

**Frontend was trying to use it:**
```javascript
// TestEditor.vue - fetchTest()
this.meta = {
  title: data.title || '',
  lessonTitle: data.lessonTitle || data.title || 'Lesson Quiz', // ⚠️ lessonTitle missing!
}
```

**AI generation was using fallback:**
```javascript
// TestEditor.vue - openAIGenerator()
const payload = {
  lesson_title: this.meta.lessonTitle || 'Lesson Quiz', // ⚠️ Always "Lesson Quiz"!
  num_questions: this.aiConfig.num_questions,
  difficulty: this.aiConfig.difficulty,
}
```

### Result
- AI received **test title** (e.g., "Test") or **"Lesson Quiz"** as the lesson title
- Generated questions were **generic and not specific to the actual lesson content**
- For example:
  - Actual lesson: "Introduction to Python Variables"
  - AI received: "Test" or "Lesson Quiz"
  - Generated questions: Generic Python questions instead of variable-specific questions

## Solution ✅

### Backend Fix (Instructor.py)

Added `lessonTitle` to the API response:

```python
# ✅ AFTER (With lessonTitle)
@instructor_bp.route('/api/tests/<int:test_id>', methods=['GET'])
@jwt_required()
def get_test(test_id):
    try:
        test = Test.query.get(test_id)
        if not test:
            return jsonify({'message': 'Test not found'}), 404

        # Get lesson title for AI generation
        lesson_title = None
        if test.lesson:
            lesson_title = test.lesson.title

        res = {
            'id': test.id,
            'title': test.title,
            'lessonTitle': lesson_title,  # ✅ Now included!
            'timeLimitMinutes': test.time_limit_minutes or 0,
            'attemptsAllowed': test.attempts_allowed or 1,
            'isPlacement': bool(test.is_placement)
        }
        
        # ... rest of the code
```

### Frontend (Already Correct)

Frontend code was already expecting and using `lessonTitle` correctly:

```javascript
// TestEditor.vue - fetchTest()
this.meta = {
  title: data.title || '',
  lessonTitle: data.lessonTitle || data.title || 'Lesson Quiz', // ✅ Now receives actual lesson title
  timeLimitMinutes: data.timeLimitMinutes || 0,
  attemptsAllowed: data.attemptsAllowed || 1,
  isPlacement: !!data.isPlacement,
}

// TestEditor.vue - openAIGenerator()
const payload = {
  lesson_title: this.meta.lessonTitle || 'Lesson Quiz', // ✅ Now uses actual lesson title
  num_questions: this.aiConfig.num_questions,
  difficulty: this.aiConfig.difficulty,
}
```

## Files Modified

### 1. Backend: `backend/app/routes/Instructor.py`
- **Function:** `get_test(test_id)`
- **Line:** ~910
- **Change:** Added `lessonTitle` field to API response

### 2. Test File Created: `backend/test_ai_quiz_lesson_title.py`
- Quick test to verify AI prompt includes lesson title
- Run: `python test_ai_quiz_lesson_title.py`

## Testing

### Manual Test Steps

1. **Create a lesson** with a specific title (e.g., "Introduction to Python Variables")
2. **Create a test** for that lesson
3. **Open Test Editor** → Click "AI Generator"
4. **Generate questions** → Questions should now be specific to "Python Variables"

### Expected Behavior

**Before Fix:**
```
Lesson: "Introduction to Python Variables"
AI receives: "Test" or "Lesson Quiz"
Generated: Generic programming questions
```

**After Fix:**
```
Lesson: "Introduction to Python Variables"
AI receives: "Introduction to Python Variables"
Generated: Questions specifically about Python variables
```

### Automated Test

Run the test script:
```bash
cd backend
python test_ai_quiz_lesson_title.py
```

Expected output:
```
================================================================================
TEST: AI Quiz Prompt Generation - Lesson Title Check
================================================================================

🧪 Test Case 1:
   Lesson Title: 'Introduction to Python Variables'
   Questions: 5
   Difficulty: medium
   ✅ PASS: Lesson title found in prompt
   ✅ PASS: Difficulty level found in prompt
   ✅ PASS: Number of questions found in prompt

================================================================================
✅ ALL TESTS PASSED
================================================================================
```

## Impact

### User Experience Improvement
- ✅ **Relevant Questions:** AI now generates questions specific to the lesson topic
- ✅ **Better Learning:** Students get targeted practice on lesson content
- ✅ **Time Savings:** Instructors don't need to manually fix irrelevant AI-generated questions

### Example Scenarios

#### Scenario 1: Python Variables Lesson
- **Lesson Title:** "Introduction to Python Variables"
- **AI Prompt:** "Create questions about: Introduction to Python Variables"
- **Generated Questions:**
  - "What is a variable in Python?"
  - "How do you assign a value to a variable?"
  - "What are the naming rules for Python variables?"

#### Scenario 2: JavaScript Arrow Functions
- **Lesson Title:** "ES6 Arrow Functions"
- **AI Prompt:** "Create questions about: ES6 Arrow Functions"
- **Generated Questions:**
  - "What is the syntax of an arrow function?"
  - "How do arrow functions handle the 'this' keyword?"
  - "When should you use arrow functions vs regular functions?"

## API Response Schema

### GET /api/tests/:test_id

**Before:**
```json
{
  "id": 123,
  "title": "Test",
  "timeLimitMinutes": 0,
  "attemptsAllowed": 1,
  "isPlacement": false,
  "questions": [...]
}
```

**After:**
```json
{
  "id": 123,
  "title": "Test",
  "lessonTitle": "Introduction to Python Variables",  ← NEW!
  "timeLimitMinutes": 0,
  "attemptsAllowed": 1,
  "isPlacement": false,
  "questions": [...]
}
```

## Related Documentation

- `SIMPLIFY_TEST_CREATION.md` - Test creation simplification
- `TEST_CREATION_UX_COMPLETE.md` - Complete test UX improvements
- `backend/app/routes/AIQuiz.py` - AI quiz generation logic

## Notes

- The fix is **backwards compatible** - if `test.lesson` is None, `lessonTitle` will be None
- Frontend already has fallback logic: `data.lessonTitle || data.title || 'Lesson Quiz'`
- This fix **does not require database migrations** - just code changes

---

**Status:** ✅ Fixed and Tested  
**Priority:** High (Critical for AI quiz quality)  
**Type:** Bug Fix  
**Date:** 2024-12-05
