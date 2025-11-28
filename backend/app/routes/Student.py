from flask import Blueprint
from flask import Blueprint, jsonify, request
from datetime import datetime
from app.models import db, Course, Enrollment, StudyPlan, PlanItem, Student
from app.models.model import User, LessonProgress, Instructor
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request, jwt_required, get_jwt

student_bp = Blueprint('student', __name__, url_prefix='/api/student')


# Helper: resolve user_id from JWT identity payload
# Now identity is a string (user_id), and role is in additional_claims
def _resolve_user_id_from_identity(identity):
    try:
        if isinstance(identity, str):
            return int(identity)
        if isinstance(identity, int):
            return identity
        if isinstance(identity, dict):
            return identity.get('user_id') or identity.get('id') or identity.get('sub')
        return None
    except Exception:
        return None


# Helper: get role from JWT claims
def _get_role_from_jwt():
    try:
        claims = get_jwt()
        return claims.get('role', 'student')
    except Exception:
        return 'student'


@student_bp.get('/ping')
def ping():
    return {'module': 'student', 'ok': True}

#  Lấy danh sách TẤT CẢ khóa học trong database (không lọc theo student)
@student_bp.route('/courses', methods=['GET'])
def get_all_courses():
    """
    Trả về TẤT CẢ khóa học có trong database.
    Không liên quan đến student ID hay trạng thái đăng ký.
    Frontend sẽ tự filter dựa trên danh sách khóa học đã đăng ký.
    """
    try:
        # Lấy TẤT CẢ khóa học trong database - không có bất kỳ filter nào
        courses = Course.query.all()
        
        data = []
        for c in courses:
            # Lấy thông tin instructor (nếu có)
            instructor_name = None
            if c.instructor_id:
                instr = Instructor.query.get(c.instructor_id)
                if instr and instr.user:
                    instructor_name = instr.user.full_name
            
            data.append({
                'id': c.id,
                'instructorId': c.instructor_id,
                'instructorName': instructor_name,
                'title': c.title,
                'slug': c.slug,
                'description': c.description,
                'level': c.level,
                'price': float(c.price) if c.price is not None else 0,
                'currency': c.currency,
                'isPublic': bool(c.is_public),
                'image': None,
                'thumbnail': None,
                'createdAt': c.created_at.isoformat() if c.created_at else None,
                'updatedAt': c.updated_at.isoformat() if c.updated_at else None,
            })
        
        print(f"✅ Trả về {len(data)} khóa học từ database")
        return jsonify({'courses': data}), 200
        
    except Exception as e:
        print(f"❌ Lỗi trong get_all_courses: {e}")
        return jsonify({'courses': [], 'error': 'Lỗi server'}), 500


#  Lấy danh sách khóa học mà sinh viên đã đăng ký
@student_bp.route('/my-courses', methods=['GET'])
def get_my_courses():
    try:
        student_id = request.args.get('student_id', type=int)
        student = None
        if not student_id:
            try:
                verify_jwt_in_request(optional=True)
                ident = get_jwt_identity()
                if ident is not None:
                    user_id = _resolve_user_id_from_identity(ident)
                    if user_id:
                        user = User.query.get(user_id)
                        if user:
                            student = Student.query.filter_by(user_id=user.id).first()
                            if student:
                                student_id = student.id
            except Exception:
                pass
        if student_id and not student:
            student = Student.query.get(student_id)

        if not student:
            return jsonify({'courses': [], 'studentId': None}), 200

        enrollments = Enrollment.query.filter(
            Enrollment.student_id == student.id,
            Enrollment.status == 'active'
        ).all()

        data = []
        for e in enrollments:
            course = Course.query.get(e.course_id)
            if not course:
                continue
            data.append({
                'id': course.id,
                'title': course.title,
                'slug': course.slug,
                'level': course.level,
                'price': float(course.price) if course.price is not None else 0,
                'currency': course.currency,
                'image': None,
                'thumbnail': None,
                'isPublic': bool(course.is_public),
                'enrollmentStatus': e.status,
                'createdAt': course.created_at.isoformat() if course.created_at else None,
                'updatedAt': course.updated_at.isoformat() if course.updated_at else None,
            })
        return jsonify({'courses': data, 'studentId': student.id}), 200
    except Exception as e:
        print(f"❌ Lỗi trong get_my_courses: {e}")
        return jsonify({'courses': [], 'studentId': None}), 200


