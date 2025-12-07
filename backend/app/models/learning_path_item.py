from datetime import datetime

from app.models import db


class LearningPathItem(db.Model):
    __tablename__ = "learning_path_items"

    id = db.Column("Id", db.BigInteger, primary_key=True, autoincrement=True)
    learning_path_id = db.Column(
        "LearningPathId", db.BigInteger, db.ForeignKey("learning_paths.Id"), nullable=False
    )
    week_number = db.Column("WeekNumber", db.Integer, nullable=False)
    title = db.Column("Title", db.String(255), nullable=False)
    description = db.Column("Description", db.Text, nullable=True)
    topics = db.Column("Topics", db.JSON, nullable=True)
    course_ids = db.Column("CourseIds", db.JSON, nullable=True)
    created_at = db.Column(
        "CreatedAt", db.DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
