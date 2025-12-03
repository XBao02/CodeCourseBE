from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
# Import db và các Models cần thiết
from ..models.model import db, Course, Instructor, CourseSection, Lesson, Test, Question, Choice, Enrollment, User
import re
import os

# Khởi tạo Blueprint cho các routes liên quan đến Giảng viên
instructor_bp = Blueprint('instructor', __name__)

# Helper function to get instructor ID from JWT token
def get_current_instructor_id():
    """Get instructor ID from JWT token"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or user.role != 'instructor':
            return None
        instructor = Instructor.query.filter_by(user_id=user_id).first()
        return instructor.id if instructor else None
    except Exception as e:
        print(f"Error getting instructor ID: {e}")
        return None

@instructor_bp.route("/api/courses", methods=['GET'])
@instructor_bp.route("/courses", methods=['GET'])
@jwt_required()
def get_instructor_courses():
    """
    Lấy danh sách khóa học của Giảng viên hiện tại dựa trên JWT token.
    """
    instructor_id = get_current_instructor_id()
    if not instructor_id:
        return jsonify({"message": "Unauthorized or invalid instructor"}), 401
    try:
        courses = Course.query.filter_by(instructor_id=instructor_id).all()
        course_list = []
        for course in courses:
            status = 'active' if course.is_public else 'draft'
            # Backward compatible thumbnail mapping
            img = course.image_url or f"/images/course/{course.id}.jpg"
            course_list.append({
                "id": course.id,
                "title": course.title,
                "description": course.description,
                "price": float(course.price) if course.price is not None else 0.00,
                "level": course.level,
                "status": status,
                "students": 120,  # mock
                "rating": "4.5", # mock
                "image_url": course.image_url,  # new
                "thumbnail": img,              # legacy field for FE until refactor complete
                "updatedAt": course.updated_at.isoformat() if course.updated_at else None
            })
        return jsonify(course_list)
    except Exception as e:
        print(f"Lỗi khi truy vấn database: {e}")
        return jsonify({"message": "Lỗi server nội bộ khi lấy dữ liệu khóa học"}), 500


@instructor_bp.route("/api/courses", methods=['POST'])
@instructor_bp.route("/courses", methods=['POST'])
@jwt_required()
def create_course():
    """
    Tạo khóa học mới
    POST /api/courses
    Body: {
        "title": "Tiêu đề khóa học",
        "description": "Mô tả",
        "price": 299000,
        "thumbnail": "url",
        "level": "beginner",
        "status": "draft",
        "category": "Web Development",
        "requirements": "HTML/CSS cơ bản"
    }
    """
    try:
        instructor_id = get_current_instructor_id()
        if not instructor_id:
            return jsonify({"message": "Unauthorized or invalid instructor"}), 401
        data = request.get_json() or {}
        required_fields = ['title', 'description', 'price']
        for f in required_fields:
            if not data.get(f):
                return jsonify({"message": f"Thiếu trường bắt buộc: {f}"}), 400
        instructor = Instructor.query.filter_by(id=instructor_id).first()
        if not instructor:
            return jsonify({"message": "Giảng viên không tồn tại"}), 404
        slug = generate_slug(data['title'])
        if Course.query.filter_by(slug=slug).first():
            slug = f"{slug}-{datetime.utcnow().timestamp()}"
        is_public = data.get('status', 'draft') == 'active'
        new_course = Course(
            instructor_id=instructor_id,
            title=data['title'],
            slug=slug,
            description=data['description'],
            price=data.get('price', 0),
            currency=data.get('currency', 'VND'),
            level=data.get('level', 'beginner'),
            is_public=is_public,
            image_url=data.get('image_url') or data.get('thumbnail'),  # save Cloudinary URL
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(new_course)
        db.session.commit()
        return jsonify({
            "message": "Khóa học đã được tạo thành công",
            "id": new_course.id,
            "title": new_course.title,
            "slug": new_course.slug,
            "image_url": new_course.image_url
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Lỗi khi tạo khóa học: {e}")
        return jsonify({"message": f"Lỗi khi tạo khóa học: {str(e)}"}), 500


@instructor_bp.route("/courses/<int:course_id>", methods=['GET'])
@jwt_required()
def get_course_detail(course_id):
    """
    Xem chi tiết một khóa học
    GET /api/courses/<course_id>
    """
    try:
        instructor_id = get_current_instructor_id()
        if not instructor_id:
            return jsonify({"message": "Unauthorized"}), 401
        course = Course.query.filter_by(id=course_id, instructor_id=instructor_id).first()
        if not course:
            return jsonify({"message": "Khóa học không tồn tại hoặc không có quyền truy cập"}), 404
        status = 'active' if course.is_public else 'draft'
        img = course.image_url or f"/images/course/{course.id}.jpg"
        return jsonify({
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "price": float(course.price) if course.price is not None else 0.00,
            "level": course.level,
            "status": status,
            "instructor_id": course.instructor_id,
            "students": 0,
            "rating": 0.0,
            "lessons": 0,
            "duration": 0,
            "image_url": course.image_url,
            "thumbnail": img,
            "createdAt": course.created_at.isoformat() if course.created_at else None,
            "updatedAt": course.updated_at.isoformat() if course.updated_at else None
        }), 200
    except Exception as e:
        print(f"Lỗi khi lấy chi tiết khóa học: {e}")
        return jsonify({"message": "Lỗi server nội bộ"}), 500


@instructor_bp.route("/api/courses/<int:course_id>", methods=['PUT'])
@instructor_bp.route("/courses/<int:course_id>", methods=['PUT'])
@jwt_required()
def update_course(course_id):
    """
    Cập nhật khóa học
    PUT /api/courses/<course_id>
    Body: {
        "title": "Tiêu đề mới",
        "description": "Mô tả mới",
        "price": 399000,
        "level": "intermediate",
        "status": "active"
    }
    """
    try:
        instructor_id = get_current_instructor_id()
        if not instructor_id:
            return jsonify({"message": "Unauthorized"}), 401
        course = Course.query.filter_by(id=course_id, instructor_id=instructor_id).first()
        if not course:
            return jsonify({"message": "Khóa học không tồn tại hoặc không có quyền truy cập"}), 404
        data = request.get_json() or {}
        if 'title' in data and data['title']:
            course.title = data['title']
            course.slug = generate_slug(data['title'])
        if 'description' in data:
            course.description = data['description']
        if 'price' in data:
            course.price = data['price']
        if 'level' in data:
            course.level = data['level']
        if 'status' in data:
            course.is_public = data['status'] == 'active'
        if 'image_url' in data or 'thumbnail' in data:
            course.image_url = data.get('image_url') or data.get('thumbnail')
        course.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify({
            "message": "Khóa học đã được cập nhật thành công",
            "id": course.id,
            "title": course.title,
            "image_url": course.image_url
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Lỗi khi cập nhật khóa học: {e}")
        return jsonify({"message": f"Lỗi khi cập nhật khóa học: {str(e)}"}), 500


@instructor_bp.route("/api/courses/<int:course_id>", methods=['DELETE'])
@instructor_bp.route("/courses/<int:course_id>", methods=['DELETE'])
@jwt_required()
def delete_course(course_id):
    """
    Xóa khóa học
    DELETE /api/courses/<course_id>
    """
    try:
        instructor_id = get_current_instructor_id()
        if not instructor_id:
            return jsonify({"message": "Unauthorized"}), 401
        course = Course.query.filter_by(id=course_id, instructor_id=instructor_id).first()
        if not course:
            return jsonify({"message": "Khóa học không tồn tại hoặc không có quyền truy cập"}), 404
        # Check if course has enrollments
        enrollment_count = db.session.query(db.func.count(Enrollment.id)).filter_by(course_id=course_id).scalar()
        if enrollment_count > 0:
            return jsonify({"message": "Không thể xóa khóa học có học viên đang tham gia"}), 400
        db.session.delete(course)
        db.session.commit()
        return jsonify({"message": "Khóa học đã được xóa thành công"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Lỗi khi xóa khóa học: {e}")
        return jsonify({"message": f"Lỗi khi xóa khóa học: {str(e)}"}), 500


@instructor_bp.route("/api/courses/<int:course_id>/archive", methods=['PUT'])
@instructor_bp.route("/courses/<int:course_id>/archive", methods=['PUT'])
@jwt_required()
def archive_course(course_id):
    """
    Lưu trữ hoặc bỏ lưu trữ khóa học
    PUT /api/courses/<course_id>/archive
    Body: {
        "is_archived": true or false
    }
    """
    try:
        instructor_id = get_current_instructor_id()
        if not instructor_id:
            return jsonify({"message": "Unauthorized"}), 401
        course = Course.query.filter_by(id=course_id, instructor_id=instructor_id).first()
        if not course:
            return jsonify({"message": "Khóa học không tồn tại hoặc không có quyền truy cập"}), 404
        data = request.get_json()
        if 'is_archived' in data:
            # Nếu is_archived là True, đặt is_public thành False (không công khai)
            # Nếu is_archived là False, đặt is_public thành True (công khai)
            course.is_public = not data['is_archived']
        course.updated_at = datetime.utcnow()
        db.session.commit()
        status = 'active' if course.is_public else 'archived'
        return jsonify({
            "message": "Trạng thái khóa học đã được cập nhật",
            "id": course.id,
            "status": status
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Lỗi khi cập nhật trạng thái lưu trữ: {e}")
        return jsonify({"message": f"Lỗi: {str(e)}"}), 500


# =============================
#          CURRICULUM APIs
#  Sections (CourseSections) & Lessons
# =============================

def _serialize_section(section, include_lessons=False):
    data = {
        "id": section.id,
        "courseId": section.course_id,
        "title": section.title,
        "sortOrder": section.sort_order,
    }
    if include_lessons:
        data["lessons"] = [
            {
                "id": l.id,
                "sectionId": l.section_id,
                "title": l.title,
                "type": l.type,
                "content": l.content,
                "videoUrl": l.video_url,
                "durationSeconds": l.duration_seconds,
                "sortOrder": l.sort_order,
                "isPreview": bool(l.is_preview),
                "createdAt": l.created_at.isoformat() if l.created_at else None,
                "updatedAt": l.updated_at.isoformat() if l.updated_at else None,
            }
            for l in sorted(section.lessons, key=lambda x: (x.sort_order or 0, x.id))
        ]
    return data


@instructor_bp.route("/api/courses/<int:course_id>/curriculum", methods=['GET'])
@instructor_bp.route("/courses/<int:course_id>/curriculum", methods=['GET'])
@jwt_required()
def get_course_curriculum(course_id):
    try:
        instructor_id = get_current_instructor_id()
        if not instructor_id:
            return jsonify({"message": "Unauthorized"}), 401
        course = Course.query.filter_by(id=course_id, instructor_id=instructor_id).first()
        if not course:
            return jsonify({"message": "Khóa học không tồn tại hoặc không có quyền truy cập"}), 404
        sections = CourseSection.query.filter_by(course_id=course_id).order_by(CourseSection.sort_order, CourseSection.id).all()
        return jsonify([_serialize_section(s, include_lessons=True) for s in sections]), 200
    except Exception as e:
        print(f"Lỗi khi lấy curriculum: {e}")
        return jsonify({"message": "Lỗi server nội bộ"}), 500


@instructor_bp.route("/api/courses/<int:course_id>/sections", methods=['GET'])
@instructor_bp.route("/courses/<int:course_id>/sections", methods=['GET'])
@jwt_required()
def list_sections(course_id):
    try:
        instructor_id = get_current_instructor_id()
        if not instructor_id:
            return jsonify({"message": "Unauthorized"}), 401
        course = Course.query.filter_by(id=course_id, instructor_id=instructor_id).first()
        if not course:
            return jsonify({"message": "Khóa học không tồn tại hoặc không có quyền truy cập"}), 404
        sections = CourseSection.query.filter_by(course_id=course_id).order_by(CourseSection.sort_order, CourseSection.id).all()
        return jsonify([_serialize_section(s) for s in sections]), 200
    except Exception as e:
        print(f"Lỗi khi lấy sections: {e}")
        return jsonify({"message": "Lỗi server nội bộ"}), 500


@instructor_bp.route("/api/courses/<int:course_id>/sections", methods=['POST'])
@instructor_bp.route("/courses/<int:course_id>/sections", methods=['POST'])
@jwt_required()
def create_section(course_id):
    try:
        instructor_id = get_current_instructor_id()
        if not instructor_id:
            return jsonify({"message": "Unauthorized"}), 401
        course = Course.query.filter_by(id=course_id, instructor_id=instructor_id).first()
        if not course:
            return jsonify({"message": "Khóa học không tồn tại hoặc không có quyền truy cập"}), 404
        data = request.get_json() or {}
        title = (data.get('title') or '').strip()
        if not title:
            return jsonify({"message": "Thiếu tiêu đề chương (title)"}), 400
        sort_order = data.get('sort_order')
        if sort_order is None:
            # Tự động set sort_order = max + 1
            max_sort = db.session.query(db.func.max(CourseSection.sort_order)).filter_by(course_id=course_id).scalar() or 0
            sort_order = int(max_sort) + 1
        section = CourseSection(course_id=course_id, title=title, sort_order=sort_order)
        db.session.add(section)
        db.session.commit()
        return jsonify(_serialize_section(section)), 201
    except Exception as e:
        db.session.rollback()
        print(f"Lỗi khi tạo section: {e}")
        return jsonify({"message": f"Lỗi khi tạo section: {str(e)}"}), 500


@instructor_bp.route("/api/sections/<int:section_id>", methods=['PUT'])
@instructor_bp.route("/sections/<int:section_id>", methods=['PUT'])
@jwt_required()
def update_section(section_id):
    try:
        section = CourseSection.query.filter_by(id=section_id).first()
        if not section:
            return jsonify({"message": "Chương không tồn tại"}), 404
        data = request.get_json() or {}
        if 'title' in data and data['title'] is not None:
            section.title = data['title']
        if 'sort_order' in data and data['sort_order'] is not None:
            section.sort_order = int(data['sort_order'])
        db.session.commit()
        return jsonify(_serialize_section(section)), 200
    except Exception as e:
        db.session.rollback()
        print(f"Lỗi khi cập nhật section: {e}")
        return jsonify({"message": f"Lỗi khi cập nhật section: {str(e)}"}), 500


@instructor_bp.route("/api/sections/<int:section_id>", methods=['DELETE'])
@instructor_bp.route("/sections/<int:section_id>", methods=['DELETE'])
@jwt_required()
def delete_section(section_id):
    try:
        section = CourseSection.query.filter_by(id=section_id).first()
        if not section:
            return jsonify({"message": "Chương không tồn tại"}), 404
        # Xóa lessons trước để tránh lỗi FK nếu DB không cascade
        Lesson.query.filter_by(section_id=section.id).delete()
        db.session.delete(section)
        db.session.commit()
        return jsonify({"message": "Đã xóa chương"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Lỗi khi xóa section: {e}")
        return jsonify({"message": f"Lỗi khi xóa section: {str(e)}"}), 500


@instructor_bp.route("/api/sections/<int:section_id>/lessons", methods=['GET'])
@instructor_bp.route("/sections/<int:section_id>/lessons", methods=['GET'])
@jwt_required()
def list_lessons(section_id):
    try:
        section = CourseSection.query.filter_by(id=section_id).first()
        if not section:
            return jsonify({"message": "Chương không tồn tại"}), 404
        lessons = Lesson.query.filter_by(section_id=section_id).order_by(Lesson.sort_order, Lesson.id).all()
        return jsonify([
            {
                "id": l.id,
                "sectionId": l.section_id,
                "title": l.title,
                "type": l.type,
                "content": l.content,
                "videoUrl": l.video_url,
                "durationSeconds": l.duration_seconds,
                "sortOrder": l.sort_order,
                "isPreview": bool(l.is_preview),
                "createdAt": l.created_at.isoformat() if l.created_at else None,
                "updatedAt": l.updated_at.isoformat() if l.updated_at else None,
            } for l in lessons
        ]), 200
    except Exception as e:
        print(f"Lỗi khi lấy lessons: {e}")
        return jsonify({"message": "Lỗi server nội bộ"}), 500


@instructor_bp.route("/api/sections/<int:section_id>/lessons", methods=['POST'])
@instructor_bp.route("/sections/<int:section_id>/lessons", methods=['POST'])
@jwt_required()
def create_lesson(section_id):
    try:
        section = CourseSection.query.filter_by(id=section_id).first()
        if not section:
            return jsonify({"message": "Chương không tồn tại"}), 404
        data = request.get_json() or {}
        title = (data.get('title') or '').strip()
        if not title:
            return jsonify({"message": "Thiếu tiêu đề bài học (title)"}), 400
        lesson = Lesson(
            section_id=section_id,
            title=title,
            type=data.get('type', 'video'),
            content=data.get('content'),
            video_url=data.get('video_url') or data.get('videoUrl'),
            duration_seconds=data.get('duration_seconds') or data.get('durationSeconds'),
            sort_order=data.get('sort_order') or data.get('sortOrder') or 0,
            is_preview=bool(data.get('is_preview') or data.get('isPreview') or False),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(lesson)
        db.session.commit()
        return jsonify({
            "id": lesson.id,
            "sectionId": lesson.section_id,
            "title": lesson.title,
            "type": lesson.type,
            "content": lesson.content,
            "videoUrl": lesson.video_url,
            "durationSeconds": lesson.duration_seconds,
            "sortOrder": lesson.sort_order,
            "isPreview": bool(lesson.is_preview),
            "createdAt": lesson.created_at.isoformat() if lesson.created_at else None,
            "updatedAt": lesson.updated_at.isoformat() if lesson.updated_at else None,
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Lỗi khi tạo lesson: {e}")
        return jsonify({"message": f"Lỗi khi tạo lesson: {str(e)}"}), 500


@instructor_bp.route("/api/lessons/<int:lesson_id>", methods=['PUT'])
@instructor_bp.route("/lessons/<int:lesson_id>", methods=['PUT'])
@jwt_required()
def update_lesson(lesson_id):
    try:
        lesson = Lesson.query.filter_by(id=lesson_id).first()
        if not lesson:
            return jsonify({"message": "Bài học không tồn tại"}), 404
        data = request.get_json() or {}
        if 'title' in data and data['title'] is not None:
            lesson.title = data['title']
        if 'type' in data and data['type'] is not None:
            lesson.type = data['type']
        if 'content' in data:
            lesson.content = data['content']
        if 'video_url' in data or 'videoUrl' in data:
            lesson.video_url = data.get('video_url') or data.get('videoUrl')
        if 'duration_seconds' in data or 'durationSeconds' in data:
            lesson.duration_seconds = data.get('duration_seconds') or data.get('durationSeconds')
        if 'sort_order' in data or 'sortOrder' in data:
            lesson.sort_order = data.get('sort_order') or data.get('sortOrder')
        if 'is_preview' in data or 'isPreview' in data:
            lesson.is_preview = bool(data.get('is_preview') or data.get('isPreview'))
        lesson.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify({
            "id": lesson.id,
            "sectionId": lesson.section_id,
            "title": lesson.title,
            "type": lesson.type,
            "content": lesson.content,
            "videoUrl": lesson.video_url,
            "durationSeconds": lesson.duration_seconds,
            "sortOrder": lesson.sort_order,
            "isPreview": bool(lesson.is_preview),
            "createdAt": lesson.created_at.isoformat() if lesson.created_at else None,
            "updatedAt": lesson.updated_at.isoformat() if lesson.updated_at else None,
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Lỗi khi cập nhật lesson: {e}")
        return jsonify({"message": f"Lỗi khi cập nhật lesson: {str(e)}"}), 500


@instructor_bp.route("/lessons/<int:lesson_id>", methods=['DELETE'])
@jwt_required()
def delete_lesson(lesson_id):
    try:
        lesson = Lesson.query.filter_by(id=lesson_id).first()
        if not lesson:
            return jsonify({"message": "Bài học không tồn tại"}), 404
        db.session.delete(lesson)
        db.session.commit()
        return jsonify({"message": "Đã xóa bài học"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Lỗi khi xóa lesson: {e}")
        return jsonify({"message": f"Lỗi khi xóa lesson: {str(e)}"}), 500


# =============================
#             TEST APIs
#  Tests under Lesson + Questions under Test
# =============================

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
    if include_counters:
        data["questionCount"] = len(t.questions or [])
    return data


def _serialize_question(q, include_choices=True):
    data = {
        "id": q.id,
        "testId": q.test_id,
        "type": q.type,
        "content": q.content,
        "points": q.points,
        "sortOrder": q.sort_order,
    }
    if include_choices:
        data["choices"] = [
            {
                "id": c.id,
                "questionId": c.question_id,
                "content": c.content,
                "isCorrect": bool(c.is_correct),
                "sortOrder": c.sort_order,
            } for c in sorted(q.choices, key=lambda x: (x.sort_order or 0, x.id))
        ]
    return data


@instructor_bp.route("/api/lessons/<int:lesson_id>/tests", methods=['GET'])
@instructor_bp.route("/lessons/<int:lesson_id>/tests", methods=['GET'])
@jwt_required()
def list_tests(lesson_id):
    try:
        lesson = Lesson.query.filter_by(id=lesson_id).first()
        if not lesson:
            return jsonify({"message": "Bài học không tồn tại"}), 404
        tests = Test.query.filter_by(lesson_id=lesson_id).order_by(Test.id).all()
        return jsonify([_serialize_test(t, include_counters=True) for t in tests]), 200
    except Exception as e:
        print(f"Lỗi khi lấy tests: {e}")
        return jsonify({"message": "Lỗi server nội bộ"}), 500


@instructor_bp.route("/api/lessons/<int:lesson_id>/tests", methods=['POST'])
@instructor_bp.route("/lessons/<int:lesson_id>/tests", methods=['POST'])
@jwt_required()
def create_test(lesson_id):
    try:
        lesson = Lesson.query.filter_by(id=lesson_id).first()
        if not lesson:
            return jsonify({"message": "Bài học không tồn tại"}), 404
        data = request.get_json() or {}
        title = (data.get('title') or '').strip()
        if not title:
            return jsonify({"message": "Thiếu tiêu đề bài test (title)"}), 400
        test = Test(
            lesson_id=lesson_id,
            title=title,
            is_placement=bool(data.get('is_placement') or data.get('isPlacement') or False),
            time_limit_minutes=data.get('time_limit_minutes') or data.get('timeLimitMinutes') or 0,
            attempts_allowed=data.get('attempts_allowed') or data.get('attemptsAllowed') or 1,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.session.add(test)
        db.session.commit()
        return jsonify(_serialize_test(test)), 201
    except Exception as e:
        db.session.rollback()
        print(f"Lỗi khi tạo test: {e}")
        return jsonify({"message": f"Lỗi khi tạo test: {str(e)}"}), 500


@instructor_bp.route("/tests/<int:test_id>", methods=['GET'])
@jwt_required()
def get_test_detail(test_id):
    try:
        t = Test.query.filter_by(id=test_id).first()
        if not t:
            return jsonify({"message": "Bài test không tồn tại"}), 404
        return jsonify(_serialize_test(t, include_counters=True)), 200
    except Exception as e:
        print(f"Lỗi khi lấy chi tiết test: {e}")
        return jsonify({"message": "Lỗi server nội bộ"}), 500


@instructor_bp.route("/api/tests/<int:test_id>", methods=['PUT'])
@instructor_bp.route("/tests/<int:test_id>", methods=['PUT'])
@jwt_required()
def update_test(test_id):
    try:
        t = Test.query.filter_by(id=test_id).first()
        if not t:
            return jsonify({"message": "Bài test không tồn tại"}), 404
        data = request.get_json() or {}
        if 'title' in data and data['title'] is not None:
            t.title = data['title']
        if 'is_placement' in data or 'isPlacement' in data:
            t.is_placement = bool(data.get('is_placement') or data.get('isPlacement'))
        if 'time_limit_minutes' in data or 'timeLimitMinutes' in data:
            t.time_limit_minutes = data.get('time_limit_minutes') or data.get('timeLimitMinutes') or 0
        if 'attempts_allowed' in data or 'attemptsAllowed' in data:
            t.attempts_allowed = data.get('attempts_allowed') or data.get('attemptsAllowed') or 1
        t.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify(_serialize_test(t)), 200
    except Exception as e:
        db.session.rollback()
        print(f"Lỗi khi cập nhật test: {e}")
        return jsonify({"message": f"Lỗi khi cập nhật test: {str(e)}"}), 500


@instructor_bp.route("/tests/<int:test_id>", methods=['DELETE'])
@jwt_required()
def delete_test(test_id):
    try:
        t = Test.query.filter_by(id=test_id).first()
        if not t:
            return jsonify({"message": "Bài test không tồn tại"}), 404
        # xóa choices và questions trước
        questions = Question.query.filter_by(test_id=t.id).all()
        for q in questions:
            Choice.query.filter_by(question_id=q.id).delete()
        Question.query.filter_by(test_id=t.id).delete()
        db.session.delete(t)
        db.session.commit()
        return jsonify({"message": "Đã xóa bài test"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Lỗi khi xóa test: {e}")
        return jsonify({"message": f"Lỗi khi xóa test: {str(e)}"}), 500


@instructor_bp.route("/tests/<int:test_id>/questions", methods=['GET'])
@jwt_required()
def list_questions(test_id):
    try:
        t = Test.query.filter_by(id=test_id).first()
        if not t:
            return jsonify({"message": "Bài test không tồn tại"}), 404
        questions = Question.query.filter_by(test_id=test_id).order_by(Question.sort_order, Question.id).all()
        return jsonify([_serialize_question(q) for q in questions]), 200
    except Exception as e:
        print(f"Lỗi khi lấy questions: {e}")
        return jsonify({"message": "Lỗi server nội bộ"}), 500


@instructor_bp.route("/api/tests/<int:test_id>/questions", methods=['POST'])
@instructor_bp.route("/tests/<int:test_id>/questions", methods=['POST'])
@jwt_required()
def create_question(test_id):
    try:
        t = Test.query.filter_by(id=test_id).first()
        if not t:
            return jsonify({"message": "Bài test không tồn tại"}), 404
        data = request.get_json() or {}
        qtype = data.get('type') or 'single_choice'
        content = (data.get('content') or '').strip()
        if not content:
            return jsonify({"message": "Thiếu nội dung câu hỏi (content)"}), 400
        points = data.get('points') or 1
        # sort_order: max + 1
        max_sort = db.session.query(db.func.max(Question.sort_order)).filter_by(test_id=test_id).scalar() or 0
        question = Question(test_id=test_id, type=qtype, content=content, points=points, sort_order=int(max_sort) + 1)
        db.session.add(question)
        db.session.flush()  # có id cho choices
        # choices optional
        choices = data.get('choices') or []
        for idx, c in enumerate(choices):
            choice_text = c.get('text', '').strip() or c.get('content', '').strip()
            if choice_text:  # Only add non-empty choices
                ch = Choice(
                    question_id=question.id,
                    content=choice_text,
                    is_correct=bool(c.get('is_correct') or c.get('isCorrect') or False),
                    sort_order=c.get('sort_order') or c.get('sortOrder') or idx,
                )
                db.session.add(ch)
        db.session.commit()
        return jsonify(_serialize_question(question)), 201
    except Exception as e:
        db.session.rollback()
        print(f"Lỗi khi tạo question: {e}")
        return jsonify({"message": f"Lỗi khi tạo câu hỏi: {str(e)}"}), 500


@instructor_bp.route("/api/questions/<int:question_id>", methods=['PUT'])
@instructor_bp.route("/questions/<int:question_id>", methods=['PUT'])
@jwt_required()
def update_question(question_id):
    try:
        q = Question.query.filter_by(id=question_id).first()
        if not q:
            return jsonify({"message": "Câu hỏi không tồn tại"}), 404
        data = request.get_json() or {}
        if 'type' in data and data['type'] is not None:
            q.type = data['type']
        if 'content' in data and data['content'] is not None:
            q.content = data['content']
        if 'points' in data and data['points'] is not None:
            q.points = data['points']
        if 'sort_order' in data or 'sortOrder' in data:
            q.sort_order = data.get('sort_order') or data.get('sortOrder')
        # Optional: replace all choices if provided
        if 'choices' in data and isinstance(data['choices'], list):
            Choice.query.filter_by(question_id=q.id).delete()
            for idx, c in enumerate(data['choices']):
                choice_text = c.get('text', '').strip() or c.get('content', '').strip()
                if choice_text:  # Only add non-empty choices
                    ch = Choice(
                        question_id=q.id,
                        content=choice_text,
                        is_correct=bool(c.get('is_correct') or c.get('isCorrect') or False),
                        sort_order=c.get('sort_order') or c.get('sortOrder') or idx,
                    )
                    db.session.add(ch)
        db.session.commit()
        return jsonify(_serialize_question(q)), 200
    except Exception as e:
        db.session.rollback()
        print(f"Lỗi khi cập nhật question: {e}")
        return jsonify({"message": f"Lỗi khi cập nhật câu hỏi: {str(e)}"}), 500


@instructor_bp.route("/api/questions/<int:question_id>", methods=['DELETE'])
@instructor_bp.route("/questions/<int:question_id>", methods=['DELETE'])
@jwt_required()
def delete_question(question_id):
    try:
        q = Question.query.filter_by(id=question_id).first()
        if not q:
            return jsonify({"message": "Câu hỏi không tồn tại"}), 404
        Choice.query.filter_by(question_id=q.id).delete()
        db.session.delete(q)
        db.session.commit()
        return jsonify({"message": "Đã xóa câu hỏi"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Lỗi khi xóa question: {e}")
        return jsonify({"message": f"Lỗi khi xóa câu hỏi: {str(e)}"}), 500


def generate_slug(title):
    """
    Tạo slug từ tiêu đề
    Ví dụ: "JavaScript Fundamentals" -> "javascript-fundamentals"
    """
    # Chuyển thành chữ thường
    slug = title.lower()
    
    # Loại bỏ các ký tự đặc biệt, giữ chữ số và dấu cách
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    
    # Thay thế khoảng trắng bằng dấu gạch ngang
    slug = re.sub(r'\s+', '-', slug)
    
    # Loại bỏ các dấu gạch ngang liên tiếp
    slug = re.sub(r'-+', '-', slug)
    
    # Loại bỏ dấu gạch ngang ở đầu và cuối
    slug = slug.strip('-')
    
    return slug

@instructor_bp.route('/api/tests/<int:test_id>', methods=['GET'])
@jwt_required()
def get_test(test_id):
    try:
        test = Test.query.get(test_id)
        if not test:
            return jsonify({'message': 'Test not found'}), 404

        res = {
            'id': test.id,
            'title': test.title,
            'timeLimitMinutes': test.time_limit_minutes or 0,
            'attemptsAllowed': test.attempts_allowed or 1,
            'isPlacement': bool(test.is_placement)
        }

        res['questions'] = []
        questions = Question.query.filter_by(test_id=test.id).order_by(Question.sort_order, Question.id).all()
        for q in questions:
            q_json = {
                'id': q.id,
                'content': q.content,
                'points': q.points or 1,
                'difficulty': 'medium',  # Default since this field doesn't exist in model
                'choices': []
            }
            choices = Choice.query.filter_by(question_id=q.id).order_by(Choice.sort_order, Choice.id).all()
            for c in choices:
                q_json['choices'].append({
                    'id': c.id,
                    'text': c.content,  # Use 'content' field from model
                    'isCorrect': bool(c.is_correct)
                })
            res['questions'].append(q_json)

        return jsonify(res)
    except Exception as e:
        print(f"Error getting test details: {e}")
        return jsonify({'message': 'Internal server error'}), 500


# =============================
#            DASHBOARD APIs
# =============================

@instructor_bp.route('/api/instructor/dashboard', methods=['GET'])
@jwt_required()
def get_instructor_dashboard():
    """Lấy dữ liệu dashboard cho giảng viên.
    Nếu không truyền instructor_id sẽ lấy từ JWT."""
    try:
        instructor_id = request.args.get('instructor_id', type=int)
        if not instructor_id:
            instructor_id = get_current_instructor_id()
        if not instructor_id:
            return jsonify({'message': 'Unauthorized'}), 401
        instructor = Instructor.query.get(instructor_id)
        if not instructor:
            return jsonify({'message': 'Giảng viên không tồn tại'}), 404
        user = instructor.user
        if not user:
            return jsonify({'message': 'Người dùng không tồn tại'}), 404
        courses = Course.query.filter_by(instructor_id=instructor_id).all()
        total_courses = len(courses)
        total_students = 0
        total_revenue = 0.0
        ratings = []
        for course in courses:
            enrollments = Enrollment.query.filter_by(course_id=course.id).all()
            total_students += len(enrollments)
            total_revenue += float(course.price or 0) * len([e for e in enrollments if getattr(e,'status',None)== 'completed'])
            ratings.append(4.5)
        average_rating = sum(ratings) / len(ratings) if ratings else 0.0
        recent_courses = courses[-5:][::-1]
        recent_courses_data = []
        for course in recent_courses:
            enrollments = Enrollment.query.filter_by(course_id=course.id).all()
            recent_courses_data.append({
                'id': course.id,
                'title': course.title,
                'description': course.description,
                'level': course.level,
                'price': float(course.price or 0),
                'students': len(enrollments),
                'status': 'active' if course.is_public else 'draft',
                'createdAt': course.created_at.isoformat() if course.created_at else None,
                'updatedAt': course.updated_at.isoformat() if course.updated_at else None
            })
        dashboard_data = {
            'instructor': {
                'id': instructor.id,
                'name': getattr(user,'full_name',None) or getattr(user,'FullName',None) or getattr(user,'name',None),
                'email': getattr(user,'email',None) or getattr(user,'Email',None),
                'avatar': getattr(user,'avatar_url',None) or getattr(user,'AvatarUrl',None),
                'expertise': getattr(instructor,'expertise',None),
                'yearsExperience': getattr(instructor,'years_experience',None)
            },
            'stats': {
                'totalCourses': total_courses,
                'totalStudents': total_students,
                'averageRating': round(average_rating, 1),
                'totalRevenue': round(total_revenue, 2)
            },
            'recentCourses': recent_courses_data
        }
        return jsonify(dashboard_data), 200
    except Exception as e:
        print(f'Error getting dashboard: {e}')
        return jsonify({'message': 'Lỗi server nội bộ'}), 500

@instructor_bp.route('/api/instructor/statistics', methods=['GET'])
@jwt_required()
def get_instructor_statistics():
    """Chi tiết thống kê giảng viên; instructor_id tùy chọn, fallback JWT."""
    try:
        instructor_id = request.args.get('instructor_id', type=int)
        if not instructor_id:
            instructor_id = get_current_instructor_id()
        if not instructor_id:
            return jsonify({'message': 'Unauthorized'}), 401
        instructor = Instructor.query.get(instructor_id)
        if not instructor:
            return jsonify({'message': 'Giảng viên không tồn tại'}), 404
        courses = Course.query.filter_by(instructor_id=instructor_id).all()
        
        stats = {
            'coursesByLevel': {
                'beginner': 0,
                'intermediate': 0,
                'advanced': 0
            },
            'coursesByStatus': {
                'active': 0,
                'draft': 0
            },
            'studentsByStatus': {
                'enrolled': 0,
                'completed': 0,
                'dropped': 0
            },
            'averageStudentsPerCourse': 0,
            'totalLessons': 0,
            'totalTests': 0
        }
        
        total_students_by_status = {'enrolled': 0, 'completed': 0, 'dropped': 0}
        
        for course in courses:
            # Cập nhật thống kê theo level
            stats['coursesByLevel'][course.level] = stats['coursesByLevel'].get(course.level, 0) + 1
            
            # Cập nhật thống kê theo status
            if course.is_public:
                stats['coursesByStatus']['active'] += 1
            else:
                stats['coursesByStatus']['draft'] += 1
            
            # Đếm enrollments
            enrollments = Enrollment.query.filter_by(course_id=course.id).all()
            for enrollment in enrollments:
                total_students_by_status[enrollment.status] = total_students_by_status.get(enrollment.status, 0) + 1
            
            # Đếm sections, lessons, tests
            sections = CourseSection.query.filter_by(course_id=course.id).all()
            for section in sections:
                lessons = Lesson.query.filter_by(section_id=section.id).all()
                stats['totalLessons'] += len(lessons)
                
                for lesson in lessons:
                    tests = Test.query.filter_by(lesson_id=lesson.id).all()
                    stats['totalTests'] += len(tests)
        
        stats['studentsByStatus'] = total_students_by_status
        
        if courses:
            total_students = sum(total_students_by_status.values())
            stats['averageStudentsPerCourse'] = round(total_students / len(courses), 1)
        
        return jsonify(stats), 200
        
    except Exception as e:
        print(f'Error getting statistics: {e}')
        return jsonify({'message': 'Lỗi server nội bộ'}), 500


@instructor_bp.route('/api/instructor/reports', methods=['GET'])
@jwt_required()
def get_instructor_reports():
    """
    Get comprehensive analytics and reports for instructor.
    If instructor_id not provided, derive from JWT.
    """
    try:
        instructor_id = request.args.get('instructor_id', type=int)
        if not instructor_id:
            instructor_id = get_current_instructor_id()
        if not instructor_id:
            return jsonify({'message': 'Unauthorized'}), 401
        instructor = Instructor.query.get(instructor_id)
        if not instructor:
            return jsonify({'message': 'Instructor not found'}), 404
        
        courses = Course.query.filter_by(instructor_id=instructor_id).all()
        
        # Initialize report structure
        report = {
            'overview': {
                'totalStudents': 0,
                'activeCourses': 0,
                'avgCompletionRate': 0,
                'avgScore': 0
            },
            'trends': {
                'studentRegistrations': [],  # Monthly data for last 12 months
                'completionRates': [],       # Monthly completion rates
            },
            'coursePerformance': [],         # Individual course metrics
            'studentDistribution': {
                'completed': 0,
                'inProgress': 0,
                'dropped': 0
            },
            'scoresByTopic': []              # Average scores by course/topic
        }
        
        # Calculate overview metrics
        total_enrollments = 0
        total_completed = 0
        total_scores = []
        active_courses = 0
        
        for course in courses:
            if course.is_public:
                active_courses += 1
            
            enrollments = Enrollment.query.filter_by(course_id=course.id).all()
            course_enrollments = len(enrollments)
            total_enrollments += course_enrollments
            
            course_completed = 0
            course_in_progress = 0
            course_dropped = 0
            course_scores = []
            
            for enrollment in enrollments:
                if enrollment.status == 'completed':
                    course_completed += 1
                    total_completed += 1
                    report['studentDistribution']['completed'] += 1
                    if enrollment.progress:
                        course_scores.append(enrollment.progress)
                        total_scores.append(enrollment.progress)
                elif enrollment.status == 'enrolled':
                    course_in_progress += 1
                    report['studentDistribution']['inProgress'] += 1
                elif enrollment.status == 'dropped':
                    course_dropped += 1
                    report['studentDistribution']['dropped'] += 1
            
            # Course performance data
            completion_rate = (course_completed / course_enrollments * 100) if course_enrollments > 0 else 0
            avg_score = (sum(course_scores) / len(course_scores)) if course_scores else 0
            
            report['coursePerformance'].append({
                'courseId': course.id,
                'courseName': course.title,
                'description': course.description or '',
                'students': course_enrollments,
                'completed': course_completed,
                'inProgress': course_in_progress,
                'completionRate': round(completion_rate, 1)
            })
            
            # Scores by topic
            if course_scores:
                report['scoresByTopic'].append({
                    'topic': course.title,
                    'avgScore': round(avg_score, 1),
                    'studentCount': len(course_scores)
                })
        
        # Overview calculations
        report['overview']['totalStudents'] = total_enrollments
        report['overview']['activeCourses'] = active_courses
        report['overview']['avgCompletionRate'] = round((total_completed / total_enrollments * 100), 1) if total_enrollments > 0 else 0
        report['overview']['avgScore'] = round((sum(total_scores) / len(total_scores)), 1) if total_scores else 0
        
        # Generate time-series data for last 12 months (simulated for now)
        # In production, this should query actual enrollment/completion dates
        import random
        from datetime import datetime, timedelta
        
        base_students = total_enrollments // 12 if total_enrollments > 0 else 10
        for i in range(12):
            month_date = datetime.now() - timedelta(days=30 * (11 - i))
            month_name = month_date.strftime('%b')
            
            # Simulated growing trend
            students = base_students + random.randint(-5, 10) + i * 2
            report['trends']['studentRegistrations'].append({
                'month': month_name,
                'count': max(0, students)
            })
            
            # Simulated completion rates
            completion_rate = report['overview']['avgCompletionRate'] + random.uniform(-10, 10)
            report['trends']['completionRates'].append({
                'month': month_name,
                'rate': round(max(0, min(100, completion_rate)), 1)
            })
        
        return jsonify(report), 200
        
    except Exception as e:
        print(f'Error getting reports: {e}')
        import traceback
        traceback.print_exc()
        return jsonify({'message': 'Internal server error', 'error': str(e)}), 500


@instructor_bp.route('/api/courses/<int:course_id>', methods=['GET'])
def get_course(course_id):
    try:
        course = Course.query.filter_by(id=course_id).first()
        if not course:
            return jsonify({'message': 'Course not found'}), 404
        status = 'active' if course.is_public else 'draft'
        img = course.image_url or f"/images/course/{course.id}.jpg"
        return jsonify({
            'id': course.id,
            'title': course.title,
            'description': course.description,
            'price': float(course.price) if course.price is not None else 0,
            'image_url': course.image_url,
            'thumbnail': img,
            'status': status
        }), 200
    except Exception as e:
        print('Error fetching course:', e)
        return jsonify({'message': 'Internal server error'}), 500


# Đã có hàm create_course ở trên (dòng 63) với đầy đủ validation
# ========== New: Google Drive upload ==========
@instructor_bp.route('/api/upload/video', methods=['POST'])
def upload_video_to_cloudinary():
    """
    Upload a video file to Cloudinary.
    Form-Data:
      - file: binary file
    Response: { publicId, url }
    """
    from flask import request, jsonify
    try:
        if 'file' not in request.files:
            return jsonify({'message': 'Missing file field'}), 400
        f = request.files['file']
        if f.filename == '':
            return jsonify({'message': 'Empty filename'}), 400

        from app.utils.cloudinary_upload import upload_video
        public_id, secure_url = upload_video(f.stream, f.filename)

        return jsonify({'publicId': public_id, 'url': secure_url}), 200
    except Exception as e:
        import traceback
        print(f"❌ Cloudinary upload error: {e}\n{traceback.format_exc()}")
        return jsonify({'message': f'Upload failed: {str(e)}'}), 500


@instructor_bp.route('/upload/thumbnail', methods=['POST'])
@instructor_bp.route('/api/instructor/upload/thumbnail', methods=['POST'])
@jwt_required()
def upload_course_thumbnail():
    try:
        # Accept any authenticated user to upload thumbnail
        user_id = get_jwt_identity()
        if not user_id:
            return jsonify({'message': 'Unauthorized'}), 401
        if 'file' not in request.files:
            return jsonify({'message': 'Missing file'}), 400
        f = request.files['file']
        try:
            from app.utils.cloudinary_upload import cloudinary, DEFAULT_FOLDER
            result = cloudinary.uploader.upload(
                f,
                folder=DEFAULT_FOLDER,
                overwrite=True,
                resource_type='image',
            )
            url = result.get('secure_url') or result.get('url')
            return jsonify({'success': True, 'url': url, 'public_id': result.get('public_id')}), 200
        except Exception as e:
            print('Cloudinary upload error:', e)
            return jsonify({'message': 'Upload failed'}), 500
    except Exception as e:
        print('Upload thumbnail error:', e)
        return jsonify({'message': 'Internal server error'}), 500