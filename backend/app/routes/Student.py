from flask import Blueprint, jsonify, request
from datetime import datetime
from app.models import db, Course, Enrollment, StudyPlan, PlanItem, Student
from app.models.model import User, LessonProgress

# Note: url_prefix is set when registering the blueprint in app/__init__.py
student_bp = Blueprint('student_bp', __name__)


# ✅ 1. Lấy danh sách tất cả khóa học (hiển thị bên trái)
@student_bp.route('/courses', methods=['GET'])
def get_all_courses():
    courses = Course.query.all()

    # Determine current student (temporary simple auth replacement)
    student = Student.query.first()
    enrolled_course_ids = set()
    if student:
        # Chỉ lấy các enrollment có status='active' (đã đăng ký thành công)
        # Sử dụng filter chính xác với điều kiện status='active'
        enrollments = Enrollment.query.filter(
            Enrollment.student_id == student.id,
            Enrollment.status == 'active'
        ).all()
        enrolled_course_ids = {e.course_id for e in enrollments}

    data = []
    for c in courses:
        data.append({
            'id': c.id,
            'instructorId': c.instructor_id,
            'title': c.title,
            'slug': c.slug,
            'description': c.description,
            'level': c.level,
            'price': float(c.price) if c.price is not None else 0,
            'currency': c.currency,
            'isPublic': c.is_public,
            'createdAt': str(c.created_at),
            'updatedAt': str(c.updated_at),
            'image': None,
            'isRegistered': c.id in enrolled_course_ids,  # Chỉ true nếu có enrollment với status='active'
        })
    return jsonify({"courses": data}), 200


# ✅ 2. Lấy danh sách khóa học mà sinh viên đã đăng ký
@student_bp.route('/my-courses', methods=['GET'])
def get_my_courses():
    try:
        # Determine current student (temporary simple auth replacement)
        student = Student.query.first()
        if not student:
            # Nếu chưa có student, trả về mảng rỗng
            print("⚠️ Không có student nào trong database")
            return jsonify({"courses": []}), 200

        # Debug: Kiểm tra tất cả enrollment của student
        all_enrollments = Enrollment.query.filter_by(student_id=student.id).all()
        print(f"🔍 Tổng số enrollment của student {student.id}: {len(all_enrollments)}")
        for e in all_enrollments:
            print(f"  - Enrollment ID {e.id}: course_id={e.course_id}, status='{e.status}'")

        # CHỈ lấy các enrollment có status='active' (đã đăng ký thành công)
        # Sử dụng filter chính xác với điều kiện status='active'
        enrollments = Enrollment.query.filter(
            Enrollment.student_id == student.id,
            Enrollment.status == 'active'
        ).all()
        
        print(f"✅ Số enrollment có status='active': {len(enrollments)}")
        
        # Nếu không có enrollment nào với status='active', trả về mảng rỗng
        if not enrollments or len(enrollments) == 0:
            print("✅ Không có enrollment nào với status='active' - trả về mảng rỗng")
            return jsonify({"courses": []}), 200
        
        data = []
        for e in enrollments:
            course = Course.query.get(e.course_id)
            # Chỉ thêm vào danh sách nếu course tồn tại
            if course:
                data.append({
                    'id': course.id,
                    'title': course.title,
                    'slug': course.slug,
                    'level': course.level,
                    'price': float(course.price) if course.price is not None else 0,
                    'currency': course.currency,
                    'image': None,
                    'isPublic': course.is_public,
                    'createdAt': str(course.created_at),
                    'updatedAt': str(course.updated_at)
                })
                print(f"✅ Đã thêm khóa học: {course.title} (ID: {course.id})")
            else:
                print(f"⚠️ Không tìm thấy course với ID: {e.course_id}")
        
        print(f"✅ Trả về {len(data)} khóa học đã đăng ký")
        # Đảm bảo luôn trả về mảng (không bao giờ None)
        return jsonify({"courses": data}), 200
    
    except Exception as e:
        print(f"❌ Lỗi trong get_my_courses: {e}")
        import traceback
        traceback.print_exc()
        # Trả về mảng rỗng nếu có lỗi
        return jsonify({"courses": []}), 200


