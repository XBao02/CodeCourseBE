from __future__ import annotations

import os
from datetime import datetime
from decimal import Decimal

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from app.models import db
from app.models.model import Course, Enrollment, Student
from app.models.payment import Payment

va_payment_bp = Blueprint("payment_va", __name__, url_prefix="/api/payment")


def _resolve_student(user_id: int | None) -> Student | None:
    if not user_id:
        return None
    return Student.query.filter_by(user_id=user_id).first()


def _ensure_enrollment(student_id: int | None, course_id: int | None) -> None:
    if not student_id or not course_id:
        return
    existing = Enrollment.query.filter_by(student_id=student_id, course_id=course_id).first()
    if existing:
        existing.status = "active"
        existing.updated_at = datetime.utcnow()
    else:
        db.session.add(
            Enrollment(
                student_id=student_id,
                course_id=course_id,
                status="active",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
        )


@va_payment_bp.post("/create")
def create_va_payment():
    """Create a VA payment order and return VA info for the frontend."""
    verify_jwt_in_request()
    identity = get_jwt_identity()
    user_id = identity.get("id") if isinstance(identity, dict) else identity
    payload = request.get_json(silent=True) or {}
    course_id = payload.get("course_id")
    if not course_id:
        return jsonify({"error": "course_id is required"}), 400
    if not user_id:
        return jsonify({"error": "unauthorized"}), 401

    course = Course.query.filter_by(id=course_id).first()
    if not course:
        return jsonify({"error": "Course not found"}), 404

    amount = Decimal(course.price or 0)
    if amount < 0:
        amount = Decimal(0)

    va_number = os.getenv("SEPAY_VA_ACCOUNT") or os.getenv("VA_ACCOUNT_NUMBER")
    bank_code = os.getenv("SEPAY_BANK_CODE", "MBbank")

    if not va_number or not bank_code:
        return jsonify({"error": "VA configuration missing"}), 500

    payment = (
        Payment.query.filter_by(user_id=user_id, course_id=course.id)
        .order_by(Payment.id.desc())
        .first()
    )
    if not payment:
        payment = Payment(
            user_id=user_id,
            course_id=course.id,
            amount=amount,
            va_account_number=va_number,
            bank_code=bank_code,
            status="PENDING",
            created_at=datetime.utcnow(),
        )
        db.session.add(payment)
        db.session.commit()
        payment.payment_code = f"PAY_{payment.id}"
        db.session.commit()

    return (
        jsonify(
            {
                "payment_id": payment.id,
                "payment_code": payment.payment_code,
                "va_account_number": va_number,
                "bank_code": bank_code,
                "amount": int(amount),
                "order_code": payment.payment_code,
                "status": (payment.status or "").lower(),
            }
        ),
        200,
    )


@va_payment_bp.post("/confirm")
def confirm_va_payment():
    verify_jwt_in_request()
    identity = get_jwt_identity()
    user_id = identity.get("id") if isinstance(identity, dict) else identity
    payload = request.get_json(silent=True) or {}
    course_id = payload.get("course_id")
    payment_id = payload.get("payment_id")
    if not user_id or not course_id:
        return jsonify({"error": "missing course_id"}), 400

    query = Payment.query.filter_by(user_id=user_id, course_id=course_id)
    if payment_id:
        query = query.filter_by(id=payment_id)
    payment = query.order_by(Payment.id.desc()).first()
    if not payment:
        return jsonify({"error": "payment not found"}), 404

    student = _resolve_student(user_id)
    if not student:
        return jsonify({"error": "student not found"}), 404

    if payment.status != "PAID":
        payment.status = "PAID"
        payment.paid_at = datetime.utcnow()
    _ensure_enrollment(student.id, payment.course_id)
    db.session.commit()

    return jsonify({"status": "paid", "course_id": payment.course_id, "payment_id": payment.id}), 200


@va_payment_bp.get("/status/<int:payment_id>")
def payment_status(payment_id: int):
    payment = Payment.query.filter_by(id=payment_id).first()
    if not payment:
        return jsonify({"error": "not found"}), 404
    return jsonify({"status": (payment.status or "").lower(), "course_id": payment.course_id}), 200


@va_payment_bp.get("/<int:payment_id>/status")
def payment_status_legacy(payment_id: int):
    return payment_status(payment_id)
