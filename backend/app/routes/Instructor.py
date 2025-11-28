from flask import Blueprint, jsonify, request
from datetime import datetime
# Import db và các Models cần thiết
from ..models.model import db, Course, Instructor, CourseSection, Lesson, Test, Question, Choice, Enrollment
import re
import os

# Khởi tạo Blueprint cho các routes liên quan đến Giảng viên
instructor_bp = Blueprint('instructor', __name__)

@instructor_bp.route("/api/courses", methods=['GET'])
@instructor_bp.route("/courses", methods=['GET'])
def get_instructor_courses():
    """
    Lấy danh sách khóa học của một Giảng viên dựa trên instructor_id.
    Ví dụ: /api/courses?instructor_id=2
    """
    # 1. Lấy instructor_id từ query parameters
    instructor_id = request.args.get('instructor_id', type=int)

    if instructor_id is None:
        # Nếu không có instructor_id, trả về danh sách trống hoặc lỗi
        return jsonify({"message": "Thiếu tham số instructor_id"}), 400

    try:
        # 2. Truy vấn các khóa học của instructor_id đã cho
        courses = Course.query.filter_by(instructor_id=instructor_id).all()

        # 3. Chuyển đổi kết quả sang định dạng JSON
        course_list = []
        for course in courses:
            # Map cột 'is_public' sang 'status' string mà frontend mong đợi
            # Giả định: is_public=True là 'active', False là 'draft'
            status = 'active' if course.is_public else 'draft'

            # CHÚ Ý: Các trường 'students', 'rating', 'thumbnail' là dữ liệu giả lập 
            # vì không có trong Model Course ban đầu. Bạn cần tính toán thực tế sau.
            course_data = {
                "id": course.id,
                "title": course.title,
                "description": course.description,
                "price": float(course.price) if course.price is not None else 0.00,
                "level": course.level,
                "status": status,
                # Dữ liệu giả lập cho Frontend
                "students": 120, 
                "rating": "4.5", 
                "thumbnail": f"/images/course/{course.id}.jpg",
                "updatedAt": course.updated_at.isoformat() if course.updated_at else None
            }
            course_list.append(course_data)

        # 4. Trả về danh sách khóa học
        return jsonify(course_list)

    except Exception as e:
        print(f"Lỗi khi truy vấn database: {e}")
        return jsonify({"message": "Lỗi server nội bộ khi lấy dữ liệu khóa học"}), 500


