import os
import logging

from werkzeug.security import generate_password_hash

from app.models import db
from app.models.model import User, Instructor
from app.models.placement_question_bank import PlacementQuestionBank

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


def seed_question_bank():
    entries = [
        {
            "topic": "logic",
            "question": "Nếu A ⇒ B và A đúng thì B có thể sai không?",
            "options": ["Không", "Có", "Không đủ thông tin", "Tùy trường hợp"],
            "correct_answer": "Không",
            "difficulty": "beginner",
        },
        {
            "topic": "programming",
            "question": "Hàm map trong JavaScript trả về kiểu dữ liệu nào?",
            "options": ["Array", "Object", "Function", "Promise"],
            "correct_answer": "Array",
            "difficulty": "beginner",
        },
        {
            "topic": "oop",
            "question": "Tính kế thừa cho phép gì cho các lớp con?",
            "options": ["Sao chép toàn bộ code", "Lấy lại thuộc tính/phương thức", "Tạo giao diện mới", "Thực thi đa luồng"],
            "correct_answer": "Lấy lại thuộc tính/phương thức",
            "difficulty": "beginner",
        },
        {
            "topic": "web",
            "question": "Thuộc tính CSS nào điều chỉnh màu chữ?",
            "options": ["background", "font-weight", "color", "text-decoration"],
            "correct_answer": "color",
            "difficulty": "beginner",
        },
        {
            "topic": "logic",
            "question": "Biểu thức !(true && false) có kết quả là?",
            "options": ["true", "false", "undefined", "1"],
            "correct_answer": "true",
            "difficulty": "beginner",
        },
        {
            "topic": "programming",
            "question": "Trong Python, từ khóa nào tạo vòng lặp while?",
            "options": ["loop", "repeat", "while", "for"],
            "correct_answer": "while",
            "difficulty": "beginner",
        },
        {
            "topic": "oop",
            "question": "SOLID chữ D nghĩa là gì?",
            "options": ["Dependency Inversion", "Data Encapsulation", "Design Pattern", "Dynamic Binding"],
            "correct_answer": "Dependency Inversion",
            "difficulty": "intermediate",
        },
        {
            "topic": "web",
            "question": "HTTP status code 201 nghĩa là gì?",
            "options": ["Thành công chung", "Tài nguyên được tạo", "Không tìm thấy", "Lỗi máy chủ"],
            "correct_answer": "Tài nguyên được tạo",
            "difficulty": "intermediate",
        },
    ]
    if PlacementQuestionBank.query.count():
        return
    try:
        db.session.bulk_insert_mappings(PlacementQuestionBank, entries)
        db.session.commit()
        logger.info("Seeded placement question bank (%d entries)", len(entries))
    except Exception as exc:
        db.session.rollback()
        logger.error("Unable to seed placement question bank: %s", exc)
