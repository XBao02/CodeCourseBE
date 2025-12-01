from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request, Response
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from decimal import Decimal
import re
import io
import csv

from app.models.model import (
    db,
    User,
    Student,
    Instructor,
    Course,
    Enrollment,
    Invoice,
    LessonProgress,
    Message,
)
from werkzeug.security import generate_password_hash

# Prefix API cho admin
admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


# --------------------------
# Helper serializers
# --------------------------
def _slugify(text: str):
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", (text or "").strip().lower()).strip("-")
    return slug or "course"


def _parse_date_range():
    """Parse start/end query params; default last 30 days."""
    start_str = request.args.get("start")
    end_str = request.args.get("end")
    days = request.args.get("days", type=int)

    today = datetime.utcnow().date()
    if end_str:
        try:
            end_date = datetime.strptime(end_str, "%Y-%m-%d").date()
        except ValueError:
            end_date = today
    else:
        end_date = today

    if start_str:
        try:
            start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
        except ValueError:
            start_date = end_date - timedelta(days=29)
    else:
        if days and days > 0:
            start_date = end_date - timedelta(days=days - 1)
        else:
            start_date = end_date - timedelta(days=29)

    if start_date > end_date:
        start_date, end_date = end_date, start_date

    start_dt = datetime.combine(start_date, datetime.min.time())
    end_dt = datetime.combine(end_date, datetime.max.time())
    return start_date, end_date, start_dt, end_dt


def _student_to_json(student: Student):
    user = student.user
    # Lấy enrollment mới nhất (nếu có) để map vào FE
    latest_enroll = None
    if student.enrollments:
        latest_enroll = sorted(
            student.enrollments,
            key=lambda e: e.updated_at or e.created_at or datetime.min,
            reverse=True,
        )[0]

    course_title = None
    course_id = None
    progress = 0
    status = "Inactive"
    enrollment_date = None

    if latest_enroll:
        course = latest_enroll.course
        if course:
            course_title = course.title
            course_id = course.id
        progress = latest_enroll.progress_percent or 0
        status = (latest_enroll.status or "inactive").title()
        enrollment_date = (
            latest_enroll.created_at.isoformat() if latest_enroll.created_at else None
        )

    return {
        "id": student.id,
        "name": user.full_name if user else None,
        "email": user.email if user else None,
        "course": course_title,
        "courseId": course_id,
        "progress": progress,
        "status": status,
        "phone": student.phone,
        "address": student.address,
        "enrollmentDate": enrollment_date,
        "isActive": bool(user.is_active) if user else False,
    }


def _instructor_to_json(inst: Instructor):
    user = inst.user
    courses = inst.courses or []
    active_courses = [c for c in courses if c.is_public]
    return {
        "id": inst.id,
        "name": user.full_name if user else None,
        "email": user.email if user else None,
        "expertise": inst.expertise,
        "status": "Active" if (user and user.is_active) else "Inactive",
        "coursesCount": len(courses),
        "activeCourses": len(active_courses),
        "averageRating": 4.5,  # Placeholder - chưa có bảng rating
        "joinDate": user.created_at.isoformat() if user and user.created_at else None,
    }


# --------------------------
# Health check
# --------------------------
@admin_bp.get("/ping")
def ping():
    return {"module": "admin", "ok": True}


# --------------------------
# Role management (Decentralization.vue)
# --------------------------
def _role_counts():
    admin_cnt = db.session.query(func.count(User.id)).filter(User.role == "admin").scalar() or 0
    instructor_cnt = db.session.query(func.count(User.id)).filter(User.role == "instructor").scalar() or 0
    student_cnt = db.session.query(func.count(User.id)).filter(User.role == "student").scalar() or 0
    roles_set = set()
    for r in db.session.query(User.role).all():
        if r[0]:
            roles_set.add(r[0])
    return admin_cnt, instructor_cnt, student_cnt, len(roles_set)


@admin_bp.get("/roles/summary")
def roles_summary():
    admin_cnt, instructor_cnt, student_cnt, total_roles = _role_counts()
    return jsonify(
        {
            "totalRoles": total_roles,
            "adminUsers": admin_cnt,
            "instructors": instructor_cnt,
            "students": student_cnt,
        }
    )


