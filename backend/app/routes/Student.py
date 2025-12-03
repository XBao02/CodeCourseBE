from flask import Blueprint
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, verify_jwt_in_request
from datetime import datetime
from app.models import db, Course, Enrollment, StudyPlan, PlanItem, Student
from app.models.model import User, LessonProgress, Instructor, Category, Topic
from app.services.recommender import semantic_recommend, recommend_courses  # new import
from app.utils.cloudinary_upload import upload_video  # placeholder import if using cloudinary for images too
import traceback
import os, uuid, time
import json
try:
    import google.generativeai as genai  # type: ignore
except Exception:
    genai = None

_AI_CHAT_SESSIONS = {}  # session_id -> {user_id, history:[{"role":"user"|"assistant","text":...}], created_at}
_GEMINI_MODEL_NAME = os.getenv('GEMINI_RECO_MODEL', 'gemini-2.5-flash')

def _configure_client():
    """Configure Gemini client similar to AIQuiz flow."""
    from dotenv import load_dotenv
    load_dotenv()
    if genai is None:
        return False
    api_key = (
        os.getenv("GEMINI_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
        or os.getenv("GOOGLE_GEMINI_KEY")
    )
    if not api_key:
        return False
    try:
        genai.configure(api_key=api_key)
        return True
    except Exception:
        return False

def _serialize_courses(limit=40):
    # Provide condensed course info for AI context
    rows = Course.query.order_by(Course.created_at.desc()).limit(limit).all()
    payload = []
    for c in rows:
        cats = [cat.name for cat in getattr(c,'categories',[]) if getattr(cat,'name',None)]
        tops = [t.name for t in getattr(c,'topics',[]) if getattr(t,'name',None)]
        payload.append({
            'id': c.id,
            'title': c.title,
            'level': c.level,
            'price': float(c.price) if c.price else 0,
            'categories': cats,
            'topics': tops,
            'description': (c.description or '')[:400]
        })
    return payload

def _build_system_instruction():
    return (
        "You are an adaptive bilingual (English + Vietnamese) course recommendation chatbot.\n"
        "You can answer ANY user question (technical, learning path, pricing) concisely, then optionally suggest relevant courses.\n"
        "You have access to a course dataset. When you decide to recommend, pick 1-6 most relevant courses.\n"
        "For each recommended course give a short reason referencing user goals, level, interests, or previous messages.\n"
        "If user asks general questions (e.g. career advice) you may answer without recommending; recommend only when helpful.\n"
        "Maintain conversation context; ask clarification when goals are unclear.\n"
        "FINAL PART: include a JSON block enclosed in <JSON>...</JSON> with structure: {\n"
        "  \"courses\": [ { \"id\": <number>, \"reason\": \"string\" } ],\n"
        "  \"follow_up_question\": \"string or null\"\n"
        "}\n"
        "If you do NOT wish to recommend in this turn, output an empty array for courses.\n"
        "Keep answers under 180 words outside the JSON. Use Vietnamese if user uses Vietnamese."
    )

def _ai_generate_reply(history, course_context):
    ready = _configure_client()
    if not ready:
        return { 'text': 'AI is unavailable, using fallback heuristic. Provide level, category, topic.', 'courses': [] }
    try:
        # Build a single prompt string (more compatible across API versions)
        sys = _build_system_instruction()
        convo = "\n".join([
            ("User: " + m['text']) if m['role']=='user' else ("Assistant: " + m['text'])
            for m in history
        ])
        dataset = json.dumps(course_context, ensure_ascii=False)
        prompt = (
            f"{sys}\n\n"
            f"Conversation so far:\n{convo}\n\n"
            f"Course dataset (JSON):\n{dataset}\n\n"
            f"Respond to the last user message with advice and optional recommendations."
        )
        model = genai.GenerativeModel(_GEMINI_MODEL_NAME)
        resp = model.generate_content(prompt)
        # Robust text extraction (like AIQuiz)
        text = getattr(resp, 'text', None)
        if not text:
            parts = []
            for cand in getattr(resp, 'candidates', []):
                content = getattr(cand, 'content', None)
                for part in getattr(content, 'parts', []) or []:
                    if hasattr(part, 'text') and part.text:
                        parts.append(part.text)
            text = " ".join(parts)
        text = (text or '').strip()
        # Extract JSON block
        import re
        courses = []
        follow_up = None
        m = re.search(r'<JSON>(.*?)</JSON>', text, re.DOTALL)
        if m:
            raw = m.group(1).strip()
            try:
                parsed = json.loads(raw)
                courses = parsed.get('courses') or []
                follow_up = parsed.get('follow_up_question')
            except Exception:
                pass
        return { 'text': text, 'courses': courses, 'follow_up': follow_up }
    except Exception as e:
        print('Gemini error:', e)
        return { 'text': 'AI error occurred; please provide level, category, topic to continue.', 'courses': [] }

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
    Trả về TẤT CẢ khóa học có trong database, hỗ trợ filter theo level, category, topic qua query params.
    Query params:
      - level: 'beginner' | 'intermediate' | 'advanced'
      - category: category name hoặc slug
      - topic: topic name hoặc slug
    """
    try:
        level = (request.args.get('level') or '').strip().lower()
        category_q = (request.args.get('category') or '').strip().lower()
        topic_q = (request.args.get('topic') or '').strip().lower()

        q = Course.query
        # Filter by level
        if level:
            q = q.filter(db.func.lower(Course.level) == level)
        # Filter by category name/slug
        if category_q:
            q = q.join(Course.categories).filter(
                db.or_(db.func.lower(Category.name) == category_q, db.func.lower(Category.slug) == category_q)
            )
        # Filter by topic name/slug
        if topic_q:
            q = q.join(Course.topics).filter(
                db.or_(db.func.lower(Topic.name) == topic_q, db.func.lower(Topic.slug) == topic_q)
            )
        # Deduplicate if multiple joins
        q = q.distinct()

        courses = q.all()
        data = []
        for c in courses:
            instructor_name = None
            if c.instructor_id:
                try:
                    ins = Instructor.query.get(c.instructor_id)
                    instructor_name = getattr(ins, 'user', None).full_name if getattr(ins, 'user', None) else None
                except Exception:
                    instructor_name = None
            categories = [cat.name for cat in getattr(c, 'categories', []) if getattr(cat, 'name', None)]
            topics = [top.name for top in getattr(c, 'topics', []) if getattr(top, 'name', None)]
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
                'categories': categories,
                'topics': topics,
                'createdAt': c.created_at.isoformat() if c.created_at else None,
                'updatedAt': c.updated_at.isoformat() if c.updated_at else None,
            })
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
                user_id = _resolve_user_id_from_identity(ident)
                if user_id:
                    user = User.query.get(user_id)
                    if user:
                        student = Student.query.filter_by(user_id=user.id).first()
            except Exception:
                student = None
        if student_id and not student:
            student = Student.query.get(student_id)
        if not student:
            return jsonify({'error': 'Unauthorized or student not found'}), 401

        enrollments = Enrollment.query.filter(
            Enrollment.student_id == student.id,
            Enrollment.status == 'active'
        ).all()

        data = []
        for e in enrollments:
            course = Course.query.get(e.course_id)
            if not course:
                continue
            categories = [cat.name for cat in getattr(course, 'categories', []) if getattr(cat, 'name', None)]
            topics = [top.name for top in getattr(course, 'topics', []) if getattr(top, 'name', None)]
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
                'categories': categories,
                'topics': topics,
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
            return jsonify({"success": False, "message": "Missing courseId"}), 400

        course_id = data['courseId']
        print(f"📝 Course ID to register: {course_id}")

        # Verify JWT manually to avoid framework 422 errors
        try:
            verify_jwt_in_request(optional=False)
            print(f"✅ JWT verification passed")
        except Exception as e:
            print(f"❌ JWT verification failed: {e}")
            return jsonify({"success": False, "message": "Unauthorized"}), 401

        ident = get_jwt_identity()
        print(f"🔐 JWT Identity decoded: {ident}")
        
        user_id = _resolve_user_id_from_identity(ident)
        if not user_id:
            print(f"❌ Could not resolve user_id from identity: {ident}")
            return jsonify({"success": False, "message": "Invalid token"}), 401
        
        print(f"👤 Resolved user_id: {user_id}")

        user = User.query.get(user_id)
        if not user:
            print(f"❌ User not found with user_id={user_id}")
            return jsonify({"success": False, "message": "User not found"}), 404
        
        print(f"✅ User found: {user.email}")

        student = Student.query.filter_by(user_id=user.id).first()
        if not student:
            print(f"❌ Student profile not found for user_id={user.id}")
            return jsonify({"success": False, "message": "Student not found"}), 404
        
        print(f"✅ Student found: id={student.id}")

        # Check course existence
        course = Course.query.get(course_id)
        if not course:
            print(f"❌ Course not found with id={course_id}")
            return jsonify({"success": False, "message": "Course not found"}), 404
        
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
            }, 200)

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
        print(f"❌ Traceback: {traceback.format_exc()}")
        print(f"{'='*80}\n")
        db.session.rollback()
        return jsonify({"error": "Server error", "success": False}), 500


# Endpoint tạm để xóa tất cả enrollment (chỉ dùng cho testing)


# ✅ 4. Lấy lộ trình học (StudyPlan & PlanItem)
@student_bp.route('/study-plans/<int:student_id>', methods=['GET'])
def get_study_plans(student_id):
    plans = StudyPlan.query.filter_by(student_id=student_id).all()
    data = []
    for plan in plans:
        items = PlanItem.query.filter_by(plan_id=plan.id).order_by(PlanItem.sort_order.asc()).all()
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
            return jsonify({'error': 'Course not found'}), 404

        # Lấy student từ JWT token (optional)
        student = None
        try:
            verify_jwt_in_request(optional=True)
            ident = get_jwt_identity()
            if ident:
                user_id = _resolve_user_id_from_identity(ident)
                user = User.query.get(user_id) if user_id else None
                student = Student.query.filter_by(user_id=user.id).first() if user else None
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

        # For computing total possible per test
        from app.models.model import Question, TestAttempt

        for section in sections:
            lessons = sorted(list(section.lessons), key=lambda l: (l.sort_order or 0, l.id))
            lesson_payload = []
            for lesson in lessons:
                # Build tests with latest score if student available
                tests_payload = []
                for t in getattr(lesson, 'tests', []):
                    # Sum of question points for this test
                    questions = Question.query.filter_by(test_id=t.id).all()
                    total_possible = sum((q.points or 1) for q in questions) if questions else 0
                    last_score = None
                    if student:
                        last_attempt = (
                            TestAttempt.query
                            .filter_by(student_id=student.id, test_id=t.id)
                            .order_by(TestAttempt.created_at.desc())
                            .first()
                        )
                        if last_attempt and last_attempt.total_score is not None:
                            try:
                                last_score = float(last_attempt.total_score)
                            except Exception:
                                last_score = None
                    tests_payload.append({
                        "id": t.id,
                        "title": t.title,
                        "timeLimitMinutes": t.time_limit_minutes or 0,
                        # extra fields for FE score display
                        "lastScore": last_score,
                        "totalScore": total_possible
                    })

                lesson_payload.append({
                    "id": lesson.id,
                    "sectionId": lesson.section_id,
                    "title": lesson.title,
                    "content": lesson.content,
                    "type": getattr(lesson, 'type', 'video'),
                    "videoUrl": getattr(lesson, 'video_url', None),
                    "durationSeconds": getattr(lesson, 'duration_seconds', 0) or 0,
                    "isPreview": getattr(lesson, 'is_preview', False) or False,
                    "sortOrder": lesson.sort_order,
                    "completed": lesson.id in lesson_id_to_completed,
                    "tests": tests_payload
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
            return jsonify({'success': False, 'message': 'Missing lessonId'}), 400

        # Lấy student từ JWT token
        student = None
        try:
            verify_jwt_in_request(optional=False)
            ident = get_jwt_identity()
            user_id = _resolve_user_id_from_identity(ident)
            user = User.query.get(user_id) if user_id else None
            student = Student.query.filter_by(user_id=user.id).first() if user else None
        except Exception as e:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
        if not student:
            return jsonify({'success': False, 'message': 'Student not found'}), 404

        from app.models.model import LessonProgress, Lesson

        lesson = Lesson.query.get(lesson_id)
        if not lesson:
            return jsonify({'success': False, 'message': 'Lesson not found'}), 404

        # Tạo/cập nhật tiến độ
        lp = LessonProgress.query.filter_by(student_id=student.id, lesson_id=lesson_id).first()
        now = datetime.utcnow()
        if not lp:
            lp = LessonProgress(student_id=student.id, lesson_id=lesson_id, updated_at=now, status='completed')
            db.session.add(lp)
        else:
            lp.updated_at = now
            lp.status = 'completed'

        # Bỏ qua cập nhật Enrollment/progress để tránh lỗi; có thể thêm lại sau khi ổn định

        db.session.commit()
        return jsonify({'success': True}), 200
    except Exception as e:
        print("Lỗi complete_lesson:", e)
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Server error'}), 500


# ==================== TEST TAKING ENDPOINTS ====================

# Get test details with questions for student
@student_bp.route('/tests/<int:test_id>', methods=['GET'])
@jwt_required()
def get_test_for_student(test_id):
    """
    Lấy thông tin test và câu hỏi để student làm bài
    Không trả về đáp án đúng
    """
    try:
        print(f"\n{'='*80}")
        print(f"📥 GET /api/student/tests/{test_id}")
        print(f"{'='*80}")
        
        from app.models.model import Test, Question, Choice
        
        # Verify student authentication
        ident = get_jwt_identity()
        print(f"🔐 JWT Identity: {ident}")
        user_id = _resolve_user_id_from_identity(ident)
        if not user_id:
            return jsonify({'message': 'Invalid token'}), 401
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        student = Student.query.filter_by(user_id=user.id).first()
        if not student:
            return jsonify({'message': 'Student not found'}), 404
        
        print(f"✅ Student verified: id={student.id}")
        
        # Get test
        test = Test.query.get(test_id)
        if not test:
            return jsonify({'message': 'Test not found'}), 404
        
        print(f"✅ Test found: {getattr(test, 'title', '')}")
        
        # Get questions with choices
        questions = Question.query.filter_by(test_id=test_id).order_by(Question.id).all()
        print(f"📝 Found {len(questions)} questions")
        
        questions_data = []
        for q in questions:
            choices = Choice.query.filter_by(question_id=q.id).order_by(Choice.id).all()
            questions_data.append({
                'id': q.id,
                'content': q.content,
                'points': getattr(q, 'points', 1) or 1,
                'difficulty': getattr(q, 'difficulty', 'medium') or 'medium',
                'choices': [
                    {
                        'id': c.id,
                        'text': getattr(c, 'text', None) or getattr(c, 'content', None),
                        'content': getattr(c, 'text', None) or getattr(c, 'content', None),
                        # do NOT return correctness for taking test
                    }
                    for c in choices
                ]
            })
        
        result = {
            'id': test.id,
            'title': getattr(test, 'title', '') or '',
            'timeLimitMinutes': getattr(test, 'time_limit_minutes', 0) or 0,
            'attemptsAllowed': getattr(test, 'attempts_allowed', 1) or 1,
            'questions': questions_data
        }
        
        print(f"✅ Returning test data successfully")
        print(f"{'='*80}\n")
        return jsonify(result), 200
        
    except Exception as e:
        print(f"❌ Error getting test for student: {e}")
        print(f"❌ Traceback: {traceback.format_exc()}")
        print(f"{'='*80}\n")
        return jsonify({'message': 'Server error'}), 500


# Submit test and get results
@student_bp.route('/tests/<int:test_id>/submit', methods=['POST'])
@jwt_required()
def submit_test(test_id):
    """
    Student nộp bài test và nhận kết quả ngay lập tức
    """
    try:
        print(f"\n{'='*80}")
        print(f"📥 POST /api/student/tests/{test_id}/submit")
        print(f"{'='*80}")
        
        from app.models.model import Test, Question, Choice, TestAttempt
        
        # Get student from JWT
        ident = get_jwt_identity()
        print(f"🔐 JWT Identity: {ident}")
        
        user_id = _resolve_user_id_from_identity(ident)
        if not user_id:
            return jsonify({'message': 'Invalid token'}), 401
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        student = Student.query.filter_by(user_id=user.id).first()
        if not student:
            return jsonify({'message': 'Student not found'}), 404
        
        print(f"✅ Student verified: id={student.id}")
        
        # Get test
        test = Test.query.get(test_id)
        if not test:
            return jsonify({'message': 'Test not found'}), 404
        
        print(f"✅ Test found: {getattr(test, 'title', '')}")
        
        # Get submitted answers
        data = request.get_json() or {}
        answers = data.get('answers', [])  # [{ questionId, choiceId }, ...]
        print(f"📝 Received {len(answers)} answers")
        answers_by_qid = {a.get('questionId'): a.get('choiceId') for a in answers}
        
        # Calculate score
        score = 0
        total_score = 0
        correct_count = 0
        
        questions = Question.query.filter_by(test_id=test_id).all()
        print(f"📊 Processing {len(questions)} questions")
        
        for question in questions:
            q_points = getattr(question, 'points', 1) or 1
            total_score += q_points
            chosen_id = answers_by_qid.get(question.id)
            if chosen_id is None:
                continue
            # check correctness
            correct_choice = Choice.query.filter_by(question_id=question.id, is_correct=True).first()
            if correct_choice and correct_choice.id == chosen_id:
                score += q_points
                correct_count += 1
        
        # Calculate percentage
        percentage = (score / total_score * 100) if total_score > 0 else 0
        passed = percentage >= 60  # 60% to pass
        
        print(f"📊 Final Score: {score}/{total_score} ({percentage:.2f}%)")
        print(f"📊 Status: {'PASSED ✅' if passed else 'FAILED ❌'}")
        
        # Save test attempt to database (map to existing columns)
        try:
            attempt_number = 1
            # determine next attempt number for this student/test
            prev_attempt = (
                TestAttempt.query
                .filter_by(student_id=student.id, test_id=test.id)
                .order_by(TestAttempt.attempt_number.desc())
                .first()
            )
            if prev_attempt and isinstance(prev_attempt.attempt_number, int):
                attempt_number = prev_attempt.attempt_number + 1

            now_dt = datetime.utcnow()
            attempt = TestAttempt(
                student_id=student.id,
                test_id=test.id,
                attempt_number=attempt_number,
                start_time=now_dt,
                submit_time=now_dt,
                total_score=score,
            )
            db.session.add(attempt)
            db.session.commit()
        except Exception as e:
            print(f"⚠️ Could not save TestAttempt: {e}")
            db.session.rollback()
        
        result = {
            "success": True,
            "score": score,
            "totalScore": total_score,
            "total_score": total_score,
            "correctCount": correct_count,
            "correct_count": correct_count,
            "percentage": round(percentage, 2),
            "passed": passed
        }
        
        print(f"✅ Returning test results successfully")
        print(f"{'='*80}\n")
        return jsonify(result), 200
        
    except Exception as e:
        print(f"❌ Error submitting test: {e}")
        print(f"❌ Traceback: {traceback.format_exc()}")
        print(f"{'='*80}\n")
        db.session.rollback()
        return jsonify({'message': 'Server error', 'success': False}), 500


# ==================== TEST METRICS (for dashboard) ====================
@student_bp.route('/test-metrics', methods=['GET'])
@jwt_required()
def get_test_metrics():
    """Return basic test statistics for the current student.
    - testsTaken: number of attempts
    - averagePercentage: average of (attempt score / test total points) * 100
    """
    try:
        from app.models.model import TestAttempt, Test, Question

        ident = get_jwt_identity()
        user_id = _resolve_user_id_from_identity(ident)
        if not user_id:
            return jsonify({'message': 'Invalid token'}), 401

        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404

        student = Student.query.filter_by(user_id=user.id).first()
        if not student:
            return jsonify({'message': 'Student not found'}), 404

        attempts = TestAttempt.query.filter_by(student_id=student.id).all()
        tests_taken = len(attempts)
        if tests_taken == 0:
            return jsonify({
                'testsTaken': 0,
                'averagePercentage': 0.0
            }), 200

        # Pre-compute total points per test id
        test_ids = {a.test_id for a in attempts}
        totals_by_test = {}
        for t_id in test_ids:
            qs = Question.query.filter_by(test_id=t_id).all()
            totals_by_test[t_id] = sum((q.points or 1) for q in qs) if qs else 0

        percentages = []
        for a in attempts:
            total_possible = totals_by_test.get(a.test_id, 0) or 0
            try:
                raw = float(a.total_score) if a.total_score is not None else 0.0
            except Exception:
                raw = 0.0
            pct = (raw / total_possible * 100.0) if total_possible > 0 else 0.0
            percentages.append(pct)

        avg_pct = sum(percentages) / len(percentages) if percentages else 0.0
        return jsonify({
            'testsTaken': tests_taken,
            'averagePercentage': round(avg_pct, 2)
        }), 200
    except Exception as e:
        print('❌ Error computing test metrics:', e)
        print(f"❌ Traceback: {traceback.format_exc()}")
        return jsonify({'message': 'Server error'}), 500


@student_bp.route('/recommend/start', methods=['POST'])
def start_recommend():
    """Start a recommendation session; returns first question."""
    return jsonify({'success': True, 'message': 'Chat session deprecated. Use /api/student/recommend/chat/init'}), 410

@student_bp.route('/recommend/step', methods=['POST'])
def recommend_step():
    """Handle step answers and progress to next question or final recommendation."""
    return jsonify({'success': False, 'error': 'Deprecated endpoint. Use chat API.'}), 410

@student_bp.route('/recommend/semantic', methods=['POST'])
def recommend_semantic():
    data = request.get_json() or {}
    query = (data.get('query') or '').strip()
    if not query:
        return jsonify({'success': False, 'error': 'Missing query'}), 400
    recs = semantic_recommend(query=query, limit=int(data.get('limit') or 6))
    return jsonify({'success': True, 'recommendations': recs}), 200

@student_bp.route('/recommend/more', methods=['POST'])
def recommend_more():
    return jsonify({'success': False, 'error': 'Deprecated. Use chat message endpoint for refinements.'}), 410


def _produce_recommendations(answers):
    from app.services.recommender import recommend_courses
    level = answers.get('level')
    major = answers.get('major')
    topic = answers.get('topic')
    recs = recommend_courses(level=level, major=major, topic=topic, limit=6)
    return jsonify({'success': True, 'completed': True, 'answers': answers, 'recommendations': recs}), 200


@student_bp.post('/recommend/chat/init')
@jwt_required(optional=True)
def recommend_chat_init():
    ident = get_jwt_identity()
    user_id = _resolve_user_id_from_identity(ident) if ident else None
    session_id = str(uuid.uuid4())
    _AI_CHAT_SESSIONS[session_id] = { 'user_id': user_id, 'history': [], 'created_at': time.time() }
    intro = 'Xin chào! Bạn muốn học gì? Hãy cho tôi biết mục tiêu (ví dụ: học backend Python, cải thiện thuật toán, chuẩn bị phỏng vấn...).'
    return jsonify({ 'success': True, 'sessionId': session_id, 'message': intro }) , 200

@student_bp.post('/recommend/chat/message')
@jwt_required(optional=True)
def recommend_chat_message():
    data = request.get_json() or {}
    session_id = data.get('sessionId')
    user_msg = (data.get('message') or '').strip()
    if not session_id or session_id not in _AI_CHAT_SESSIONS:
        return jsonify({ 'success': False, 'error': 'Invalid session' }), 400
    if not user_msg:
        return jsonify({ 'success': False, 'error': 'Empty message' }), 400
    sess = _AI_CHAT_SESSIONS[session_id]
    sess['history'].append({'role':'user','text': user_msg})
    course_context = _serialize_courses()
    ai = _ai_generate_reply(sess['history'], course_context)
    # If AI included course IDs with reasons, map to full course objects
    detailed = []
    for item in ai.get('courses', [])[:8]:
        cid = item.get('id')
        if not cid:
            continue
        c = Course.query.get(int(cid))
        if not c:
            continue
        detailed.append({
            'course': {
                'id': c.id,
                'title': c.title,
                'level': c.level,
                'price': float(c.price) if c.price else 0,
                'categories': [cat.name for cat in getattr(c,'categories',[]) if getattr(cat,'name',None)],
                'topics': [t.name for t in getattr(c,'topics',[]) if getattr(t,'name',None)],
                'description': c.description
            },
            'reason': item.get('reason')
        })
    # Append assistant message (store trimmed text to avoid growth)
    assistant_text = ai.get('text','')[:6000]
    sess['history'].append({'role':'assistant','text': assistant_text})
    return jsonify({
        'success': True,
        'sessionId': session_id,
        'reply': assistant_text,
        'coursesWithReasons': detailed,
        'followUp': ai.get('follow_up')
    }), 200


# --- Profile endpoints ---
from sqlalchemy import text as _sa_text

# Reuse existing blueprint if already declared above in this module
try:
    student_bp  # type: ignore[name-defined]
except NameError:  # pragma: no cover
    from flask import Blueprint as _Blueprint
    student_bp = _Blueprint('student', __name__, url_prefix='/api/student')


def _get_current_user():
    try:
        uid = int(get_jwt_identity())
    except Exception:
        uid = None
    if not uid:
        return None
    return db.session.get(User, uid)


def _get_student_for_user(user: User):
    if not user:
        return None
    # Prefer ORM; fall back to raw query if mapping is used in schema
    try:
        user_id = getattr(user, 'Id', None) or getattr(user, 'id', None)
        return db.session.query(Student).filter_by(UserId=user_id).first()
    except Exception:
        m = db.session.execute(_sa_text('SELECT * FROM Students WHERE UserId=:uid'), {'uid': user_id}).mappings().first()
        return m


def _pick(*names, src=None, default=None):
    for n in names:
        try:
            if isinstance(src, dict) and n in src:
                return src[n]
            v = getattr(src, n)
            return v
        except Exception:
            continue
    return default


def _serialize_student(st, user: User):
    return {
        'id': _pick('Id', 'id', src=st),
        'name': _pick('FullName', 'name', src=user) or _pick('Name', 'name', src=st),
        'email': _pick('Email', 'email', src=user) or _pick('Email', 'email', src=st),
        'phone': _pick('Phone', 'phone', src=user) or _pick('Phone', 'phone', src=st),
        'photo': _pick('AvatarUrl', 'avatar_url', 'photo', src=user) or _pick('AvatarUrl', 'avatar_url', 'photo', src=st),
        'dob': _pick('Dob', 'DOB', 'DateOfBirth', 'BirthDate', 'dob', src=user) or _pick('Dob', 'DOB', 'DateOfBirth', 'BirthDate', 'dob', src=st),
        'address': _pick('Address', 'address', src=user) or _pick('Address', 'address', src=st),
        'createdAt': _pick('CreatedAt', 'created_at', src=user) or _pick('CreatedAt', 'created_at', src=st),
        'updatedAt': _pick('UpdatedAt', 'updated_at', src=user) or _pick('UpdatedAt', 'updated_at', src=st),
        'courses': [],  # can be populated later
    }


@student_bp.get('/profile')
@jwt_required()
def get_profile():
    user = _get_current_user()
    if not user:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    st = _get_student_for_user(user)
    if not st:
        return jsonify({'success': False, 'error': 'Student not found'}), 404
    return jsonify({'success': True, 'student': _serialize_student(st, user)})


@student_bp.put('/profile')
@jwt_required()
def update_profile():
    user = _get_current_user()
    if not user:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    data = request.get_json(silent=True) or {}
    name = data.get('name') or data.get('fullName')
    phone = data.get('phone')
    email = data.get('email')
    dob = data.get('dob') or data.get('dateOfBirth')
    address = data.get('address')
    photo = data.get('photo')
    try:
        # --- Update User ---
        if name is not None:
            if hasattr(user, 'FullName'): user.FullName = name
            elif hasattr(user, 'name'): user.name = name
        if phone is not None and hasattr(user, 'Phone'): user.Phone = phone
        if email is not None:
            if hasattr(user, 'Email'): user.Email = email
            elif hasattr(user, 'email'): user.email = email
        if dob is not None:
            for attr in ['Dob','DOB','DateOfBirth','BirthDate','dob']:
                if hasattr(user, attr): setattr(user, attr, dob); break
        if address is not None:
            for attr in ['Address','address']:
                if hasattr(user, attr): setattr(user, attr, address); break
        if photo is not None:
            for attr in ['AvatarUrl','avatar_url','photo']:
                if hasattr(user, attr): setattr(user, attr, photo); break
        if hasattr(user, 'UpdatedAt'):
            user.UpdatedAt = datetime.utcnow()

        # --- Update Student row as well ---
        st = _get_student_for_user(user)
        if st is not None and not isinstance(st, dict):
            if name is not None:
                for attr in ['FullName','Name','name']:
                    if hasattr(st, attr): setattr(st, attr, name); break
            if phone is not None:
                for attr in ['Phone','phone']:
                    if hasattr(st, attr): setattr(st, attr, phone); break
            if dob is not None:
                for attr in ['Dob','DOB','DateOfBirth','BirthDate','dob']:
                    if hasattr(st, attr): setattr(st, attr, dob); break
            if address is not None:
                for attr in ['Address','address']:
                    if hasattr(st, attr): setattr(st, attr, address); break
            if photo is not None:
                for attr in ['AvatarUrl','avatar_url','photo']:
                    if hasattr(st, attr): setattr(st, attr, photo); break
            if hasattr(st, 'UpdatedAt'):
                st.UpdatedAt = datetime.utcnow()

        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@student_bp.post('/profile/avatar')
@jwt_required()
def upload_avatar():
    user = _get_current_user()
    if not user:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'Missing file'}), 400
    f = request.files['file']
    try:
        # Prefer Cloudinary if available
        try:
            from app.utils.cloudinary_upload import cloudinary, DEFAULT_FOLDER
            result = cloudinary.uploader.upload(
                f,
                folder=DEFAULT_FOLDER,
                overwrite=True,
                resource_type='image',
            )
            url = result.get('secure_url') or result.get('url')
        except Exception:
            url = None
        if not url:
            # Fallback: return a data URL preview (not persisted server-side)
            return jsonify({'success': True, 'url': ''})
        for attr in ['AvatarUrl','avatar_url','photo']:
            if hasattr(user, attr): setattr(user, attr, url); break
        db.session.commit()
        return jsonify({'success': True, 'url': url})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

