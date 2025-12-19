from datetime import datetime
import os

from flask import Blueprint, current_app, jsonify, request

from app.models import db
from app.models.model import Enrollment
from app.models.payment import Payment


sepay_webhook_bp = Blueprint("sepay_webhook", __name__, url_prefix="/api/payment/sepay")


@sepay_webhook_bp.post("/webhook")
def sepay_webhook():
    secret = os.getenv("SEPAY_WEBHOOK_SECRET")
    auth_header = request.headers.get("Authorization", "")
    if not secret or auth_header != f"Apikey {secret}":
        return jsonify({"error": "unauthorized"}), 401

    payload = request.get_json(silent=True) or {}
    current_app.logger.info("SePay webhook payload: %s", payload)

    payment_code = payload.get("payment_code") or payload.get("description") or payload.get("content")
    amount = payload.get("amount")
    transaction_id = payload.get("transaction_id") or payload.get("payment_code")
    bank_code = payload.get("bank_code")

    if not payment_code or amount is None:
        return jsonify({"status": "ignored"}), 200

    payment = Payment.query.filter_by(payment_code=payment_code).first()
    if not payment:
        return jsonify({"status": "ignored"}), 200

    if payment.status == "PAID":
        return jsonify({"status": "ok"}), 200

    if int(payment.amount) != int(amount):
        return jsonify({"status": "ignored"}), 200

    payment.status = "PAID"
    payment.paid_at = datetime.utcnow()
    payment.transaction_id = transaction_id
    payment.bank_code = bank_code or payment.bank_code
    db.session.commit()

    existing = Enrollment.query.filter_by(student_id=payment.user_id, course_id=payment.course_id).first()
    if not existing:
        db.session.add(
            Enrollment(
                student_id=payment.user_id,
                course_id=payment.course_id,
                status="active",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
        )
        db.session.commit()

    return jsonify({"status": "ok"}), 200
