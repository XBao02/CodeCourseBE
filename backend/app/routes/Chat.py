from datetime import datetime
import os
from pathlib import Path
from flask import Blueprint, jsonify, request, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from sqlalchemy import or_, and_
from werkzeug.utils import secure_filename

from app.models import db
from app.models.model import (
    User,
    Student,
    Instructor,
    Course,
    Enrollment,
    Message,
)

chat_bp = Blueprint("chat", __name__, url_prefix="/api/chat")


def _current_user():
    """Resolve current user and role from JWT."""
    user_id = get_jwt_identity()
    try:
        user_id = int(user_id)
    except Exception:
        pass
    user = User.query.get(user_id)
    role = (get_jwt() or {}).get("role") or (user.role if user else None)
    return user, role


def _student_record(user: User):
    return Student.query.filter_by(user_id=user.id).first() if user else None


def _instructor_record(user: User):
    return Instructor.query.filter_by(user_id=user.id).first() if user else None


def _enrollment_for(student_id: int, course_id: int):
    return (
        Enrollment.query.filter_by(student_id=student_id, course_id=course_id).first()
    )


def _serialize_message(msg: Message):
    return {
        "id": msg.id,
        "fromUserId": msg.from_user_id,
        "toUserId": msg.to_user_id,
        "courseId": msg.course_id,
        "content": msg.content,
        "attachmentUrl": msg.attachment_url,
        "attachmentType": msg.attachment_type,
        "attachmentName": msg.attachment_name,
        "messageType": msg.message_type or "text",
        "createdAt": msg.created_at.isoformat() if msg.created_at else None,
        "readAt": msg.read_at.isoformat() if msg.read_at else None,
    }


@chat_bp.get("/threads")
@jwt_required()
def list_threads():
    user, role = _current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    if role == "student":
        student = _student_record(user)
        if not student:
            return jsonify([])
        enrollments = Enrollment.query.filter_by(student_id=student.id).all()
        course_ids = [e.course_id for e in enrollments]
        courses = Course.query.filter(Course.id.in_(course_ids)).all()
        course_map = {c.id: c for c in courses}
        threads = []
        for e in enrollments:
            course = course_map.get(e.course_id)
            if not course or not course.instructor:
                continue
            inst_user = course.instructor.user if course.instructor else None
            # Last message between this student and instructor for the course
            last_msg = (
                Message.query.filter(
                    Message.course_id == course.id,
                    or_(
                        and_(
                            Message.from_user_id == user.id,
                            Message.to_user_id == inst_user.id if inst_user else None,
                        ),
                        and_(
                            Message.from_user_id == inst_user.id if inst_user else None,
                            Message.to_user_id == user.id,
                        ),
                    ),
                )
                .order_by(Message.created_at.desc())
                .first()
            )
            unread = (
                Message.query.filter(
                    Message.course_id == course.id,
                    Message.to_user_id == user.id,
                    Message.read_at.is_(None),
                ).count()
            )
            threads.append(
                {
                    "courseId": course.id,
                    "courseTitle": course.title,
                    "instructorId": inst_user.id if inst_user else None,
                    "instructorName": inst_user.full_name if inst_user else None,
                    "studentId": student.id,
                    "lastMessage": last_msg.content if last_msg else None,
                    "lastAt": last_msg.created_at.isoformat()
                    if last_msg and last_msg.created_at
                    else None,
                    "unread": unread,
                }
            )
        return jsonify(threads)

    if role == "instructor":
        inst = _instructor_record(user)
        if not inst:
            return jsonify([])
        # Students enrolled in instructor's courses
        course_ids = [c.id for c in inst.courses]
        enrollments = (
            Enrollment.query.filter(Enrollment.course_id.in_(course_ids)).all()
            if course_ids
            else []
        )
        # Map student_id -> student record
        student_ids = list({e.student_id for e in enrollments})
        students = (
            Student.query.filter(Student.id.in_(student_ids)).all() if student_ids else []
        )
        student_map = {s.id: s for s in students}
        threads = []
        for e in enrollments:
            st = student_map.get(e.student_id)
            if not st or not st.user:
                continue
            course = next((c for c in inst.courses if c.id == e.course_id), None)
            if not course:
                continue
            last_msg = (
                Message.query.filter(
                    Message.course_id == course.id,
                    or_(
                        and_(
                            Message.from_user_id == user.id,
                            Message.to_user_id == st.user.id,
                        ),
                        and_(
                            Message.from_user_id == st.user.id,
                            Message.to_user_id == user.id,
                        ),
                    ),
                )
                .order_by(Message.created_at.desc())
                .first()
            )
            unread = (
                Message.query.filter(
                    Message.course_id == course.id,
                    Message.to_user_id == user.id,
                    Message.read_at.is_(None),
                ).count()
            )
            threads.append(
                {
                    "courseId": course.id,
                    "courseTitle": course.title,
                    "studentId": st.id,
                    "studentName": st.user.full_name,
                    "studentUserId": st.user.id,
                    "instructorId": inst.id,
                    "lastMessage": last_msg.content if last_msg else None,
                    "lastAt": last_msg.created_at.isoformat()
                    if last_msg and last_msg.created_at
                    else None,
                    "unread": unread,
                }
            )
        return jsonify(threads)

    return jsonify({"error": "Role not supported"}), 403


