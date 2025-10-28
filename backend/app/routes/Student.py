from flask import Blueprint, jsonify, request
from app.models import db, Course, Enrollment, StudyPlan, PlanItem, Student
from app.models.model import User

student_bp = Blueprint('student_bp', __name__, url_prefix='/api/student')


# ✅ 1. Lấy danh sách tất cả khóa học (hiển thị bên trái)
@student_bp.route('/courses', methods=['GET'])
def get_all_courses():
    courses = Course.query.all()
    data = []
    for c in courses:
        data.append({
            'id': c.id,
            'instructorId': c.instructor_id,
            'title': c.title,
            'slug': c.slug,
            'description': c.description,
            'level': c.level,
            'price': c.price,
            'currency': c.currency,
            'isPublic': c.is_public,
            'createdAt': str(c.created_at),
            'updatedAt': str(c.updated_at),
            # 'image': c.image_url if hasattr(c, 'image_url') else None
        })
    return jsonify({"courses": data}), 200


# ✅ 2. Lấy danh sách khóa học mà sinh viên đã đăng ký
@student_bp.route('/my-courses/<int:student_id>', methods=['GET'])
def get_my_courses(student_id):
    enrollments = Enrollment.query.filter_by(StudentID=student_id).all()
    data = []
    for e in enrollments:
        course = Course.query.get(e.CourseID)
        if course:
            data.append({
                'id': course.Id,
                'title': course.Title,
                'slug': course.Slug,
                'level': course.Level,
                'price': course.Price,
                'currency': course.Currency,
                'image': course.ImageUrl,
                'isPublic': course.IsPublic,
                'createdAt': str(course.CreatedAt),
                'updatedAt': str(course.UpdatedAt)
            })
    return jsonify(data), 200


# Đăng ký khóa học 
@student_bp.route('/register', methods=['POST'])
def register_course():
    try: 
        data = request.get_json()
        if not data or 'courseId' not in data:
            return jsonify({"error": "Thiếu courseId"}), 400

        course_id = data['courseId']

        # ✅ Fake student_id có thật trong DB
        student = Student.query.first()
        if not student:
            fake_user = User(email="temp@student.com", password_hash="fakehash", full_name="Temp User")
            db.session.add(fake_user)
            db.session.flush()  # để lấy fake_user.id mà chưa commit

            student = Student(user_id=fake_user.id)
            db.session.add(student)
            db.session.commit()

        student_id = student.id  # ✅ lấy id có thật

        # ✅ Check khóa học tồn tại
        course = Course.query.get(course_id)
        if not course:
            return jsonify({"error": "Khóa học không tồn tại"}), 404

        # ✅ Kiểm tra đăng ký trùng
        existing = Enrollment.query.filter_by(student_id=student_id, course_id=course_id).first()
        if existing:
            return jsonify({"message": "Đã đăng ký khóa học này rồi"}), 200

        # ✅ Tạo đăng ký mới
        new_enrollment = Enrollment(student_id=student_id, course_id=course_id)
        db.session.add(new_enrollment)
        db.session.commit()

        return jsonify({"message": "Đăng ký thành công!"}), 200

    except Exception as e:
        print("Lỗi đăng ký:", e)
        db.session.rollback()
        return jsonify({"error": "Lỗi server"}), 500



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
