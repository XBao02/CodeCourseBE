import os
import logging

from werkzeug.security import generate_password_hash

from app.models import db
from app.models.model import User, Instructor

logger = logging.getLogger(__name__)


def _env_or_default(key: str, default: str) -> str:
    value = os.getenv(key)
    return value.strip() if isinstance(value, str) and value.strip() else default


def seed_default_instructor():
    """Ensure the demo instructor account from the docs exists."""
    email = _env_or_default("DEFAULT_INSTRUCTOR_EMAIL", "instructor@example.com").lower()
    password = _env_or_default("DEFAULT_INSTRUCTOR_PASSWORD", "password123")
    full_name = _env_or_default("DEFAULT_INSTRUCTOR_NAME", "Instructor Demo")
    role = _env_or_default("DEFAULT_INSTRUCTOR_ROLE", "instructor")

    if not email or not password:
        logger.info("Default instructor credentials are missing; skipping seeding.")
        return

    try:
        existing = User.query.filter(db.func.lower(User.email) == email).first()
        if existing:
            updated = False
            if existing.role != role:
                existing.role = role
                updated = True
            if existing.full_name != full_name:
                existing.full_name = full_name
                updated = True

            instructor_row = Instructor.query.filter_by(user_id=existing.id).first()
            if not instructor_row and role == "instructor":
                db.session.add(Instructor(user_id=existing.id))
                updated = True

            if updated:
                db.session.commit()
                logger.info("Updated default instructor record (%s)", email)
            else:
                logger.debug("Default instructor already exists (%s)", email)
            return

        user = User(
            email=email,
            password_hash=generate_password_hash(password),
            full_name=full_name,
            role=role,
            is_active=True,
        )
        db.session.add(user)
        db.session.flush()
        if role == "instructor":
            db.session.add(Instructor(user_id=user.id))
        db.session.commit()
        logger.info("Created default instructor account (%s)", email)
    except Exception as exc:  # pragma: no cover - best effort seeding
        db.session.rollback()
        logger.error("Unable to seed default instructor account: %s", exc)