# Đăng ký khóa học 
@student_bp.route('/register', methods=['POST'])
def register_course():
    try:
        data = request.get_json()
        if not data or 'courseId' not in data:
            return jsonify({"error": "Thiếu courseId", "success": False}), 400

        course_id = data['courseId']

        # Determine current student (temporary simple auth replacement)
        student = Student.query.first()
        if not student:
            # Tạo student tạm nếu chưa có
            fake_user = User(email="temp@student.com", password_hash="fakehash", full_name="Temp User")
            db.session.add(fake_user)
            db.session.flush()  # để lấy fake_user.id mà chưa commit

            student = Student(user_id=fake_user.id)
            db.session.add(student)
            db.session.flush()  # để lấy student.id mà chưa commit

        # Kiểm tra khóa học có tồn tại không
        course = Course.query.get(course_id)
        if not course:
            return jsonify({"error": "Khóa học không tồn tại", "success": False}), 404

        # Kiểm tra đã đăng ký chưa (tránh trùng enrollment)
        # CHỈ kiểm tra enrollment có status='active'
        existing = Enrollment.query.filter(
            Enrollment.student_id == student.id,
            Enrollment.course_id == course_id,
            Enrollment.status == 'active'
        ).first()

        if existing:
            # Đã đăng ký rồi, nhưng vẫn trả về success vì đã có enrollment
            print(f"ℹ️ Khóa học {course_id} đã được đăng ký trước đó")
            return jsonify({
                "message": "Đã đăng ký khóa học này rồi",
                "success": True,
                "courseId": course_id
            }), 200

        # Tạo enrollment mới với status='active'
        new_enrollment = Enrollment(
            student_id=student.id,
            course_id=course_id,
            status='active'  # Đảm bảo status='active'
        )
        db.session.add(new_enrollment)
        db.session.commit()
        
        print(f"✅ Đã tạo enrollment mới: student_id={student.id}, course_id={course_id}, status='active'")

        # Trả về response rõ ràng với success=True
        return jsonify({
            "message": "Đăng ký thành công!",
            "success": True,
            "courseId": course_id
        }), 200

    except Exception as e:
        print("Lỗi đăng ký:", e)
        db.session.rollback()
        return jsonify({"error": "Lỗi server", "success": False}), 500


# Endpoint tạm để xóa tất cả enrollment (chỉ dùng cho testing)


# ✅ 4. Lấy lộ trình học (StudyPlan & PlanItem)
@student_bp.route('/study-plans/<int:student_id>', methods=['GET'])
def get_study_plans(student_id):
    plans = StudyPlan.query.filter_by(StudentID=student_id).all()
    data = []
    for plan in plans:
        items = PlanItem.query.filter_by(PlanID=plan.Id).order_by(PlanItem.SortOrder.asc()).all()
        plan_data = {
            'id': plan.id,
            'studentId': plan.student_id,
            'createdBy': plan.created_by,
            'createdAt': str(plan.created_at),
            'items': []
        }
        for item in items:
            plan_data['items'].append({
                'id': item.id,
                'courseId': item.course_id,
                'targetLevel': item.target_level,
                'deadline': str(item.deadline),
                'sortOrder': item.sort_order,
                'status': item.status
            })
        data.append(plan_data)

    return jsonify({"studyPlans": data}), 200
    