@admin_bp.get("/roles")
def list_roles():
    admin_cnt, instructor_cnt, student_cnt, total_roles = _role_counts()
    roles = [
        {
            "id": 1,
            "name": "Admin",
            "description": "Full system access with all permissions",
            "users": admin_cnt,
            "type": "System",
            "permissions": ["user_management", "course_management", "content_management", "settings_management", "analytics_view"],
            "status": "Active",
        },
        {
            "id": 2,
            "name": "Instructor",
            "description": "Can create and manage courses",
            "users": instructor_cnt,
            "type": "System",
            "permissions": ["course_management", "content_management", "student_management"],
            "status": "Active",
        },
        {
            "id": 3,
            "name": "Student",
            "description": "Can enroll in and access courses",
            "users": student_cnt,
            "type": "System",
            "permissions": ["course_access", "content_view"],
            "status": "Active",
        },
    ]
    return jsonify({"totalRoles": total_roles, "roles": roles})


# --------------------------
# Student management (Accounts.vue)
# --------------------------
@admin_bp.get("/students")
def list_students():
    students = (
        Student.query.options(
            joinedload(Student.user),
            joinedload(Student.enrollments).joinedload(Enrollment.course),
        )
        .order_by(Student.id)
        .all()
    )
    return jsonify([_student_to_json(s) for s in students])


