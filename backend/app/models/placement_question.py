from datetime import datetime

from app.models import db


class PlacementQuestion(db.Model):
    __tablename__ = "placement_questions"

    id = db.Column("Id", db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column("UserId", db.BigInteger, db.ForeignKey("Users.Id"), nullable=False)
    question = db.Column("Question", db.Text, nullable=False)
    options = db.Column("Options", db.JSON, nullable=False)
    correct_answer = db.Column("CorrectAnswer", db.String(255), nullable=False)
    topic = db.Column("Topic", db.String(64), nullable=False)
    language = db.Column("Language", db.String(64), nullable=False, default="general")
    difficulty = db.Column("Difficulty", db.String(64), nullable=True)
    batch_id = db.Column("BatchId", db.String(64), nullable=True, index=True)
    created_at = db.Column("CreatedAt", db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
