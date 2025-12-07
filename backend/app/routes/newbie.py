"""Newbie onboarding endpoints."""

import json
from uuid import uuid4

import random
from collections import Counter
from datetime import datetime, timedelta

from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash

from app.models import db
from sqlalchemy import desc

from app.models.model import (
    User,
    Course,
    CourseSection,
    Lesson,
    PlacementTestResult,
    LearningPath,
    LearningPathItem,
    NewbieProfile,
    NewbieQuizHistory,
)

newbie_bp = Blueprint("newbie", __name__, url_prefix="/api/newbie")

TEST_SESSIONS = {}
SESSION_TTL = timedelta(minutes=30)

LEVEL_BRACKETS = [
    (2, "absolute_beginner"),
    (4, "beginner"),
    (7, "medium_beginner"),
    (10, "low_intermediate"),
]

LEVEL_TO_COURSE_LEVEL = {
    "absolute_beginner": "beginner",
    "beginner": "beginner",
    "medium_beginner": "beginner",
    "low_intermediate": "intermediate",
}

LEGACY_TEST_QUESTIONS = [
    {
        "id": 1,
        "question": "HTML stands for?",
        "options": ["Hyper Text", "Home Tool", "Hyperlink"],
        "correct_index": 0,
    },
    {
        "id": 2,
        "question": "CSS is used for?",
        "options": ["Structure", "Styling", "Storage"],
        "correct_index": 1,
    },
    {
        "id": 3,
        "question": "Python is a?",
        "options": ["Programming language", "Database", "Markup"],
        "correct_index": 0,
    },
    {
        "id": 4,
        "question": "Flask is a?",
        "options": ["Backend framework", "Frontend tool", "Database"],
        "correct_index": 0,
    },
    {
        "id": 5,
        "question": "React components are written in?",
        "options": ["Python", "JavaScript", "SQL"],
        "correct_index": 1,
    },
]

TRACK_RESPONSIBILITIES = {
    "frontend": "Crafting user interfaces with HTML/CSS/JavaScript",
    "backend": "Designing APIs, business logic, and data storage",
    "fullstack": "Building end-to-end experiences from UI to servers",
}

TRACK_TOOL_MAP = {
    "frontend": "HTML, CSS, JavaScript bundle",
    "backend": "REST APIs, databases and Python/Node",
    "fullstack": "End-to-end app wiring with cloud services",
}

OTHER_TRACKS = ["design", "data", "devops"]


def _normalize_track(value):
    if not value:
        return "backend"
    value = value.lower()
    if "front" in value:
        return "frontend"
    if "full" in value:
        return "fullstack"
    if "back" in value:
        return "backend"
    return "backend"


def _infer_course_track(course):
    slug = getattr(course, "slug", "") or ""
    return _normalize_track(slug)


def _preferred_course_level(level):
    return LEVEL_TO_COURSE_LEVEL.get(level, "beginner")


def _serialize_course(course):
    return {
        "course_id": course.id,
        "title": course.title,
        "description": course.description,
        "level": course.level,
        "track": _infer_course_track(course),
    }


def _shuffle_options(correct, distractors):
    pool = [correct, *distractors]
    random.shuffle(pool)
    return pool, pool.index(correct)


_track_variations = [
    "Which task would you assign to a {track} developer working with {topic}?",
    "When focusing on {track}, which activity supports {topic} the most?",
    "Choose the action that clearly fits into {track} learning on {topic}.",
]


def _build_track_question(track, course, difficulty, focus_topic):
    track_label = track.title() if track else "Engineering"
    topic_label = focus_topic or track_label
    prompt = random.choice(_track_variations).format(track=track_label, topic=topic_label)
    correct = TRACK_RESPONSIBILITIES.get(track, f"Giải các bài toán trong {track_label}")
    distractors = [
        "Thiết kế phần cứng vật lý",
        "Quản lý nhân sự và báo cáo hành chính",
        "Tạo nội dung marketing",
    ]
    options, idx = _shuffle_options(correct, random.sample(distractors, k=2))
    return {
        "question": prompt,
        "options": options,
        "correct_index": idx,
        "topic": focus_topic or "track",
        "difficulty": difficulty,
    }


_level_variations = [
    "Điểm mạnh nào sau đây miêu tả đúng trình độ {topic} học viên đang cần?",
    "Chọn mức độ phù hợp với người mới học {track}.",
    "Đâu là level nên tập trung để học {topic} hiệu quả?",
]


