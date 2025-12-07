from uuid import uuid4
from typing import Dict

from flask import Blueprint, jsonify, request
from sqlalchemy import func

from app.models import (
    PlacementTest,
    SkillProfile,
    LearningPath,
    LearningPathItem,
    PlacementQuestion,
    PlacementQuestionBank,
    db,
)
from app.models.model import Course
from app.services.ai_generate_questions import generate_questions_with_ai
from app.services.ai_learning_path import generate_learning_path_with_ai
from app.services.recommender import recommend_courses

placement_bp = Blueprint("placement", __name__, url_prefix="/api/placement")

TOPIC_TO_SKILL_GROUP = {
    "logic": "logic",
    "programming": "programming",
    "oop": "oop",
    "web": "web",
    "syntax": "programming",
    "library": "web",
    "closure": "programming",
    "event loop": "web",
    "async": "web",
    "typing": "programming",
    "pointer": "programming",
    "reference": "programming",
    "stl": "programming",
    "templates": "programming",
    "jvm": "oop",
    "thread": "oop",
    "concurrency": "oop",
    "performance": "programming",
}
TOPIC_SUGGESTIONS = {
    "syntax": ["Review language syntax and write small examples using unique operators."],
    "oop": ["Build small class hierarchies and practice SOLID design for your language."],
    "library": ["Explore the standard library modules and integrate them into mini projects."],
    "closure": ["Trace closure scopes and practice building functional-style helpers."],
    "event loop": ["Review asynchronous flows and the event loop model."],
    "async": ["Implement async/await or equivalent concurrency constructs."],
    "pointer": ["Study pointer/reference management and smart pointer alternatives."],
    "reference": ["Practice ownership models and the nuances of references."],
    "stl": ["Rework standard library algorithms with custom iterators."],
    "templates": ["Deepen template/generic programming paradigms for reusable types."],
    "jvm": ["Inspect JVM launch options and bytecode implications."],
    "thread": ["Practice thread synchronization and safe concurrency patterns."],
    "concurrency": ["Explore concurrency libraries and share-nothing architecture."],
    "performance": ["Profile code paths and apply caching/optimization strategies."],
}


@placement_bp.post("/start")
def start_placement():
    payload = request.get_json(force=True, silent=True) or {}
    user_id = payload.get("user_id")
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400
    session_id = str(uuid4())
    return jsonify({"session_id": session_id, "status": "ready"})


@placement_bp.post("/generate-questions")
def generate_questions():
    payload = request.get_json(force=True, silent=True) or {}
    user_id = payload.get("user_id")
    learning_goal = payload.get("learning_goal")
    language = (payload.get("language") or "general").lower()
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    questions = generate_questions_with_ai(user_id, learning_goal, language)
    saved = []
    batch_id = str(uuid4())
    for question in questions:
        difficulty = (question.get("difficulty") or "intermediate").lower()
        topic = question.get("topic") or "syntax"
        pq = PlacementQuestion(
            user_id=user_id,
            question=question["question"],
            options=question["options"],
            correct_answer=question["correct_answer"],
            topic=topic,
            language=language,
            difficulty=difficulty,
            batch_id=batch_id,
        )
        db.session.add(pq)
        saved.append(pq)
        existing_bank = PlacementQuestionBank.query.filter_by(question=question["question"], language=language).first()
        if not existing_bank:
            bank_entry = PlacementQuestionBank(
                topic=topic,
                question=question["question"],
                options=question["options"],
                correct_answer=question["correct_answer"],
                difficulty=difficulty,
                language=language,
            )
            db.session.add(bank_entry)
    db.session.commit()

    return jsonify(
        [
            {
                "id": q.id,
            "question": q.question,
            "options": q.options,
            "topic": q.topic,
            "language": q.language,
            "difficulty": q.difficulty,
                "language": q.language,
            }
            for q in saved
        ]
    )


