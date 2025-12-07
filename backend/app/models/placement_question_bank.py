from app.models import db


class PlacementQuestionBank(db.Model):
    __tablename__ = "placement_question_bank"

    id = db.Column("Id", db.BigInteger, primary_key=True, autoincrement=True)
    topic = db.Column("Topic", db.String(64), nullable=False)
    question = db.Column("Question", db.Text, nullable=False)
    options = db.Column("Options", db.JSON, nullable=False)
    correct_answer = db.Column("CorrectAnswer", db.String(255), nullable=False)
    difficulty = db.Column("Difficulty", db.String(64), nullable=True)
    language = db.Column("Language", db.String(64), nullable=False, default="general")
