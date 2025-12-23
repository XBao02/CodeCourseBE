from __future__ import annotations

from uuid import uuid4
from flask import Blueprint, jsonify, request

from app.ai.unified_ai.inference import (
    generate_questions,
    evaluate_answers,
    recommend_courses,
)
from app.models import db
from app.models.placement_question import PlacementQuestion
from app.models.placement_test import PlacementTest
from app.models.skill_profile import SkillProfile

placement_ai_bp = Blueprint("placement_ai", __name__, url_prefix="/api/placement")


@placement_ai_bp.post("/run")
def run_placement():
    """
    Single endpoint for placement test:
    - If no answers provided: generate questions.
    - If answers provided: evaluate, predict level, recommend courses.
    """
    payload = request.get_json(force=True, silent=True) or {}
    language = (payload.get("language") or "general").lower()
    goal = (payload.get("goal") or "beginner").lower()
    answers = payload.get("answers") or []
    user_id = payload.get("user_id")
    batch_id = payload.get("batch_id")

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    if not answers:
        # Generate and persist questions
        raw_questions = generate_questions(language=language, goal=goal)
        batch_id = str(uuid4())
        saved = []
        try:
            for q in raw_questions:
                pq = PlacementQuestion(
                    user_id=user_id,
                    question=q["question"],
                    options=q["options"],
                    correct_answer=q["correct_answer"],
                    topic=q.get("skill_tag") or "general",
                    language=language,
                    difficulty=q.get("difficulty"),
                    batch_id=batch_id,
                )
                db.session.add(pq)
                db.session.flush()
                saved.append(pq)
            db.session.commit()
        except Exception:
            db.session.rollback()
            return jsonify({"error": "Không lưu được câu hỏi."}), 500
        public_questions = [
            {
                "id": q.id,
                "question": q.question,
                "options": q.options,
                "difficulty": q.difficulty,
                "skill_tag": q.topic,
                "language": q.language,
            }
            for q in saved
        ]
        return jsonify({"questions": public_questions, "batch_id": batch_id})

    if not batch_id:
        return jsonify({"error": "batch_id is required to grade answers."}), 400

    # Fetch questions from DB by batch/user to ensure integrity
    questions = (
        PlacementQuestion.query.filter_by(user_id=user_id, batch_id=batch_id)
        .order_by(PlacementQuestion.id)
        .all()
    )
    if not questions:
        return jsonify({"error": "Không tìm thấy bộ câu hỏi để chấm."}), 400

    # Rebuild question dicts for evaluator
    question_dicts = []
    answer_map = {a.get("question_id") or a.get("question"): a for a in answers}
    for q in questions:
        question_dicts.append(
            {
                "id": q.id,
                "question": q.question,
                "options": q.options,
                "correct_answer": q.correct_answer,
                "skill_tag": q.topic,
                "difficulty": q.difficulty,
            }
        )
    eval_result = evaluate_answers(questions=question_dicts, answers=answers)
    recs = recommend_courses(level=eval_result["level"], language=language, limit=5)

    # Persist placement test summary + answers JSON in strengths
    try:
        pt = PlacementTest(
            user_id=user_id,
            total_score=eval_result["score"],
            logic_score=0,
            programming_score=0,
            oop_score=0,
            web_score=0,
            level=eval_result["level"],
            language=language,
            strengths=[],
            weaknesses=eval_result["weak_skills"],
        )
        db.session.add(pt)
        db.session.flush()

        rec_ids = [c.get("id") for c in recs if c.get("id") is not None]
        sp = SkillProfile(
            user_id=user_id,
            placement_test_id=pt.id,
            level=eval_result["level"],
            strengths=[],
            weaknesses=eval_result["weak_skills"],
            recommended_topics=[],
            recommended_course_ids=rec_ids,
            language=language,
        )
        db.session.add(sp)
        db.session.commit()
    except Exception:
        db.session.rollback()
        # continue even if persistence fails

    return jsonify(
        {
            "score": eval_result["score"],
            "weak_skills": eval_result["weak_skills"],
            "level": eval_result["level"],
            "level_probabilities": eval_result["level_probabilities"],
            "recommended_courses": recs,
            "batch_id": batch_id,
        }
    )