@placement_bp.get("/questions")
def list_questions():
    user_id = request.args.get("user_id", type=int)
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400
    questions = (
        PlacementQuestion.query.filter_by(user_id=user_id)
        .order_by(PlacementQuestion.created_at.desc())
        .limit(20)
        .all()
    )
    return jsonify(
        {
            "questions": [
                {
                    "id": q.id,
                    "question": q.question,
                    "options": q.options,
                    "topic": q.topic,
                    "language": q.language,
                    "difficulty": q.difficulty,
                }
                for q in questions
            ]
        }
    )


@placement_bp.get("/questions/latest/<int:user_id>")
def latest_questions(user_id):
    latest_question = (
        PlacementQuestion.query.filter_by(user_id=user_id)
        .order_by(PlacementQuestion.created_at.desc())
        .first()
    )
    if not latest_question or not latest_question.batch_id:
        return jsonify([])
    batch_id = latest_question.batch_id
    questions = (
        PlacementQuestion.query.filter_by(user_id=user_id, batch_id=batch_id)
        .order_by(PlacementQuestion.id)
        .all()
    )
    return jsonify(
        [
            {
                "id": q.id,
                "question": q.question,
                "options": q.options,
                "topic": q.topic,
            }
            for q in questions
        ]
    )


def _pick_level(total):
    if total >= 70:
        return "advanced"
    if total >= 40:
        return "intermediate"
    return "beginner"


