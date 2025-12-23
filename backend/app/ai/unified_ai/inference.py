"""
Runtime helpers for unified placement AI.
"""

from __future__ import annotations

import os
import threading
from typing import Dict, List, Tuple

from sqlalchemy import func
from flask import current_app

from app.models.model import Course
from app.models import db
from .model import UnifiedAIModel

MODEL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ""))
_MODEL = UnifiedAIModel(MODEL_DIR)
_LOAD_LOCK = threading.Lock()
_LOADED = False


def _ensure_model():
    global _LOADED
    if _LOADED:
        return
    with _LOAD_LOCK:
        if _LOADED:
            return
        _MODEL.load()
        _LOADED = True


def generate_questions(language: str, goal: str, limit: int = 8) -> List[Dict[str, str]]:
    _ensure_model()
    return _MODEL.generate_questions(language=language, goal=goal, limit=limit)


def evaluate_answers(questions: List[Dict[str, str]], answers: List[Dict[str, str]]) -> Dict[str, any]:
    _ensure_model()
    score, weak_skills = _MODEL.evaluate(questions, answers)
    level, prob = _MODEL.predict_level(score)
    return {
        "score": score,
        "weak_skills": weak_skills,
        "level": level,
        "level_probabilities": prob,
    }


def recommend_courses(level: str, language: str, limit: int = 5) -> List[Dict[str, any]]:
    """
    Simple SQLAlchemy query: match language and level; fallback to latest courses.
    """
    q = Course.query
    if language:
        q = q.filter(func.lower(Course.language) == language.lower())
    if level:
        q = q.filter(func.lower(Course.level) == level.lower())
    courses = q.order_by(Course.created_at.desc()).limit(limit).all()
    if len(courses) < limit:
        extra = Course.query.order_by(Course.created_at.desc()).limit(limit).all()
        for c in extra:
            if c not in courses:
                courses.append(c)
                if len(courses) >= limit:
                    break
    result = []
    for c in courses[:limit]:
        result.append(
            {
                "id": c.id,
                "title": c.title,
                "description": c.description,
                "level": c.level,
                "language": c.language,
                "price": float(c.price) if c.price is not None else 0,
            }
        )
    return result