# . Lấy danh sách Section & Lesson của một khóa học cụ thể
@student_bp.route('/course/<int:course_id>/sections-lessons', methods=['GET'])
def get_course_sections_and_lessons(course_id):
    try:
        # Kiểm tra khóa học có tồn tại không
        course = Course.query.get(course_id)
        if not course:
            return jsonify({"error": "Khóa học không tồn tại"}), 404

        # Determine current student (temporary simple auth replacement)
        student = Student.query.first()

        # Map tiến độ bài học cho student hiện tại
        lesson_id_to_completed = set()
        if student:
            progresses = (
                LessonProgress.query
                .filter(LessonProgress.student_id == student.id)
                .all()
            )
            for p in progresses:
                if (p.status or '').lower() in ['done', 'completed', 'finished', 'complete']:
                    lesson_id_to_completed.add(p.lesson_id)

        # Lấy danh sách section theo course_id
        sections = sorted(list(course.sections), key=lambda s: (s.sort_order or 0, s.id))
        result = {
            "course": {
                "id": course.id,
                "instructorId": course.instructor_id,
                "title": course.title,
                "slug": course.slug,
                "description": course.description,
                "level": course.level,
                "price": float(course.price) if course.price is not None else 0,
                "currency": course.currency,
                "isPublic": course.is_public,
                "createdAt": str(course.created_at),
                "updatedAt": str(course.updated_at),
            },
            "sections": []
        }

        for section in sections:
            lessons = sorted(list(section.lessons), key=lambda l: (l.sort_order or 0, l.id))
            lesson_payload = []
            for lesson in lessons:
                lesson_payload.append({
                    "id": lesson.id,
                    "sectionId": lesson.section_id,
                    "title": lesson.title,
                    "type": lesson.type,
                    "content": lesson.content,
                    "videoUrl": lesson.video_url,
                    "durationSeconds": lesson.duration_seconds,
                    "sortOrder": lesson.sort_order,
                    "isPreview": lesson.is_preview,
                    "isCompleted": lesson.id in lesson_id_to_completed
                })

            result["sections"].append({
                "id": section.id,
                "courseId": section.course_id,
                "title": section.title,
                "sortOrder": section.sort_order,
                "lessons": lesson_payload
            })
        return jsonify(result), 200

    except Exception as e:
        print("Lỗi khi lấy section/lesson:", e)
        return jsonify({"error": "Lỗi server"}), 500


# ✅ Đánh dấu hoàn thành một bài học cho student hiện tại
@student_bp.route('/lesson-progress/complete', methods=['POST'])
def complete_lesson():
    try:
        data = request.get_json() or {}
        lesson_id = data.get('lessonId')
        if not lesson_id:
            return jsonify({"success": False, "error": "Thiếu lessonId"}), 400

        # Determine current student (temporary simple auth replacement)
        student = Student.query.first()
        if not student:
            # tạo tạm student nếu chưa có để tránh lỗi 500
            fake_user = User(email=f"temp_student_{datetime.utcnow().timestamp()}@example.com", password_hash="fakehash", full_name="Temp Student")
            db.session.add(fake_user)
            db.session.flush()
            student = Student(user_id=fake_user.id)
            db.session.add(student)
            db.session.flush()

        from app.models.model import LessonProgress, Lesson

        lesson = Lesson.query.get(lesson_id)
        if not lesson:
            return jsonify({"success": False, "error": "Bài học không tồn tại"}), 404

        # Tạo/cập nhật tiến độ
        lp = LessonProgress.query.filter_by(student_id=student.id, lesson_id=lesson_id).first()
        now = datetime.utcnow()
        if not lp:
            lp = LessonProgress(student_id=student.id, lesson_id=lesson_id, status='completed', updated_at=now)
            db.session.add(lp)
        else:
            lp.status = 'completed'
            lp.updated_at = now

        # Bỏ qua cập nhật Enrollment/progress để tránh lỗi; có thể thêm lại sau khi ổn định

        db.session.commit()
        return jsonify({"success": True}), 200
    except Exception as e:
        print("Lỗi complete_lesson:", e)
        db.session.rollback()
        return jsonify({"success": False, "error": "Lỗi server"}), 500