@placement_bp.post("/submit")
def submit_placement():
    data = request.get_json(force=True, silent=True) or {}
    user_id = data.get("user_id")
    answers = data.get("answers", [])
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400
    if not isinstance(answers, list) or not answers:
        return jsonify({"error": "Answers list required"}), 400

    q_ids = [item.get("question_id") for item in answers if item.get("question_id")]
    questions = (
        PlacementQuestion.query.filter(PlacementQuestion.user_id == user_id, PlacementQuestion.id.in_(q_ids))
        .all()
    )
    question_map = {q.id: q for q in questions}
    languages = [q.language for q in questions if q.language]
    language = (data.get("language") or (languages[0] if languages else "general")).lower()
    topic_scores: Dict[str, float] = {}
    total_score = 0
    for answer in answers:
        q_id = answer.get("question_id")
        chosen = answer.get("chosen_answer") or answer.get("chosen_option") or answer.get("value")
        question = question_map.get(q_id)
        if not question:
            continue
        topic = (question.topic or "syntax").strip().lower()
        topic_scores.setdefault(topic, 0)
        correct = (
            chosen
            and str(chosen).strip().lower() == str(question.correct_answer).strip().lower()
        )
        if correct:
            topic_scores[topic] += 10
            total_score += 10
    if not topic_scores:
        topic_scores["syntax"] = 0
    level = _pick_level(total_score)
    sorted_topics = sorted(topic_scores.items(), key=lambda item: item[1], reverse=True)
    strengths = []
    weaknesses = []
    for topic, _ in sorted_topics:
        if len(strengths) < 2 and topic not in strengths:
            strengths.append(topic)
    for topic, _ in reversed(sorted_topics):
        if len(weaknesses) < 2 and topic not in weaknesses:
            weaknesses.append(topic)
    if not strengths:
        strengths = ["syntax"]
    if not weaknesses:
        weaknesses = strengths[-2:] if len(strengths) > 1 else [strengths[0]]
    general_scores = {"logic": 0, "programming": 0, "oop": 0, "web": 0}
    for topic, score in topic_scores.items():
        group = TOPIC_TO_SKILL_GROUP.get(topic, "programming")
        general_scores[group] = general_scores.get(group, 0) + score

    placement = PlacementTest(
        user_id=user_id,
        total_score=total_score,
        logic_score=general_scores.get("logic", 0),
        programming_score=general_scores.get("programming", 0),
        oop_score=general_scores.get("oop", 0),
        web_score=general_scores.get("web", 0),
        level=level,
        language=language,
        strengths=strengths,
        weaknesses=weaknesses,
    )
    recommended_topics = []
    seen_topics = set()
    for weak_topic in weaknesses:
        suggestions = TOPIC_SUGGESTIONS.get(weak_topic) or []
        for hint in suggestions:
            if hint not in seen_topics:
                recommended_topics.append(hint)
                seen_topics.add(hint)
    if not recommended_topics:
        recommended_topics = ["Tập trung vào các khái niệm nền tảng để cải thiện hiệu suất học tập."]
    # ensure uniqueness preserving order
    seen = set()
    recommended_topics = [topic for topic in recommended_topics if topic not in seen and not seen.add(topic)]
    # recommended courses based on level and key weakness
    suggestion_topic = weaknesses[0] if weaknesses else None
    recommended_courses = recommend_courses(level=level, topic=suggestion_topic, language=language, limit=6)
    course_ids = [c["id"] for c in recommended_courses]
    profile = SkillProfile(
        user_id=user_id,
        placement_test=placement,
        level=level,
        strengths=strengths,
        weaknesses=weaknesses,
        recommended_topics=recommended_topics,
        recommended_course_ids=course_ids,
        language=language,
    )

    ai_payload = generate_learning_path_with_ai(placement, profile)
    learning_path = LearningPath(
        user_id=user_id,
        raw_ai_response=ai_payload.get("raw_ai_response"),
        recommended_course_ids=course_ids,
    )
    db.session.add(placement)
    db.session.add(profile)
    db.session.add(learning_path)
    db.session.flush()

    ai_weeks = ai_payload.get("weeks") or []
    if ai_weeks:
        for week in ai_weeks:
            item = LearningPathItem(
                learning_path_id=learning_path.id,
                week_number=week.get("week_number"),
                title=week.get("title") or f"Week {week.get('week_number')}",
                description=week.get("description"),
                topics=week.get("topics") or [],
                course_ids=week.get("course_ids") or [],
            )
            db.session.add(item)
    elif course_ids:
        courses = Course.query.filter(Course.id.in_(course_ids)).all()
        course_map = {course.id: course for course in courses}
        for idx, course_id in enumerate(course_ids, start=1):
            course = course_map.get(course_id)
            item = LearningPathItem(
                learning_path_id=learning_path.id,
                week_number=idx,
                title=f"Week {idx}: {course.title if course else 'Course focus'}",
                description=course.description if course else None,
                topics=[course.title] if course else [],
                course_ids=[course_id],
            )
            db.session.add(item)

    db.session.commit()

    return jsonify(
        {
            "placement_id": placement.id,
            "user_id": user_id,
            "level": level,
            "language": language,
            "total_score": float(total_score),
            "strengths": strengths,
            "weaknesses": weaknesses,
            "profile": {
                "level": profile.level,
                "language": profile.language,
                "strengths": profile.strengths,
                "weaknesses": profile.weaknesses,
                "recommended_topics": profile.recommended_topics,
            },
        }
    )


@placement_bp.get("/result/<int:user_id>")
def get_placement_result(user_id):
    placement = (
        PlacementTest.query.filter_by(user_id=user_id)
        .order_by(PlacementTest.created_at.desc())
        .first()
    )
    if not placement:
        return jsonify({"placement": None, "profile": None})
    profile = (
        SkillProfile.query.filter_by(user_id=user_id)
        .order_by(SkillProfile.created_at.desc())
        .first()
    )
    return jsonify(
        {
            "placement": {
                "total_score": float(placement.total_score),
                "logic_score": float(placement.logic_score),
                "programming_score": float(placement.programming_score),
                "oop_score": float(placement.oop_score),
                "web_score": float(placement.web_score),
                "level": placement.level,
                "language": placement.language,
                "strengths": placement.strengths or [],
                "weaknesses": placement.weaknesses or [],
                "created_at": placement.created_at.isoformat(),
            },
            "profile": {
                "level": profile.level if profile else "pending",
                "language": profile.language if profile else "general",
                "strengths": profile.strengths or [],
                "weaknesses": profile.weaknesses or [],
                "recommended_topics": profile.recommended_topics or [],
            },
        }
    )
