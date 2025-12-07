from datetime import datetime

from app.models import db


class SkillProfile(db.Model):
    __tablename__ = "skill_profiles"

    id = db.Column("Id", db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column("UserId", db.BigInteger, db.ForeignKey("Users.Id"), nullable=False)
    placement_test_id = db.Column(
        "PlacementTestId", db.BigInteger, db.ForeignKey("placement_tests.Id")
    )
    level = db.Column("Level", db.String(32), nullable=False, default="pending")
    strengths = db.Column("Strengths", db.JSON, nullable=True)
    weaknesses = db.Column("Weaknesses", db.JSON, nullable=True)
    recommended_topics = db.Column("RecommendedTopics", db.JSON, nullable=True)
    recommended_course_ids = db.Column("RecommendedCourseIds", db.JSON, nullable=True)
    language = db.Column("Language", db.String(64), nullable=False, default="general")
    created_at = db.Column(
        "CreatedAt", db.DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
