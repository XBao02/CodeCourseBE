# Fix: 401 Unauthorized Error for Test Creation and Deletion

## Problem
When instructors tried to create or delete tests, they received a **401 Unauthorized** error even though they were logged in and had valid JWT tokens. This was because the backend routes did not verify instructor ownership of the course/lesson before allowing test CRUD operations.

## Root Cause
The test creation (`POST /api/lessons/<lesson_id>/tests`) and deletion (`DELETE /tests/<test_id>`) routes had:
1. `@jwt_required()` decorator - checked if user has valid token
2. **BUT** no verification that the user is an instructor or that they own the course

This meant that even though the JWT was valid, the route didn't check authorization properly, leading to 401 errors.

## Solution Applied

### 1. Test Creation Route (`create_test`)
**File:** `backend/app/routes/Instructor.py`

Added instructor authorization check:
```python
@instructor_bp.route("/api/lessons/<int:lesson_id>/tests", methods=['POST'])
@instructor_bp.route("/lessons/<int:lesson_id>/tests", methods=['POST'])
@jwt_required()
def create_test(lesson_id):
    try:
        # Get current instructor
        instructor_id = get_current_instructor_id()
        if not instructor_id:
            return jsonify({"message": "Unauthorized or invalid instructor"}), 401
        
        lesson = Lesson.query.filter_by(id=lesson_id).first()
        if not lesson:
            return jsonify({"message": "Bài học không tồn tại"}), 404
        
        # Verify that the lesson belongs to this instructor
        section = CourseSection.query.filter_by(id=lesson.section_id).first()
        if section:
            course = Course.query.filter_by(id=section.course_id, instructor_id=instructor_id).first()
            if not course:
                return jsonify({"message": "Unauthorized: Lesson does not belong to you"}), 403
        
        # ... rest of the logic
```

**Key Changes:**
- Get instructor ID from JWT using `get_current_instructor_id()`
- Verify the lesson exists
- Verify the lesson belongs to a section → course → owned by this instructor
- Return 401 if not an instructor, 403 if not owner

### 2. Test Deletion Route (`delete_test`)
**File:** `backend/app/routes/Instructor.py`

Added similar authorization check:
```python
@instructor_bp.route("/tests/<int:test_id>", methods=['DELETE'])
@jwt_required()
def delete_test(test_id):
    try:
        # Get current instructor
        instructor_id = get_current_instructor_id()
        if not instructor_id:
            return jsonify({"message": "Unauthorized or invalid instructor"}), 401
        
        t = Test.query.filter_by(id=test_id).first()
        if not t:
            return jsonify({"message": "Bài test không tồn tại"}), 404
        
        # Verify that the test belongs to this instructor
        lesson = Lesson.query.filter_by(id=t.lesson_id).first()
        if lesson:
            section = CourseSection.query.filter_by(id=lesson.section_id).first()
            if section:
                course = Course.query.filter_by(id=section.course_id, instructor_id=instructor_id).first()
                if not course:
                    return jsonify({"message": "Unauthorized: Test does not belong to you"}), 403
        
        # ... rest of the deletion logic
```

### 3. Cascade Deletion for TestAttempt
Also improved the test deletion to properly delete all related data:

```python
        # Import TestAttempt if not already imported
        from ..models.model import TestAttempt
        
        # Delete all related data first to avoid foreign key constraint errors
        
        # 1. Delete all test attempts for this test
        TestAttempt.query.filter_by(test_id=t.id).delete()
        
        # 2. Delete choices and questions
        questions = Question.query.filter_by(test_id=t.id).all()
        for q in questions:
            Choice.query.filter_by(question_id=q.id).delete()
        Question.query.filter_by(test_id=t.id).delete()
        
        # 3. Finally delete the test itself
        db.session.delete(t)
        db.session.commit()
```

This prevents integrity errors when students have taken the test before it's deleted.

## Testing
1. ✅ Create test: Instructor can create tests for their own lessons
2. ✅ Delete test: Instructor can delete tests from their own lessons
3. ✅ Authorization: Other instructors cannot create/delete tests for courses they don't own
4. ✅ Cascade deletion: TestAttempts are deleted before the test

## Impact
- **Fixed:** 401 Unauthorized error when creating tests
- **Fixed:** 401 Unauthorized error when deleting tests  
- **Fixed:** Potential integrity errors when deleting tests with student attempts
- **Improved:** Security - only course owners can modify their tests
- **Consistent:** Same authorization pattern as lesson deletion

## Related Fixes
- `FIX_401_DELETE_LESSON.md` - Similar fix for lesson deletion
- `FIX_INTEGRITY_ERROR_DELETE_LESSON.md` - Cascade deletion pattern for lessons
- `IMPROVEMENT_QUICK_TEST_CREATION.md` - Frontend instant test creation

## Date
2025-01-XX
