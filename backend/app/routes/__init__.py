
"""Routes package initializer."""

from functools import wraps
from flask import jsonify, g
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt
from sqlalchemy import text
from app.utils.db import engine
from .Student import student_bp
from .Auth import auth_bp
from .Admin import admin_bp
from .Instructor import instructor_bp
from .AIQuiz import ai_quiz_bp

__all__ = ['student_bp', 'auth_bp', 'admin_bp', 'instructor_bp', 'ai_quiz_bp']

def resolve_role(user_id: int) -> str:
    """Xác định role dựa trên 3 bảng admins/instructors/students."""
    sql = """
    SELECT
      CASE
        WHEN EXISTS(SELECT 1 FROM Admins WHERE UserId=:uid) THEN 'admin'
        WHEN EXISTS(SELECT 1 FROM Instructors WHERE UserId=:uid) THEN 'instructor'
        WHEN EXISTS(SELECT 1 FROM Students WHERE UserId=:uid) THEN 'student'
        ELSE 'guest'
      END AS role
    """
    with engine.begin() as conn:
        role = conn.execute(text(sql), {"uid": user_id}).scalar()
    return role or "guest"

def require_roles(*allowed_roles):
    """Decorator yêu cầu JWT + role hợp lệ."""
    def deco(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()  # Now it's a string
            user_id = int(user_id) if isinstance(user_id, str) else user_id
            
            if not user_id:
                return jsonify({"error": "Unauthorized"}), 401

            # Get role from JWT claims
            claims = get_jwt()
            current_role = claims.get('role', 'student')

            if current_role not in allowed_roles:
                return jsonify({"error": "Forbidden", "role": current_role}), 403

            g.current_user_id = user_id
            g.current_role = current_role
            return fn(*args, **kwargs)
        return wrapper
    return deco