@chat_bp.get("/messages")
@jwt_required()
def list_messages():
    user, role = _current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    course_id = request.args.get("course_id", type=int)
    student_id = request.args.get("student_id", type=int)
    since_iso = request.args.get("since")

    if not course_id:
        return jsonify({"error": "course_id is required"}), 400

    course = Course.query.filter_by(id=course_id).first()
    if not course:
        return jsonify({"error": "Course not found"}), 404

    if role == "student":
        student = _student_record(user)
        if not student:
            return jsonify({"error": "Student profile not found"}), 404
        student_id = student.id
        if not _enrollment_for(student.id, course_id):
            return jsonify({"error": "Not enrolled in this course"}), 403
        other_user_id = course.instructor.user.id if course.instructor and course.instructor.user else None
    elif role == "instructor":
        inst = _instructor_record(user)
        if not inst or inst.id != course.instructor_id:
            return jsonify({"error": "Not allowed"}), 403
        if not student_id:
            return jsonify({"error": "student_id is required"}), 400
        if not _enrollment_for(student_id, course_id):
            return jsonify({"error": "Student not enrolled in this course"}), 403
        student_row = Student.query.filter_by(id=student_id).first()
        other_user_id = student_row.user.id if student_row and student_row.user else None
    else:
        return jsonify({"error": "Role not supported"}), 403

    if not other_user_id:
        return jsonify({"error": "Participant not found"}), 404

    since_dt = None
    if since_iso:
        try:
            since_dt = datetime.fromisoformat(since_iso)
        except Exception:
            since_dt = None

    q = Message.query.filter(
        Message.course_id == course_id,
        or_(
            and_(Message.from_user_id == user.id, Message.to_user_id == other_user_id),
            and_(Message.from_user_id == other_user_id, Message.to_user_id == user.id),
        ),
    ).order_by(Message.created_at.asc())
    if since_dt:
        q = q.filter(Message.created_at > since_dt)

    messages = q.all()

    # Mark unread messages addressed to current user as read
    unread = [
        m for m in messages if m.to_user_id == user.id and m.read_at is None
    ]
    if unread:
        now = datetime.utcnow()
        for m in unread:
            m.read_at = now
        db.session.commit()

    return jsonify([_serialize_message(m) for m in messages])


@chat_bp.post("/messages")
@jwt_required()
def send_message():
    user, role = _current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    payload = request.get_json(silent=True) or {}
    course_id = payload.get("course_id")
    content = (payload.get("content") or "").strip()
    attachment_url = (payload.get("attachment_url") or "").strip()
    attachment_type = (payload.get("attachment_type") or "").strip()
    attachment_name = (payload.get("attachment_name") or "").strip()
    message_type = (payload.get("message_type") or "").strip()
    student_id = payload.get("student_id")

    if not course_id:
        return jsonify({"error": "course_id is required"}), 400
    if not content and not attachment_url:
        return jsonify({"error": "content or attachment is required"}), 400

    course = Course.query.filter_by(id=course_id).first()
    if not course:
        return jsonify({"error": "Course not found"}), 404

    if role == "student":
        student = _student_record(user)
        if not student:
            return jsonify({"error": "Student profile not found"}), 404
        if not _enrollment_for(student.id, course_id):
            return jsonify({"error": "Not enrolled in this course"}), 403
        receiver_id = (
            course.instructor.user.id if course.instructor and course.instructor.user else None
        )
        student_id = student.id
    elif role == "instructor":
        inst = _instructor_record(user)
        if not inst or inst.id != course.instructor_id:
            return jsonify({"error": "Not allowed"}), 403
        if not student_id:
            return jsonify({"error": "student_id is required"}), 400
        if not _enrollment_for(student_id, course_id):
            return jsonify({"error": "Student not enrolled in this course"}), 403
        student_row = Student.query.filter_by(id=student_id).first()
        receiver_id = student_row.user.id if student_row and student_row.user else None
    else:
        return jsonify({"error": "Role not supported"}), 403

    if not receiver_id:
        return jsonify({"error": "Receiver not found"}), 404

    if not message_type:
        if attachment_type == "image":
            message_type = "image"
        elif attachment_type == "file":
            message_type = "file"
        else:
            message_type = "text"

    msg = Message(
        channel="direct",
        from_user_id=user.id,
        to_user_id=receiver_id,
        course_id=course_id,
        content=content or "",
        attachment_url=attachment_url or None,
        attachment_type=attachment_type or None,
        attachment_name=attachment_name or None,
        message_type=message_type or "text",
        created_at=datetime.utcnow(),
    )
    db.session.add(msg)
    db.session.commit()

    return jsonify(_serialize_message(msg)), 201


UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads" / "chat"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MAX_SIZE = 10 * 1024 * 1024  # 10MB
IMAGE_EXTS = {"jpg", "jpeg", "png", "webp"}
FILE_EXTS = {"pdf", "docx", "zip", "txt"}


@chat_bp.post("/upload")
@jwt_required()
def upload_attachment():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    f = request.files["file"]
    if not f.filename:
        return jsonify({"error": "Empty filename"}), 400
    ext = f.filename.rsplit(".", 1)[-1].lower()
    if not (ext in IMAGE_EXTS or ext in FILE_EXTS):
        return jsonify({"error": "Unsupported file type"}), 400
    f.seek(0, os.SEEK_END)
    size = f.tell()
    f.seek(0)
    if size > MAX_SIZE:
        return jsonify({"error": "File too large (max 10MB)"}), 400
    safe_name = secure_filename(f.filename)
    filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}_{safe_name}"
    dest = UPLOAD_DIR / filename
    f.save(dest)
    attachment_type = "image" if ext in IMAGE_EXTS else "file"
    url = f"/api/chat/uploads/{filename}"
    return jsonify(
        {
            "message_type": attachment_type,
            "content": url,
            "original_filename": safe_name,
        }
    )


@chat_bp.get("/uploads/<path:filename>")
def serve_chat_upload(filename):
    return send_from_directory(UPLOAD_DIR, filename, as_attachment=False)