@instructor_bp.route("/api/courses", methods=['POST'])
@instructor_bp.route("/courses", methods=['POST'])
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
        "instructor_id": 2,
        "category": "Web Development",
        "requirements": "HTML/CSS cơ bản"
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'description', 'price', 'instructor_id']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"message": f"Thiếu trường bắt buộc: {field}"}), 400
        
        # Check if instructor exists
        instructor = Instructor.query.filter_by(id=data['instructor_id']).first()
        if not instructor:
            return jsonify({"message": "Giảng viên không tồn tại"}), 404
        
        # Generate slug from title
        slug = generate_slug(data['title'])
        
        # Check if slug already exists
        existing_course = Course.query.filter_by(slug=slug).first()
        if existing_course:
            slug = f"{slug}-{datetime.utcnow().timestamp()}"
        
        # Map status to is_public
        is_public = data.get('status', 'draft') == 'active'
        
        # Create new course
        new_course = Course(
            instructor_id=data['instructor_id'],
            title=data['title'],
            slug=slug,
            description=data['description'],
            price=data.get('price', 0),
            currency=data.get('currency', 'VND'),
            level=data.get('level', 'beginner'),
            is_public=is_public,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.session.add(new_course)
        db.session.commit()
        
        return jsonify({
            "message": "Khóa học đã được tạo thành công",
            "id": new_course.id,
            "title": new_course.title,
            "slug": new_course.slug
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Lỗi khi tạo khóa học: {e}")
        return jsonify({"message": f"Lỗi khi tạo khóa học: {str(e)}"}), 500


@instructor_bp.route("/courses/<int:course_id>", methods=['GET'])
def get_course_detail(course_id):
    """
    Xem chi tiết một khóa học
    GET /api/courses/<course_id>
    """
    try:
        course = Course.query.filter_by(id=course_id).first()
        
        if not course:
            return jsonify({"message": "Khóa học không tồn tại"}), 404
        
        status = 'active' if course.is_public else 'draft'
        
        course_data = {
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "price": float(course.price) if course.price is not None else 0.00,
            "level": course.level,
            "status": status,
            "instructor_id": course.instructor_id,
            "students": 0,  # Tính từ Enrollment table
            "rating": 0.0,  # Tính từ Reviews table
            "lessons": 0,   # Tính từ Lesson table
            "duration": 0,  # Tính từ Lesson table
            "thumbnail": f"/images/course/{course.id}.jpg",
            "createdAt": course.created_at.isoformat() if course.created_at else None,
            "updatedAt": course.updated_at.isoformat() if course.updated_at else None
        }
        
        return jsonify(course_data), 200
        
    except Exception as e:
        print(f"Lỗi khi lấy chi tiết khóa học: {e}")
        return jsonify({"message": "Lỗi server nội bộ"}), 500


@instructor_bp.route("/courses/<int:course_id>", methods=['PUT'])
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
        course = Course.query.filter_by(id=course_id).first()
        
        if not course:
            return jsonify({"message": "Khóa học không tồn tại"}), 404
        
        data = request.get_json()
        
        # Update fields
        if 'title' in data:
            course.title = data['title']
            # Regenerate slug if title changed
            course.slug = generate_slug(data['title'])
        
        if 'description' in data:
            course.description = data['description']
        
        if 'price' in data:
            course.price = data['price']
        
        if 'level' in data:
            course.level = data['level']
        
        if 'status' in data:
            course.is_public = data['status'] == 'active'
        
        course.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            "message": "Khóa học đã được cập nhật thành công",
            "id": course.id,
            "title": course.title
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Lỗi khi cập nhật khóa học: {e}")
        return jsonify({"message": f"Lỗi khi cập nhật khóa học: {str(e)}"}), 500


@instructor_bp.route("/courses/<int:course_id>", methods=['DELETE'])
def delete_course(course_id):
    """
    Xóa khóa học
    DELETE /api/courses/<course_id>
    """
    try:
        course = Course.query.filter_by(id=course_id).first()
        
        if not course:
            return jsonify({"message": "Khóa học không tồn tại"}), 404
        
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


@instructor_bp.route("/courses/<int:course_id>/archive", methods=['PUT'])
def archive_course(course_id):
    """
    Lưu trữ hoặc bỏ lưu trữ khóa học
    PUT /api/courses/<course_id>/archive
    Body: {
        "is_archived": true or false
    }
    """
    try:
        course = Course.query.filter_by(id=course_id).first()
        
        if not course:
            return jsonify({"message": "Khóa học không tồn tại"}), 404
        
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
def get_course_curriculum(course_id):
    try:
        course = Course.query.filter_by(id=course_id).first()
        if not course:
            return jsonify({"message": "Khóa học không tồn tại"}), 404
        sections = CourseSection.query.filter_by(course_id=course_id).order_by(CourseSection.sort_order, CourseSection.id).all()
        return jsonify([_serialize_section(s, include_lessons=True) for s in sections]), 200
    except Exception as e:
        print(f"Lỗi khi lấy curriculum: {e}")
        return jsonify({"message": "Lỗi server nội bộ"}), 500


@instructor_bp.route("/api/courses/<int:course_id>/sections", methods=['GET'])
@instructor_bp.route("/courses/<int:course_id>/sections", methods=['GET'])
def list_sections(course_id):
    try:
        course = Course.query.filter_by(id=course_id).first()
        if not course:
            return jsonify({"message": "Khóa học không tồn tại"}), 404
        sections = CourseSection.query.filter_by(course_id=course_id).order_by(CourseSection.sort_order, CourseSection.id).all()
        return jsonify([_serialize_section(s) for s in sections]), 200
    except Exception as e:
        print(f"Lỗi khi lấy sections: {e}")
        return jsonify({"message": "Lỗi server nội bộ"}), 500


@instructor_bp.route("/api/courses/<int:course_id>/sections", methods=['POST'])
@instructor_bp.route("/courses/<int:course_id>/sections", methods=['POST'])
def create_section(course_id):
    try:
        course = Course.query.filter_by(id=course_id).first()
        if not course:
            return jsonify({"message": "Khóa học không tồn tại"}), 404
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
def get_instructor_dashboard():
    """
    Lấy dữ liệu dashboard cho giảng viên
    Query: ?instructor_id=X
    Response: {
        instructor: { name, email, avatar },
        stats: { totalCourses, totalStudents, averageRating, totalRevenue },
        recentCourses: [...]
    }
    """
    try:
        instructor_id = request.args.get('instructor_id', type=int)
        
        if not instructor_id:
            return jsonify({'message': 'Thiếu tham số instructor_id'}), 400
        
        # Lấy thông tin giảng viên
        instructor = Instructor.query.get(instructor_id)
        if not instructor:
            return jsonify({'message': 'Giảng viên không tồn tại'}), 404
        
        user = instructor.user
        if not user:
            return jsonify({'message': 'Người dùng không tồn tại'}), 404
        
        # Lấy danh sách khóa học
        courses = Course.query.filter_by(instructor_id=instructor_id).all()
        
        # Tính toán thống kê
        total_courses = len(courses)
        total_students = 0
        total_revenue = 0.0
        ratings = []
        
        for course in courses:
            # Đếm học viên đăng ký
            enrollments = Enrollment.query.filter_by(course_id=course.id).all()
            total_students += len(enrollments)
            
            # Tính doanh thu (giả định là price * số học viên đã thanh toán)
            total_revenue += float(course.price or 0) * len([e for e in enrollments if e.status == 'completed'])
            
            # Giả định đánh giá (có thể thêm bảng Rating sau)
            ratings.append(4.5)
        
        average_rating = sum(ratings) / len(ratings) if ratings else 0.0
        
        # Lấy 5 khóa học gần đây
        recent_courses = courses[-5:][::-1]
        recent_courses_data = []
        
        for course in recent_courses:
            enrollments = Enrollment.query.filter_by(course_id=course.id).all()
            course_data = {
                'id': course.id,
                'title': course.title,
                'description': course.description,
                'level': course.level,
                'price': float(course.price or 0),
                'students': len(enrollments),
                'status': 'active' if course.is_public else 'draft',
                'createdAt': course.created_at.isoformat() if course.created_at else None,
                'updatedAt': course.updated_at.isoformat() if course.updated_at else None
            }
            recent_courses_data.append(course_data)
        
        dashboard_data = {
            'instructor': {
                'id': instructor.id,
                'name': user.full_name,
                'email': user.email,
                'avatar': user.avatar_url,
                'expertise': instructor.expertise,
                'yearsExperience': instructor.years_experience
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
def get_instructor_statistics():
    """
    Lấy thống kê chi tiết cho giảng viên
    Query: ?instructor_id=X
    """
    try:
        instructor_id = request.args.get('instructor_id', type=int)
        
        if not instructor_id:
            return jsonify({'message': 'Thiếu tham số instructor_id'}), 400
        
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
def get_instructor_reports():
    """
    Get comprehensive analytics and reports for instructor
    Query: ?instructor_id=X
    Returns: Time-series data, course metrics, student progress, and performance analytics
    """
    try:
        instructor_id = request.args.get('instructor_id', type=int)
        
        if not instructor_id:
            return jsonify({'message': 'Missing instructor_id parameter'}), 400
        
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
                'courseName': course.title,
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
        return jsonify({
            'id': course.id,
            'title': course.title,
            'description': course.description,
            'price': float(course.price) if course.price is not None else 0,
            'thumbnail': getattr(course, 'thumbnail', None),
            'status': course.status or 'draft'
        }), 200
    except Exception as e:
        print('Error fetching course:', e)
        return jsonify({'message': 'Internal server error'}), 500


# Đã có hàm create_course ở trên (dòng 63) với đầy đủ validation
# ========== New: Google Drive upload ==========
@instructor_bp.route('/api/upload/video', methods=['POST'])
def upload_video_to_drive():
    """
    Upload a video file to Google Drive using a Service Account.
    Form-Data:
      - file: binary file
      - folder_id (optional): Google Drive folder ID to upload into
    Response: { fileId, viewUrl, downloadUrl }
    Env required: GOOGLE_SERVICE_ACCOUNT_JSON (file path or JSON string)
    Optionally set default folder via GOOGLE_DRIVE_FOLDER_ID
    """
    try:
        print(f"\n{'='*80}")
        print(f"📤 /api/upload/video - Starting upload")
        print(f"{'='*80}")
        
        if 'file' not in request.files:
            print(f"❌ Missing file field in request")
            return jsonify({'message': 'Missing file field'}), 400
        
        f = request.files['file']
        if f.filename == '':
            print(f"❌ Empty filename")
            return jsonify({'message': 'Empty filename'}), 400
        
        print(f"📝 File: {f.filename} (size: {len(f.read())} bytes)")
        f.seek(0)  # Reset stream position
        print(f"📝 MIME type: {f.mimetype}")
        
        # Prefer explicit folder_id from request, else fallback to env
        folder_id = request.form.get('folder_id') or os.getenv('GOOGLE_DRIVE_FOLDER_ID')
        print(f"📁 Target folder ID: {folder_id}")

        from ..utils.google_drive import upload_file_to_drive
        import io

        stream = io.BytesIO(f.read())
        print(f"✅ Reading file into memory... {len(stream.getvalue())} bytes")
        
        print(f"🔄 Uploading to Google Drive...")
        file_id, web_view_link, public_download_url = upload_file_to_drive(
            stream,
            f.filename,
            f.mimetype or 'application/octet-stream',
            folder_id=folder_id
        )
        
        print(f"✅ Upload successful!")
        print(f"   File ID: {file_id}")
        print(f"   View URL: {web_view_link}")
        print(f"   Download URL: {public_download_url}")
        print(f"{'='*80}\n")
        
        return jsonify({
            'fileId': file_id,
            'viewUrl': web_view_link,
            'downloadUrl': public_download_url
        }), 200
    except Exception as e:
        print(f"\n{'='*80}")
        print(f"❌ Error uploading to drive: {e}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        print(f"{'='*80}\n")
        return jsonify({'message': f'Upload failed: {str(e)}'}), 500