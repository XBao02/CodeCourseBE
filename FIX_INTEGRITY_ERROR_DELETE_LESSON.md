# Fix: Lỗi IntegrityError Khi Xóa Bài Học

## ❌ Vấn Đề
Khi xóa bài học, xuất hiện lỗi database constraint:
```
IntegrityError: (pymysql.err.IntegrityError) (1048, "Column 'LessonId' cannot be null")
[SQL: UPDATE `LessonProgress` SET `LessonId`=%(LessonId)s WHERE `LessonProgress`.`Id` = %(LessonProgress_Id)s]
[parameters: {'LessonId': None, 'LessonProgress_Id': 1}]
```

## 🔍 Nguyên Nhân
- Khi xóa lesson, database cố gắng **UPDATE** bảng `LessonProgress` để set `LessonId = NULL`
- Nhưng cột `LessonId` trong bảng `LessonProgress` có constraint **NOT NULL**
- Do đó database không thể set NULL → lỗi IntegrityError

### Tại Sao Lại UPDATE Thay Vì DELETE?
SQLAlchemy có thể được cấu hình với các relationship behaviors:
- **CASCADE DELETE**: Tự động xóa các bản ghi con khi xóa cha
- **SET NULL**: Cố gắng set NULL cho foreign key khi xóa cha
- **RESTRICT**: Không cho phép xóa nếu có bản ghi con

Trong trường hợp này, relationship có thể đang dùng SET NULL hoặc không có CASCADE DELETE.

## ✅ Giải Pháp
Xóa **tất cả dữ liệu liên quan** theo đúng thứ tự trước khi xóa lesson.

### Thứ Tự Xóa (Quan Trọng!)
```
1. TestAttempt (học sinh làm test)
   ↓
2. Choice (các lựa chọn của câu hỏi)
   ↓
3. Question (câu hỏi trong test)
   ↓
4. Test (bài test của lesson)
   ↓
5. LessonProgress (tiến độ học của học sinh)
   ↓
6. Lesson (bài học chính)
```

### Code Đã Sửa

**File**: `backend/app/routes/Instructor.py`

```python
@instructor_bp.route("/api/lessons/<int:lesson_id>", methods=['DELETE'])
@instructor_bp.route("/lessons/<int:lesson_id>", methods=['DELETE'])
@jwt_required()
def delete_lesson(lesson_id):
    try:
        # Verify instructor authorization
        instructor_id = get_current_instructor_id()
        if not instructor_id:
            return jsonify({"message": "Unauthorized: Not an instructor"}), 401
        
        lesson = Lesson.query.filter_by(id=lesson_id).first()
        if not lesson:
            return jsonify({"message": "Bài học không tồn tại"}), 404
        
        # Verify lesson belongs to instructor's course
        section = CourseSection.query.filter_by(id=lesson.section_id).first()
        if section:
            course = Course.query.filter_by(id=section.course_id, instructor_id=instructor_id).first()
            if not course:
                return jsonify({"message": "Unauthorized: Lesson does not belong to you"}), 403
        
        # Import models cần thiết
        from ..models.model import LessonProgress, TestAttempt
        
        # Delete all related data first to avoid foreign key constraint errors
        
        # 1. Delete all test attempts related to tests in this lesson
        tests = Test.query.filter_by(lesson_id=lesson_id).all()
        for test in tests:
            # Delete test attempts
            TestAttempt.query.filter_by(test_id=test.id).delete()
            # Delete choices for all questions in this test
            questions = Question.query.filter_by(test_id=test.id).all()
            for question in questions:
                Choice.query.filter_by(question_id=question.id).delete()
            # Delete all questions
            Question.query.filter_by(test_id=test.id).delete()
        
        # 2. Delete all tests in this lesson
        Test.query.filter_by(lesson_id=lesson_id).delete()
        
        # 3. Delete all lesson progress records
        LessonProgress.query.filter_by(lesson_id=lesson_id).delete()
        
        # 4. Finally delete the lesson itself
        db.session.delete(lesson)
        db.session.commit()
        
        return jsonify({"message": "Đã xóa bài học"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Lỗi khi xóa lesson: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"message": f"Lỗi khi xóa lesson: {str(e)}"}), 500
```

## 📊 Database Schema Liên Quan

```
Course (1) ─────┐
                │
CourseSections (N) ────┐
                       │
Lessons (N) ───────────┼─────────┐
    │                  │         │
    ├─ LessonProgress (N)        │
    │                            │
    └─ Tests (N) ────────────────┤
           │                     │
           ├─ TestAttempt (N)    │
           │                     │
           └─ Questions (N) ─────┤
                  │               │
                  └─ Choice (N)   │
```

