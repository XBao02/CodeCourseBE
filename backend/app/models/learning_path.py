from datetime import datetime

from app.models import db


class LearningPath(db.Model):
    __tablename__ = "learning_paths"

    id = db.Column("Id", db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column("UserId", db.BigInteger, db.ForeignKey("Users.Id"), nullable=False)
    raw_ai_response = db.Column("RawAIResponse", db.JSON, nullable=True)
    recommended_course_ids = db.Column("RecommendedCourseIds", db.JSON, nullable=True)
    created_at = db.Column(
        "CreatedAt", db.DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )

    items = db.relationship("LearningPathItem", backref="learning_path", cascade="all, delete-orphan")
