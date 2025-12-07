from datetime import datetime

from app.models import db


class PlacementTest(db.Model):
    __tablename__ = "placement_tests"

    id = db.Column("Id", db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column("UserId", db.BigInteger, db.ForeignKey("Users.Id"), nullable=False)
    total_score = db.Column("TotalScore", db.Numeric(6, 2), nullable=False, default=0)
    logic_score = db.Column("LogicScore", db.Numeric(6, 2), nullable=False, default=0)
    programming_score = db.Column("ProgrammingScore", db.Numeric(6, 2), nullable=False, default=0)
    oop_score = db.Column("OOPScore", db.Numeric(6, 2), nullable=False, default=0)
    web_score = db.Column("WebScore", db.Numeric(6, 2), nullable=False, default=0)
    level = db.Column("Level", db.String(32), nullable=False, default="pending")
    language = db.Column("Language", db.String(64), nullable=False, default="general")
    strengths = db.Column("Strengths", db.JSON)
    weaknesses = db.Column("Weaknesses", db.JSON)
    created_at = db.Column("CreatedAt", db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    profile = db.relationship("SkillProfile", backref="placement_test", uselist=False)