@admin_bp.post("/students")
def create_student():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()

    if not name or not email:
        return jsonify({"message": "Thiếu name hoặc email"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email đã tồn tại"}), 409

    try:
        user = User(
            email=email,
            password_hash=generate_password_hash(data.get("password") or "123456"),
            full_name=name,
            role="student",
            is_active=True,
        )
        db.session.add(user)
        db.session.flush()

        student = Student(
            user_id=user.id,
            phone=data.get("phone"),
            address=data.get("address"),
        )
        db.session.add(student)
        db.session.flush()

        course_id = data.get("course_id") or data.get("courseId")
        if course_id:
            enrollment = Enrollment(
                student_id=student.id,
                course_id=course_id,
                status=(data.get("status") or "Active").lower(),
                progress_percent=data.get("progress") or 0,
            )
            db.session.add(enrollment)

        db.session.commit()
        return jsonify(_student_to_json(student)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Lỗi khi tạo student: {e}"}), 500


@admin_bp.put("/students/<int:student_id>")
def update_student(student_id: int):
    student = Student.query.options(joinedload(Student.user)).filter_by(id=student_id).first()
    if not student:
        return jsonify({"message": "Student không tồn tại"}), 404

    data = request.get_json(silent=True) or {}
    try:
        if student.user:
            if "name" in data:
                student.user.full_name = data["name"]
            if "email" in data:
                student.user.email = data["email"].lower()
            if "isActive" in data:
                student.user.is_active = bool(data["isActive"])

        if "phone" in data:
            student.phone = data["phone"]
        if "address" in data:
            student.address = data["address"]

        # Update enrollment info nếu gửi lên
        course_id = data.get("course_id") or data.get("courseId")
        status = data.get("status")
        progress = data.get("progress")

        latest_enroll = None
        if student.enrollments:
            latest_enroll = sorted(
                student.enrollments,
                key=lambda e: e.updated_at or e.created_at or datetime.min,
                reverse=True,
            )[0]

        if course_id or status or progress is not None:
            if latest_enroll is None and course_id:
                latest_enroll = Enrollment(student_id=student.id, course_id=course_id)
                db.session.add(latest_enroll)

            if latest_enroll:
                if course_id:
                    latest_enroll.course_id = course_id
                if status:
                    latest_enroll.status = status.lower()
                if progress is not None:
                    latest_enroll.progress_percent = progress
                latest_enroll.updated_at = datetime.utcnow()

        db.session.commit()
        return jsonify(_student_to_json(student)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Lỗi khi cập nhật student: {e}"}), 500


@admin_bp.delete("/students/<int:student_id>")
def delete_student(student_id: int):
    student = Student.query.filter_by(id=student_id).first()
    if not student:
        return jsonify({"message": "Student không tồn tại"}), 404
    try:
        # Xóa enrollments trước để tránh FK
        Enrollment.query.filter_by(student_id=student.id).delete()
        user = student.user
        db.session.delete(student)
        if user:
            db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "Đã xóa student"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Lỗi khi xóa student: {e}"}), 500


# --------------------------
# Instructor management (Accounts_Instructor.vue)
# --------------------------
@admin_bp.get("/instructors")
def list_instructors():
    instructors = (
        Instructor.query.options(
            joinedload(Instructor.user),
            joinedload(Instructor.courses),
        )
        .order_by(Instructor.id)
        .all()
    )
    return jsonify([_instructor_to_json(i) for i in instructors])


@admin_bp.post("/instructors")
def create_instructor():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()

    if not name or not email:
        return jsonify({"message": "Thiếu name hoặc email"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email đã tồn tại"}), 409

    try:
        user = User(
            email=email,
            password_hash=generate_password_hash(data.get("password") or "123456"),
            full_name=name,
            role="instructor",
            is_active=True,
        )
        db.session.add(user)
        db.session.flush()

        inst = Instructor(
            user_id=user.id,
            expertise=data.get("expertise"),
            biography=data.get("biography"),
            years_experience=data.get("years_experience") or data.get("yearsExperience") or 0,
        )
        db.session.add(inst)
        db.session.commit()
        return jsonify(_instructor_to_json(inst)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Lỗi khi tạo instructor: {e}"}), 500


@admin_bp.put("/instructors/<int:inst_id>")
def update_instructor(inst_id: int):
    inst = Instructor.query.options(joinedload(Instructor.user)).filter_by(id=inst_id).first()
    if not inst:
        return jsonify({"message": "Instructor không tồn tại"}), 404
    data = request.get_json(silent=True) or {}
    try:
        if inst.user:
            if "name" in data:
                inst.user.full_name = data["name"]
            if "email" in data:
                inst.user.email = data["email"].lower()
            if "isActive" in data:
                inst.user.is_active = bool(data["isActive"])

        if "expertise" in data:
            inst.expertise = data["expertise"]
        if "biography" in data:
            inst.biography = data["biography"]
        if "years_experience" in data or "yearsExperience" in data:
            inst.years_experience = data.get("years_experience") or data.get("yearsExperience") or 0

        db.session.commit()
        return jsonify(_instructor_to_json(inst)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Lỗi khi cập nhật instructor: {e}"}), 500


@admin_bp.delete("/instructors/<int:inst_id>")
def delete_instructor(inst_id: int):
    inst = Instructor.query.filter_by(id=inst_id).first()
    if not inst:
        return jsonify({"message": "Instructor không tồn tại"}), 404
    try:
        # Xóa course nếu muốn cứng; hiện giữ nguyên nhưng bỏ FK bằng cách từ chối nếu có course
        if inst.courses:
            return jsonify({"message": "Không thể xóa instructor vì đang có courses"}), 400
        user = inst.user
        db.session.delete(inst)
        if user:
            db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "Đã xóa instructor"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Lỗi khi xóa instructor: {e}"}), 500


# --------------------------
# Courses list for Admin (Courses.vue)
# --------------------------
@admin_bp.get("/courses")
def list_courses():
    courses = Course.query.options(joinedload(Course.instructor).joinedload(Instructor.user)).all()
    results = []
    for c in courses:
        instructor_name = c.instructor.user.full_name if c.instructor and c.instructor.user else None
        enroll_count = (
            db.session.query(func.count(Enrollment.id))
            .filter(Enrollment.course_id == c.id)
            .scalar()
            or 0
        )
        results.append(
            {
                "id": c.id,
                "title": c.title,
                "description": c.description,
                "price": float(c.price or 0),
                "level": c.level,
                "status": "active" if c.is_public else "draft",
                "students": enroll_count,
                "rating": 4.6,  # Placeholder
                "instructor": instructor_name,
                "updatedAt": c.updated_at.isoformat() if c.updated_at else None,
            }
        )
    return jsonify(results)


@admin_bp.post("/courses")
def create_course():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    instructor_id = data.get("instructor_id") or data.get("instructorId")

    if not title:
        return jsonify({"message": "Thiếu title"}), 400
    if not instructor_id:
        return jsonify({"message": "Thiếu instructor_id"}), 400

    instructor = Instructor.query.filter_by(id=instructor_id).first()
    if not instructor:
        return jsonify({"message": "Instructor không tồn tại"}), 404

    try:
        slug_base = _slugify(title)
        slug = slug_base
        n = 1
        while Course.query.filter_by(slug=slug).first():
            n += 1
            slug = f"{slug_base}-{n}"

        course = Course(
            instructor_id=instructor.id,
            title=title,
            slug=slug,
            description=data.get("description"),
            level=data.get("level") or "beginner",
            price=data.get("price") or 0,
            currency=data.get("currency") or "VND",
            is_public=bool(data.get("is_public") or data.get("isPublic") or False),
        )
        db.session.add(course)
        db.session.commit()

        instructor_name = instructor.user.full_name if instructor.user else None
        result = {
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "price": float(course.price or 0),
            "level": course.level,
            "status": "active" if course.is_public else "draft",
            "students": 0,
            "rating": 0,
            "instructor": instructor_name,
            "updatedAt": course.updated_at.isoformat() if course.updated_at else None,
        }
        return jsonify(result), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Lỗi khi tạo course: {e}"}), 500



@admin_bp.delete("/courses/<int:course_id>")
def delete_course(course_id: int):
    course = Course.query.filter_by(id=course_id).first()
    if not course:
        return jsonify({"message": "Course không tồn tại"}), 404
    try:
        # Xóa enrollment và invoice liên quan trước để tránh lỗi FK
        Enrollment.query.filter_by(course_id=course.id).delete()
        Invoice.query.filter_by(course_id=course.id).delete()
        db.session.delete(course)
        db.session.commit()
        return jsonify({"message": "Đã xóa course"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Lỗi khi xóa course: {e}"}), 500


# --------------------------
# Dashboard & basic reports (Dashboard.vue, Reports.vue)
# --------------------------
@admin_bp.get("/dashboard/overview")
def dashboard_overview():
    total_students = db.session.query(func.count(Student.id)).scalar() or 0
    total_instructors = db.session.query(func.count(Instructor.id)).scalar() or 0
    total_courses = db.session.query(func.count(Course.id)).scalar() or 0
    active_courses = db.session.query(func.count(Course.id)).filter(Course.is_public == True).scalar() or 0  # noqa: E712
    total_enrollments = db.session.query(func.count(Enrollment.id)).scalar() or 0

    return jsonify(
        {
            "totals": {
                "students": total_students,
                "instructors": total_instructors,
                "courses": total_courses,
                "activeCourses": active_courses,
                "enrollments": total_enrollments,
            }
        }
    )


@admin_bp.get("/reports/summary")
def reports_summary():
    # Số liệu nhẹ cho FE reports, có thể mở rộng sau
    total_students = db.session.query(func.count(Student.id)).scalar() or 0
    total_courses = db.session.query(func.count(Course.id)).scalar() or 0
    active_courses = db.session.query(func.count(Course.id)).filter(Course.is_public == True).scalar() or 0  # noqa: E712
    enrollments = db.session.query(Enrollment).all()
    completed = len([e for e in enrollments if (e.status or "").lower() == "completed"])
    in_progress = len([e for e in enrollments if (e.status or "").lower() in ("active", "enrolled")])
    dropped = len([e for e in enrollments if (e.status or "").lower() == "dropped"])
    avg_progress = (
        round(
            sum([e.progress_percent or 0 for e in enrollments]) / len(enrollments),
            1,
        )
        if enrollments
        else 0
    )
    completion_rate = round((completed / len(enrollments) * 100), 1) if enrollments else 0

    avg_score = (
        db.session.query(func.coalesce(func.avg(LessonProgress.score), 0)).scalar() or 0
    )
    try:
        avg_score_val = float(avg_score)
    except Exception:
        avg_score_val = 0.0
    message_count = db.session.query(func.count(Message.id)).scalar() or 0

    return jsonify(
        {
            "students": total_students,
            "courses": total_courses,
            "activeCourses": active_courses,
            "enrollments": len(enrollments),
            "studentDistribution": {
                "completed": completed,
                "inProgress": in_progress,
                "dropped": dropped,
            },
            "averageProgress": avg_progress,
            "completionRate": completion_rate,
            "averageScore": round(avg_score_val, 2),
            "engagementCount": message_count,
        }
    )


# --------------------------
# Dashboard analytics (for Dashboard.vue)
# --------------------------
@admin_bp.get("/dashboard/analytics")
def dashboard_analytics():
    """
    Trả dữ liệu tổng hợp cho Dashboard:
    - overview: totalUsers, activeCourses, totalRevenue
    - registrationsByMonth: số user đăng ký theo tháng của năm được chọn
    - revenueByMonth: doanh thu theo tháng (Invoices) năm được chọn
    - revenueByCourse: doanh thu theo khóa học (Invoices) năm được chọn
    - courseCompletion: tỉ lệ hoàn thành theo Enrollment.status
    """
    year = request.args.get("year", type=int) or datetime.utcnow().year

    # Overview
    total_users = db.session.query(func.count(User.id)).scalar() or 0
    active_courses = (
        db.session.query(func.count(Course.id))
        .filter(Course.is_public == True)  # noqa: E712
        .scalar()
        or 0
    )
    total_revenue = (
        db.session.query(func.coalesce(func.sum(Invoice.amount), 0))
        .filter(Invoice.payment_status == "paid")
        .scalar()
        or 0
    )
    if isinstance(total_revenue, Decimal):
        total_revenue = float(total_revenue)

    # New registrations by month (Users.created_at)
    registrations_by_month = [0] * 12
    reg_rows = (
        db.session.query(func.month(User.created_at), func.count(User.id))
        .filter(func.year(User.created_at) == year)
        .group_by(func.month(User.created_at))
        .all()
    )
    for m, cnt in reg_rows:
        if m and 1 <= m <= 12:
            registrations_by_month[m - 1] = int(cnt or 0)

    # Revenue by month (Invoices.paid_at nếu có, fallback issued_at)
    revenue_by_month = [0] * 12
    rev_rows = (
        db.session.query(
            func.month(func.coalesce(Invoice.paid_at, Invoice.issued_at)).label("m"),
            func.coalesce(func.sum(Invoice.amount), 0),
        )
        .filter(func.year(func.coalesce(Invoice.paid_at, Invoice.issued_at)) == year)
        .filter(Invoice.payment_status == "paid")
        .group_by("m")
        .all()
    )
    for m, amt in rev_rows:
        val = float(amt or 0)
        if m and 1 <= m <= 12:
            revenue_by_month[m - 1] = val

    # Revenue by course (year filter)
    revenue_by_course = []
    rev_course_rows = (
        db.session.query(
            Course.id,
            Course.title,
            func.coalesce(func.sum(Invoice.amount), 0).label("rev"),
        )
        .join(Invoice, Invoice.course_id == Course.id)
        .filter(func.year(func.coalesce(Invoice.paid_at, Invoice.issued_at)) == year)
        .filter(Invoice.payment_status == "paid")
        .group_by(Course.id, Course.title)
        .all()
    )
    for cid, title, rev in rev_course_rows:
        revenue_by_course.append(
            {
                "id": cid,
                "name": title,
                "revenue": float(rev or 0),
            }
        )

    # Course completion (Enrollment.status)
    course_completion = []
    course_rows = Course.query.all()
    for course in course_rows:
        enrolls = course.enrollments or []
        total_students = len(enrolls)
        completed = len(
            [e for e in enrolls if (e.status or "").lower() == "completed"]
        )
        completion_rate = round((completed / total_students * 100), 1) if total_students else 0
        course_completion.append(
            {
                "id": course.id,
                "name": course.title,
                "completionRate": completion_rate,
                "totalStudents": total_students,
            }
        )

    return jsonify(
        {
            "overview": {
                "totalUsers": total_users,
                "activeCourses": active_courses,
                "totalRevenue": round(total_revenue, 2),
            },
            "registrationsByMonth": registrations_by_month,
            "revenueByMonth": revenue_by_month,
            "revenueByCourse": revenue_by_course,
            "courseCompletion": course_completion,
            "year": year,
        }
    )


@admin_bp.get("/reports/export")
def export_reports():
    """Xuất báo cáo CSV theo khoảng ngày (start/end hoặc days)."""
    start_date, end_date, start_dt, end_dt = _parse_date_range()

    # Tổng hợp trong khoảng thời gian
    total_students = (
        db.session.query(func.count(User.id))
        .filter(User.role == "student")
        .filter(User.created_at.between(start_dt, end_dt))
        .scalar()
        or 0
    )
    total_instructors = (
        db.session.query(func.count(User.id))
        .filter(User.role == "instructor")
        .filter(User.created_at.between(start_dt, end_dt))
        .scalar()
        or 0
    )
    total_courses = (
        db.session.query(func.count(Course.id))
        .filter(Course.created_at.between(start_dt, end_dt))
        .scalar()
        or 0
    )
    active_courses = (
        db.session.query(func.count(Course.id))
        .filter(Course.is_public == True)  # noqa: E712
        .filter(Course.created_at.between(start_dt, end_dt))
        .scalar()
        or 0
    )

    enrollments = (
        db.session.query(Enrollment)
        .filter(Enrollment.created_at.between(start_dt, end_dt))
        .all()
    )
    completed = len([e for e in enrollments if (e.status or "").lower() == "completed"])
    in_progress = len([e for e in enrollments if (e.status or "").lower() in ("active", "enrolled")])
    dropped = len([e for e in enrollments if (e.status or "").lower() == "dropped"])

    registrations_by_day = []
    reg_rows = (
        db.session.query(func.date(User.created_at), func.count(User.id))
        .filter(User.created_at.between(start_dt, end_dt))
        .group_by(func.date(User.created_at))
        .order_by(func.date(User.created_at))
        .all()
    )
    for d, cnt in reg_rows:
        registrations_by_day.append((d.isoformat(), int(cnt or 0)))

    revenue_by_month_rows = (
        db.session.query(
            func.date_format(func.coalesce(Invoice.paid_at, Invoice.issued_at), "%Y-%m").label("ym"),
            func.coalesce(func.sum(Invoice.amount), 0),
        )
        .filter(func.coalesce(Invoice.paid_at, Invoice.issued_at).between(start_dt, end_dt))
        .filter(Invoice.payment_status == "paid")
        .group_by("ym")
        .order_by("ym")
        .all()
    )
    revenue_by_month = [(ym, float(val or 0)) for ym, val in revenue_by_month_rows]

    revenue_by_course_rows = (
        db.session.query(
            Course.title,
            func.coalesce(func.sum(Invoice.amount), 0).label("rev"),
        )
        .join(Invoice, Invoice.course_id == Course.id)
        .filter(func.coalesce(Invoice.paid_at, Invoice.issued_at).between(start_dt, end_dt))
        .filter(Invoice.payment_status == "paid")
        .group_by(Course.title)
        .all()
    )

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["Report Range", f"{start_date.isoformat()} to {end_date.isoformat()}"])
    writer.writerow([])

    writer.writerow(["Summary (within range)"])
    writer.writerow(["New Students", total_students])
    writer.writerow(["New Instructors", total_instructors])
    writer.writerow(["New Courses", total_courses])
    writer.writerow(["New Active Courses", active_courses])
    writer.writerow(["New Enrollments", len(enrollments)])
    writer.writerow(["Completed", completed])
    writer.writerow(["In Progress", in_progress])
    writer.writerow(["Dropped", dropped])
    writer.writerow([])

    writer.writerow(["Registrations By Day"])
    writer.writerow(["Date", "Registrations"])
    for day, cnt in registrations_by_day:
        writer.writerow([day, cnt])
    writer.writerow([])

    writer.writerow(["Revenue By Month"])
    writer.writerow(["Year-Month", "Revenue"])
    for ym, val in revenue_by_month:
        writer.writerow([ym, val])
    writer.writerow([])

    writer.writerow(["Revenue By Course"])
    writer.writerow(["Course", "Revenue"])
    for title, rev in revenue_by_course_rows:
        writer.writerow([title, float(rev or 0)])

    csv_data = output.getvalue()
    output.close()
    filename = f"admin_report_{start_date.isoformat()}_to_{end_date.isoformat()}.csv"
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        },
    )