def _build_level_question(track, course, difficulty, focus_topic):
    topic_label = focus_topic or (track.title() if track else "môn học")
    prompt = random.choice(_level_variations).format(track=track.title() if track else "công nghệ", topic=topic_label)
    correct = (course.level.title() if course else "Beginner")
    others = [lvl for lvl in ["Beginner", "Intermediate", "Advanced"] if lvl != correct]
    options, idx = _shuffle_options(correct, random.sample(others, k=2))
    return {
        "question": prompt,
        "options": options,
        "correct_index": idx,
        "topic": "level",
        "difficulty": difficulty,
    }


_tool_variations = [
    "Những công cụ nào giúp ích nhất khi làm {track} với {topic}?",
    "Chọn bộ tool phù hợp để làm việc với {topic} trong {track}.",
]


def _build_tool_question(track, course, difficulty, focus_topic):
    track_label = track.title() if track else "công nghệ"
    topic_label = focus_topic or track_label
    prompt = random.choice(_tool_variations).format(track=track_label, topic=topic_label)
    correct = TRACK_TOOL_MAP.get(track, "Software tooling and automation")
    distractors = [
        "Các công cụ tạo mô hình 3D",
        "Phần mềm biên tập video",
        "Công cụ marketing và CRM",
    ]
    options, idx = _shuffle_options(correct, random.sample(distractors, k=2))
    return {
        "question": prompt,
        "options": options,
        "correct_index": idx,
        "topic": "tools",
        "difficulty": difficulty,
    }


_deliverable_variations = [
    "Chọn deliverable đúng với cách bạn tạo sản phẩm {track}.",
    "Trong {topic}, mục tiêu nào mô tả sản phẩm cuối cùng?",
]


def _build_deliverable_question(track, course, difficulty, focus_topic):
    track_label = track.title() if track else "hệ thống"
    topic_label = focus_topic or track_label
    prompt = random.choice(_deliverable_variations).format(track=track_label, topic=topic_label)
    deliverable = f"{track_label} interface"
    distractors = ["Database schema", "Manufacturing blueprint", "Marketing campaign"]
    options, idx = _shuffle_options(deliverable, random.sample(distractors, k=2))
    return {
        "question": prompt,
        "options": options,
        "correct_index": idx,
        "topic": "deliverable",
        "difficulty": difficulty,
    }


_context_variations = [
    "Khái niệm nào mô tả tốt nhất phần lý thuyết {topic}?",
    "Đâu là từ khóa phù hợp để gắn với {track}?"
]


def _build_context_question(track, course, difficulty, focus_topic):
    track_label = track.title() if track else "kiến thức chuyên môn"
    topic_label = focus_topic or track_label
    prompt = random.choice(_context_variations).format(track=track_label, topic=topic_label)
    trait = f"{topic_label} Domain"
    distractors = ["Customer service scripts", "Human resource policies", "Financial planning"]
    options, idx = _shuffle_options(trait, random.sample(distractors, k=2))
    return {
        "question": prompt,
        "options": options,
        "correct_index": idx,
        "topic": "context",
        "difficulty": difficulty,
    }


def _generate_ai_questions(track, course, difficulty, focus_topic):
    builders = [
        _build_track_question,
        _build_level_question,
        _build_tool_question,
        _build_deliverable_question,
        _build_context_question,
    ]
    questions = []
    for idx in range(10):
        builder = random.choice(builders)
        question = builder(track, course, difficulty, focus_topic)
        question["id"] = idx + 1
        questions.append(question)
    return questions


def _cleanup_sessions():
    threshold = datetime.utcnow() - SESSION_TTL
    stale_keys = [
        key for key, info in TEST_SESSIONS.items() if info.get("created_at") < threshold
    ]
    for key in stale_keys:
        TEST_SESSIONS.pop(key, None)


def _get_history_stats(user_id, limit=5):
    if not user_id:
        return {}
    history = (
        NewbieQuizHistory.query.filter_by(user_id=user_id)
        .order_by(desc(NewbieQuizHistory.created_at))
        .limit(limit)
        .all()
    )
    if not history:
        return {}
    avg_score = sum(entry.score for entry in history) / len(history)
    difficulty = history[0].difficulty or "beginner"
    topic_counter = Counter()
    for entry in history:
        if entry.topics:
            for topic, count in (entry.topics or {}).items():
                topic_counter[topic] += count or 1
    top_topic = topic_counter.most_common(1)
    return {
        "avg_score": avg_score,
        "difficulty": difficulty,
        "top_topic": top_topic[0][0] if top_topic else None,
    }