# Đăng ký khóa học 
@student_bp.route('/register', methods=['POST'])
def register_course():
    try:
        # Debug: Log incoming request
        print(f"\n{'='*80}")
        print(f"📥 /api/student/register - Incoming request")
        print(f"{'='*80}")
        
        # Check Authorization header
        auth_header = request.headers.get('Authorization', '')
        print(f"📋 Authorization header: {auth_header[:80]}..." if len(auth_header) > 80 else f"📋 Authorization header: {auth_header}")
        
        data = request.get_json()
        if not data or 'courseId' not in data:
            return jsonify({"error": "Missing courseId", "success": False}), 400

        course_id = data['courseId']
        print(f"📝 Course ID to register: {course_id}")

        # Verify JWT manually to avoid framework 422 errors
        try:
            verify_jwt_in_request(optional=False)
            print(f"✅ JWT verification passed")
        except Exception as e:
            print(f"❌ JWT verification failed: {e}")
            return jsonify({"error": "Unauthorized: missing or invalid token", "success": False}), 401

        ident = get_jwt_identity()
        print(f"🔐 JWT Identity decoded: {ident}")
        
        user_id = _resolve_user_id_from_identity(ident)
        if not user_id:
            print(f"❌ Could not resolve user_id from identity: {ident}")
            return jsonify({"error": "Invalid token identity", "success": False}), 401
        
        print(f"👤 Resolved user_id: {user_id}")

        user = User.query.get(user_id)
        if not user:
            print(f"❌ User not found with user_id={user_id}")
            return jsonify({"error": "User not found", "success": False}), 401
        
        print(f"✅ User found: {user.email}")

        student = Student.query.filter_by(user_id=user.id).first()
        if not student:
            print(f"❌ Student profile not found for user_id={user.id}")
            return jsonify({"error": "Student profile not found", "success": False}), 403
        
        print(f"✅ Student found: id={student.id}")

        # Check course existence
        course = Course.query.get(course_id)
        if not course:
            print(f"❌ Course not found with id={course_id}")
            return jsonify({"error": "Course not found", "success": False}), 404
        
        print(f"✅ Course found: {course.title} (id={course.id})")

        # Check existing active enrollment
        existing = Enrollment.query.filter(
            Enrollment.student_id == student.id,
            Enrollment.course_id == course_id,
            Enrollment.status == 'active'
        ).first()

        if existing:
            print(f"⚠️ Student already enrolled in course {course_id}")
            return jsonify({
                "message": "Already enrolled",
                "success": True,
                "courseId": course_id
            }), 200

        # Create new enrollment
        new_enrollment = Enrollment(
            student_id=student.id,
            course_id=course_id,
            status='active'
        )
        db.session.add(new_enrollment)
        db.session.commit()
        
        print(f"✅ Successfully enrolled student {student.id} in course {course.id}")
        print(f"{'='*80}\n")

        return jsonify({
            "message": "Enrollment successful",
            "success": True,
            "courseId": course_id
        }), 200

    except Exception as e:
        print(f"❌ Exception in register_course: {e}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        print(f"{'='*80}\n")
        db.session.rollback()
        return jsonify({"error": "Server error", "success": False}), 500


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

        # Lấy student từ JWT token (optional)
        student = None
        try:
            verify_jwt_in_request(optional=True)
            ident = get_jwt_identity()
            if ident:
                user_id = _resolve_user_id_from_identity(ident)
                if user_id:
                    user = User.query.get(user_id)
                    if user:
                        student = Student.query.filter_by(user_id=user.id).first()
        except Exception:
            pass

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

        # Lấy student từ JWT token
        student = None
        try:
            verify_jwt_in_request(optional=True)
            ident = get_jwt_identity()
            if ident:
                user_id = _resolve_user_id_from_identity(ident)
                if user_id:
                    user = User.query.get(user_id)
                    if user:
                        student = Student.query.filter_by(user_id=user.id).first()
        except Exception as e:
            print(f"⚠️ Không thể lấy student từ JWT: {e}")
        
        if not student:
            return jsonify({"success": False, "error": "Vui lòng đăng nhập"}), 401

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

