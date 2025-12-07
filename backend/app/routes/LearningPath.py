from flask import Blueprint, jsonify

from app.models import LearningPath, LearningPathItem, SkillProfile
from app.models.model import Course
from app.services.ai_learning_path import generate_week_description

learning_path_bp = Blueprint("learning_path", __name__, url_prefix="/api/learning-path")


@learning_path_bp.get("/<int:user_id>")
def get_learning_path(user_id):
    profile = (
        SkillProfile.query.filter_by(user_id=user_id)
        .order_by(SkillProfile.created_at.desc())
        .first()
    )
    skill_profile_payload = {
        "level": "pending",
        "strengths": [],
        "weaknesses": [],
        "recommended_courses": [],
        "language": "general",
    }
    course_ids = []
    if profile:
        skill_profile_payload["level"] = profile.level
        skill_profile_payload["strengths"] = profile.strengths or []
        skill_profile_payload["weaknesses"] = profile.weaknesses or []
        skill_profile_payload["language"] = profile.language or "general"
        course_ids = profile.recommended_course_ids or []
    course_lookup = {}
    if course_ids:
        courses = Course.query.filter(Course.id.in_(course_ids)).all()
        course_lookup = {c.id: c for c in courses}
        ordered_courses = []
        for cid in course_ids:
            course = course_lookup.get(cid)
            if course:
                ordered_courses.append(
                    {
                        "id": course.id,
                        "title": course.title,
                        "slug": course.slug,
                        "level": course.level,
                        "language": course.language,
                    }
                )
        skill_profile_payload["recommended_courses"] = ordered_courses

    path = (
        LearningPath.query.filter_by(user_id=user_id)
        .order_by(LearningPath.created_at.desc())
        .first()
    )
    timeline = []
    if path:
        items = (
            LearningPathItem.query.filter_by(learning_path_id=path.id)
            .order_by(LearningPathItem.week_number)
            .all()
        )
        for idx, item in enumerate(items, start=1):
            course_ids_for_week = item.course_ids or []
            courses_for_week = []
            for weekly_course_id in course_ids_for_week:
                course = course_lookup.get(weekly_course_id)
                if course:
                    courses_for_week.append({"title": course.title, "slug": course.slug})
            description = generate_week_description(
                level=skill_profile_payload["level"] or "beginner",
                strengths=skill_profile_payload["strengths"] or [],
                weaknesses=skill_profile_payload["weaknesses"] or [],
                week_index=idx,
            )
            timeline.append(
                {
                    "week": item.week_number,
                    "title": item.title,
                    "description": description,
                    "strengths": skill_profile_payload["strengths"] or [],
                    "weaknesses": skill_profile_payload["weaknesses"] or [],
                    "course_ids": course_ids_for_week,
                }
            )

    return jsonify({"skill_profile": skill_profile_payload, "timeline": timeline})