def _determine_difficulty_label(avg_score):
    if not avg_score:
        return "beginner"
    if avg_score >= 4.5:
        return "advanced"
    if avg_score >= 3.0:
        return "intermediate"
    return "beginner"


def _difficulty_prompt(level):
    mapping = {
        "absolute_beginner": ("nhẹ nhàng", "tập trung vào tư duy cơ bản"),
        "beginner": ("có hướng", "xây dựng nền hiểu biết"),
        "intermediate": ("nâng cao", "phát triển dự án"),
        "advanced": ("tập trung chuyên sâu", "giải bài toán thực tế"),
    }
    return mapping.get(level, ("thực hành đều", "củng cố kỹ năng"))


def _describe_lessons(selected):
    return "\n".join(f"• Bài học #{lesson_id}" for lesson_id in selected)


_description_phrases = {
    "track": [
        "Khám phá các patterns và kiến trúc nền mới.",
        "Ôn tập lại những lý thuyết cốt lõi từng học trước.",
        "Rèn luyện tư duy hệ thống và giải quyết vấn đề.",
    ],
    "advanced": [
        "Chuyển sang các thử thách phân tích hệ thống và tối ưu hiệu năng.",
        "Thực hành debugging và case study thực tế.",
    ],
    "beginner": [
        "Tập trung vào cú pháp và flow cơ bản của chương trình.",
        "Thực hành với ví dụ minh họa và câu hỏi trắc nghiệm.",
    ],
}


_mini_project_phrases = [
    "Thiết kế một API nhỏ để chia sẻ dữ liệu học tập mỗi ngày.",
    "Xây dựng công cụ ghi chú tự động dựa vào topic đã học.",
    "Tạo thử nghiệm mini liên quan đến chủ đề bài học và chia sẻ kết quả.",
    "Viết script tự động hóa một tác vụ đơn giản trong track.",
]


_note_phrases = [
    "Thường xuyên quay lại các ghi chú và viết code mỗi ngày.",
    "Giữ nhịp học đều đặn, mỗi ngày thêm một dòng code mới.",
    "Ôn lại khi nào thấy kiến thức chưa vững, tạo flashcards nếu cần.",
]


def _week_text(track, level, week, difficulty_label):
    vibe, focus = _difficulty_prompt(level)
    track_title = track.title() if track else "phần mềm"
    title = f"Tuần {week}: {focus}" if week > 0 else "Tuần nền tảng"
    desc_options = _description_phrases["track"] + _description_phrases.get(difficulty_label, [])
    description = f"Học {vibe} về {track_title}. {random.choice(desc_options)}"
    if difficulty_label == "advanced":
        description = f"Thực hành sâu về {track_title} với các thách thức thực tế. {random.choice(desc_options)}"
    mini_project = _mini_project_phrases[week % len(_mini_project_phrases)]
    if week == 0:
        mini_project = f"Cài đặt môi trường và chạy Hello World trong {track_title}"
    note = _note_phrases[week % len(_note_phrases)]
    return title, description, mini_project, note


def call_ai_learning_path(user, profile, placement_result, courses, lesson_map, all_lessons):
    level = (placement_result.level if placement_result else "absolute_beginner").lower()
    preferred_track = _normalize_track(profile.goal if profile else None)
    filtered = [c for c in courses if _infer_course_track(c) == preferred_track]
    filtered = filtered or courses
    target_level = _preferred_course_level(level)
    candidate = next((c for c in filtered if c.level == target_level), None)
    if not candidate:
        candidate = next((c for c in filtered if c.level == "beginner"), filtered[0])

    lesson_pool = lesson_map.get(candidate.id, [])
    fallback_ids = all_lessons or [0]
    if not lesson_pool:
        lesson_pool = fallback_ids

    max_weeks = max(6, min(10, ((placement_result.raw_score if placement_result else 3) + 3)))
    weeks = []
    for week in range(1, max_weeks + 1):
        if lesson_pool:
            start = ((week - 1) * 2) % len(lesson_pool)
            selected = lesson_pool[start : start + 2] or lesson_pool[:2]
        else:
            selected = fallback_ids[:2]
        title, description, mini_project, note = _week_text(
            preferred_track, level, week, level
        )
        weeks.append(
            {
                "week": week,
                "title": title,
                "description": f"{description}\n{_describe_lessons(selected)}",
                "recommended_lesson_ids": selected,
                "mini_project": mini_project,
                "note": note,
            }
        )

    if level == "absolute_beginner":
        title, description, mini_project, note = _week_text(
            preferred_track, level, 0, level
        )
        weeks.insert(
            0,
            {
                "week": 0,
                "title": title,
                "description": f"{description}\n{_describe_lessons(lesson_pool[:1] or fallback_ids[:1])}",
                "recommended_lesson_ids": lesson_pool[:1] or fallback_ids[:1],
                "mini_project": mini_project,
                "note": note,
            },
        )

    return {
        "recommended_course": _serialize_course(candidate),
        "personalized_learning_path": {"weeks": weeks},
    }


