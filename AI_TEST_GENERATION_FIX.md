# AI Test Generation Fix - Using Lesson Title

## Summary
Updated the AI test generation feature to use the **lesson title** instead of the **test title** when generating quiz questions. This ensures that AI-generated questions are contextually relevant to the lesson content rather than just the test name.

## Changes Made

### 1. Backend - Instructor.py
**File**: `backend/app/routes/Instructor.py`

**What Changed**: Modified the `_serialize_test` function to include the lesson title in the API response.

```python
def _serialize_test(t, include_counters=False):
    data = {
        "id": t.id,
        "lessonId": t.lesson_id,
        "title": t.title,
        "isPlacement": bool(t.is_placement),
        "timeLimitMinutes": t.time_limit_minutes,
        "attemptsAllowed": t.attempts_allowed,
        "createdAt": t.created_at.isoformat() if t.created_at else None,
        "updatedAt": t.updated_at.isoformat() if t.updated_at else None,
    }
    # Include lesson title if available
    if t.lesson:
        data["lessonTitle"] = t.lesson.title
    if include_counters:
        data["questionCount"] = len(t.questions or [])
    return data
```

**Why**: The Test model has a relationship with Lesson (`lesson` backref), which allows us to access `t.lesson.title` to get the lesson's title associated with the test.

---

### 2. Frontend - TestEditor.vue
**File**: `fe/src/components/Instructor/TestEditor.vue`

#### Change 1: Store Lesson Title in Meta Object
**Function**: `fetchTest()`

Added `lessonTitle` to the meta object when loading test details:

```javascript
this.meta = {
  title: data.title || '',
  timeLimitMinutes: data.timeLimitMinutes || 0,
  attemptsAllowed: data.attemptsAllowed || 1,
  isPlacement: !!data.isPlacement,
  lessonTitle: data.lessonTitle || data.title || 'Lesson Quiz', // Use lesson title from API
}
```

**Why**: This stores the lesson title received from the backend API so it can be used throughout the component.

#### Change 2: Use Lesson Title for AI Generation
**Function**: `openAIGenerator()`

Updated the AI generation payload to use the lesson title:

```javascript
const payload = {
  lesson_title: this.meta.lessonTitle || 'Lesson Quiz',
  num_questions: this.aiConfig.num_questions,
  difficulty: this.aiConfig.difficulty,
}
```

**Why**: Previously used `this.meta.title` (test title). Now uses `this.meta.lessonTitle` (lesson title) for more contextually accurate question generation.

---

## How It Works

1. **Backend API**: When fetching test details via `/api/tests/:testId`, the response now includes:
   - `lessonTitle`: The title of the lesson associated with the test (if available)
   
2. **Frontend Loading**: The TestEditor component fetches the test details and stores the lesson title in `this.meta.lessonTitle`

3. **AI Generation**: When the instructor clicks "Generate" in the AI Settings panel:
   - The lesson title is sent to the AI API endpoint (`/api/ai/quiz/generate`)
   - The AI generates questions based on the lesson's context
   - Questions are automatically added to the test

## Benefits

✅ **Better Context**: AI generates questions relevant to the lesson content, not just the test name  
✅ **Improved Quality**: More accurate and meaningful quiz questions  
✅ **Fallback Handling**: If lesson title is unavailable, falls back to test title, then to "Lesson Quiz"  
✅ **No Breaking Changes**: Backward compatible with existing tests

## Testing

To verify this feature works correctly:

1. Create or open a lesson with an associated test
2. Open the Test Editor for that test
3. Click "AI Generator" button
4. Configure number of questions and difficulty
5. Click "Generate"
6. Verify that generated questions are contextually relevant to the lesson (not just the test title)

## Database Relationship

The feature relies on this relationship in the models:
- `Test.lesson_id` → Foreign key to `Lessons.Id`
- `Test.lesson` → Backref relationship to access the `Lesson` object
- `Lesson.title` → The lesson's title used for AI generation

---

**Date**: 2025
**Status**: ✅ Complete