## 🧪 Test Lại

### 1. Khởi Động Lại Backend
```powershell
cd backend
python app.py
```

### 2. Test Xóa Lesson
1. Login với tài khoản instructor
2. Vào **Course Content Management**
3. Expand một section
4. Click **Delete** trên một lesson có:
   - ✅ Tests
   - ✅ Questions
   - ✅ Student progress
   - ✅ Test attempts
5. Xác nhận xóa

**Kết quả mong đợi**:
- ✅ Lesson được xóa thành công
- ✅ Tất cả dữ liệu liên quan cũng bị xóa
- ✅ Không có lỗi IntegrityError
- ✅ Frontend refresh và hiển thị danh sách mới

## 🔍 Debug Tips

### Kiểm Tra Dữ Liệu Liên Quan Trước Khi Xóa
```python
# Thêm vào đầu hàm delete_lesson để debug
print(f"Deleting lesson {lesson_id}")
print(f"Tests: {Test.query.filter_by(lesson_id=lesson_id).count()}")
print(f"Progress: {LessonProgress.query.filter_by(lesson_id=lesson_id).count()}")
```

### Xem SQL Queries
Thêm vào `config.py`:
```python
SQLALCHEMY_ECHO = True  # Log tất cả SQL queries
```

### Check Database Constraints
```sql
SHOW CREATE TABLE LessonProgress;
```

## 🛠️ Giải Pháp Thay Thế (Không Khuyến Nghị)

### Option 1: CASCADE DELETE Ở Database Level
Sửa foreign key constraint trong database:
```sql
ALTER TABLE LessonProgress
DROP FOREIGN KEY fk_lesson;

ALTER TABLE LessonProgress
ADD CONSTRAINT fk_lesson
FOREIGN KEY (LessonId) REFERENCES Lessons(Id)
ON DELETE CASCADE;
```

**Ưu điểm**: Tự động xóa con khi xóa cha  
**Nhược điểm**: Mất kiểm soát, dễ xóa nhầm dữ liệu

### Option 2: Soft Delete
Thêm cột `is_deleted` thay vì xóa thật:
```python
lesson.is_deleted = True
db.session.commit()
```

**Ưu điểm**: Có thể khôi phục  
**Nhược điểm**: Cần sửa nhiều queries

## 📝 Best Practices

### ✅ DO
- Xóa dữ liệu con trước khi xóa cha
- Sử dụng transaction (rollback nếu lỗi)
- Log chi tiết để debug
- Kiểm tra quyền trước khi xóa

### ❌ DON'T
- Không xóa trực tiếp mà không kiểm tra relationship
- Không dùng CASCADE DELETE ở khắp nơi
- Không skip authorization check
- Không xóa dữ liệu production mà không backup

## 📌 Checklist

- [x] Thêm code xóa TestAttempt
- [x] Thêm code xóa Choice và Question
- [x] Thêm code xóa Test
- [x] Thêm code xóa LessonProgress
- [x] Xóa Lesson cuối cùng
- [x] Thêm error handling và logging
- [ ] **Khởi động lại backend** ⚠️
- [ ] Test xóa lesson có dữ liệu liên quan
- [ ] Test xóa lesson không có dữ liệu
- [ ] Verify database sau khi xóa

## 🎯 Các Model Liên Quan

```python
# backend/app/models/model.py

class Lesson:
    id
    section_id (FK → CourseSections)
    # Relationships:
    - tests (1:N → Test)
    - progress (1:N → LessonProgress)

class Test:
    id
    lesson_id (FK → Lessons)
    # Relationships:
    - questions (1:N → Question)
    - attempts (1:N → TestAttempt)

class Question:
    id
    test_id (FK → Tests)
    # Relationships:
    - choices (1:N → Choice)

class LessonProgress:
    id
    lesson_id (FK → Lessons, NOT NULL)
    student_id (FK → Students)

class TestAttempt:
    id
    test_id (FK → Tests)
    student_id (FK → Students)

class Choice:
    id
    question_id (FK → Questions)
```

---

**Ngày**: 2025-12-05  
**Trạng thái**: ✅ **ĐÃ SỬA**  
**Lỗi**: IntegrityError - Column 'LessonId' cannot be null  
**Giải pháp**: Xóa tất cả dữ liệu liên quan theo đúng thứ tự  
**Commit message**: `fix: cascade delete all related data when deleting lesson`