def _get_or_create_user(email, name):
    email = email.strip().lower()
    user = User.query.filter(db.func.lower(User.email) == email).first()
    if user:
        user.full_name = name.strip()
        return user
    user = User(
        email=email,
        full_name=name.strip(),
        password_hash=generate_password_hash(str(uuid4())),
        role="student",
        is_active=True,
    )
    db.session.add(user)
    db.session.flush()
    return user


@newbie_bp.post("/setup-profile")
def setup_profile():
    data = request.get_json() or {}
    required = ["name", "email", "goal", "study_time_per_day"]
    missing = [field for field in required if not data.get(field)]
    if missing:
        return jsonify({"error": f"Thiếu trường: {', '.join(missing)}"}), 400

    user = _get_or_create_user(data["email"], data["name"])
    study_time = 0
    try:
        study_time = int(data["study_time_per_day"])
    except (TypeError, ValueError):
        study_time = 0

    profile = NewbieProfile.query.filter_by(user_id=user.id).first()
    if not profile:
        profile = NewbieProfile(user_id=user.id, goal=data["goal"].strip(), study_time_per_day=study_time)
        db.session.add(profile)
    else:
        profile.goal = data["goal"].strip()
        profile.study_time_per_day = study_time

    db.session.commit()
    return jsonify(
        {
            "id": user.id,
            "name": user.full_name,
            "email": user.email,
            "goal": profile.goal,
            "study_time_per_day": profile.study_time_per_day,
        }
    )


@newbie_bp.get("/test-questions")
def test_questions():
    user_id = request.args.get("user_id", type=int)
    goal = request.args.get("goal")
    profile = None
    if user_id:
        profile = NewbieProfile.query.filter_by(user_id=user_id).first()
        goal = profile.goal if profile and profile.goal else goal

    history_stats = _get_history_stats(user_id)
    base_track = _normalize_track(goal)
    track = base_track
    difficulty_label = history_stats.get("difficulty") or _determine_difficulty_label(
        history_stats.get("avg_score")
    )
    focus_topic = history_stats.get("top_topic") or track

    courses = Course.query.all()
    course_context = random.choice(courses) if courses else None
    questions = _generate_ai_questions(track, course_context, difficulty_label, focus_topic)

    test_id = str(uuid4())
    _cleanup_sessions()
    session_answers = {}
    session_meta = {}
    payload_questions = []
    question_ids = []
    for question in questions:
        qid = f"{test_id}-{question['id']}"
        session_answers[qid] = question["correct_index"]
        session_meta[qid] = {
            "topic": question.get("topic"),
            "difficulty": question.get("difficulty"),
        }
        question_ids.append(qid)
        payload_questions.append(
            {"id": qid, "question": question["question"], "options": question["options"]}
        )

    TEST_SESSIONS[test_id] = {
        "answers": session_answers,
        "metadata": session_meta,
        "track": track,
        "difficulty": difficulty_label,
        "focus_topic": focus_topic,
        "created_at": datetime.utcnow(),
        "question_ids": question_ids,
    }
    return jsonify({"test_id": test_id, "questions": payload_questions})


@newbie_bp.post("/submit-test")
def submit_test():
    data = request.get_json() or {}
    test_id = data.get("test_id")
    answers = {item["question_id"]: item["chosen_index"] for item in data.get("answers", [])}
    session = None
    answer_key = None
    session_meta = {}
    track = None
    difficulty = None
    question_id_list = []
    if test_id:
        session = TEST_SESSIONS.pop(test_id, None)
        if not session:
            return jsonify({"error": "Phiên bài test không hợp lệ."}), 400
        answer_key = session["answers"]
        session_meta = session.get("metadata", {})
        track = session.get("track")
        difficulty = session.get("difficulty")
        question_id_list = session.get("question_ids", [])
    else:
        answer_key = {q["id"]: q["correct_index"] for q in LEGACY_TEST_QUESTIONS}

    correct = sum(1 for question_id, correct_index in answer_key.items() if answers.get(question_id) == correct_index)
    level = next(lvl for score, lvl in LEVEL_BRACKETS if correct <= score)
    result = PlacementTestResult(user_id=data["user_id"], raw_score=correct, level=level)
    db.session.add(result)
    topic_counts = Counter()
    for meta in session_meta.values():
        topic = meta.get("topic")
        if topic:
            topic_counts[topic] += 1
    if not track:
        profile = NewbieProfile.query.filter_by(user_id=data["user_id"]).first()
        track = _normalize_track(profile.goal if profile else None)
    history_entry = NewbieQuizHistory(
        user_id=data["user_id"],
        track=track,
        difficulty=difficulty or level,
        score=correct,
        question_count=len(answer_key),
        topics={k: v for k, v in topic_counts.items()} if topic_counts else None,
        question_ids=question_id_list or None,
    )
    db.session.add(history_entry)
    db.session.commit()
    return jsonify({"user_id": data["user_id"], "raw_score": correct, "level": level})


@newbie_bp.post("/ai-recommend")
def ai_recommend():
    payload = request.get_json() or {}
    user = User.query.get_or_404(payload.get("user_id"))
    profile = NewbieProfile.query.filter_by(user_id=user.id).first()
    placement = (
        PlacementTestResult.query.filter_by(user_id=user.id)
        .order_by(PlacementTestResult.created_at.desc())
        .first()
    )
    courses = Course.query.all()
    lesson_rows = (
        db.session.query(Lesson.id, CourseSection.course_id)
        .join(CourseSection, Lesson.section_id == CourseSection.id)
        .all()
    )
    lesson_map = {}
    all_lessons = []
    for lesson_id, course_id in lesson_rows:
        if course_id is None:
            continue
        lesson_map.setdefault(course_id, []).append(lesson_id)
        all_lessons.append(lesson_id)

    ai_response = call_ai_learning_path(user, profile, placement, courses, lesson_map, all_lessons)

    existing = (
        LearningPath.query.filter_by(user_id=user.id)
        .order_by(LearningPath.created_at.desc())
        .first()
    )
    if existing:
        LearningPathItem.query.filter_by(learning_path_id=existing.id).delete()
        db.session.delete(existing)
        db.session.flush()

    learning_path = LearningPath(user_id=user.id, course_id=ai_response["recommended_course"]["course_id"])
    db.session.add(learning_path)
    db.session.flush()
    for week in ai_response["personalized_learning_path"]["weeks"]:
        item = LearningPathItem(
            learning_path_id=learning_path.id,
            week=week["week"],
            title=week["title"],
            description=week["description"],
            recommended_lesson_ids=json.dumps(week["recommended_lesson_ids"]),
            mini_project=week["mini_project"],
            note=week["note"],
        )
        db.session.add(item)
    db.session.commit()
    return jsonify(ai_response)


@newbie_bp.get("/history")
def quiz_history():
    user_id = request.args.get("user_id", type=int)
    if not user_id:
        return jsonify({"error": "Thiếu user_id"}), 400
    history = (
        NewbieQuizHistory.query.filter_by(user_id=user_id)
        .order_by(desc(NewbieQuizHistory.created_at))
        .limit(10)
        .all()
    )
    if not history:
        return jsonify({"history": [], "summary": {}})
    total = sum(entry.score for entry in history)
    avg = total / len(history)
    summary = {
        "latest_score": history[0].score,
        "average_score": avg,
        "last_track": history[0].track,
        "last_difficulty": history[0].difficulty,
    }
    payload = []
    for entry in history:
        payload.append(
            {
                "score": entry.score,
                "difficulty": entry.difficulty,
                "track": entry.track,
                "topics": entry.topics,
                "question_count": entry.question_count,
                "created_at": entry.created_at.isoformat(),
            }
        )
    return jsonify({"history": payload, "summary": summary})


@newbie_bp.get("/learning-path/<int:user_id>")
def learning_path(user_id):
    path = (
        LearningPath.query.filter_by(user_id=user_id)
        .order_by(LearningPath.created_at.desc())
        .first()
    )
    if not path:
        return jsonify({"error": "Path not found"}), 404

    course = Course.query.get(path.course_id)
    items = (
        LearningPathItem.query.filter_by(learning_path_id=path.id)
        .order_by(LearningPathItem.week)
        .all()
    )
    weeks = []
    for item in items:
        weeks.append(
            {
                "week": item.week,
                "title": item.title,
                "description": item.description,
                "recommended_lesson_ids": json.loads(item.recommended_lesson_ids),
                "mini_project": item.mini_project,
                "note": item.note,
            }
        )

    return jsonify(
        {
            "recommended_course": _serialize_course(course),
            "personalized_learning_path": {"weeks": weeks},
        }
    )
