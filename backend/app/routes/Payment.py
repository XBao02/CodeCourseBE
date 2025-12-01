"""Payment endpoints integrating MoMo for course purchases."""

from __future__ import annotations

import hashlib
import hmac
import os
import time
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

import requests
from dotenv import load_dotenv
from flask import Blueprint, current_app, jsonify, request
from sqlalchemy import or_

from app.models import db
from app.models.model import Course, Enrollment, Invoice, Student

payment_bp = Blueprint("payment", __name__, url_prefix="/api/payments")


def _env(key: str, default: str = "") -> str:
    load_dotenv()
    return os.getenv(key, default)


def _momo_config() -> dict[str, str]:
    return {
        "partner_code": _env("MOMO_PARTNER_CODE"),
        "access_key": _env("MOMO_ACCESS_KEY"),
        "secret_key": _env("MOMO_SECRET_KEY"),
        "endpoint": _env("MOMO_ENDPOINT", "https://test-payment.momo.vn/v2/gateway/api/create"),
        "ipn_url": _env("MOMO_IPN_URL", ""),
        "redirect_url": _env("MOMO_REDIRECT_URL", ""),
    }


def _hmac_sha256(secret: str, raw: str) -> str:
    return hmac.new(secret.encode(), raw.encode(), hashlib.sha256).hexdigest()


def _generate_invoice_number() -> str:
    return uuid.uuid4().hex[:20]


def _create_invoice(student: Student, course: Course, method: str, reference: str | None = None) -> Invoice:
    invoice = Invoice(
        invoice_number=_generate_invoice_number(),
        student_id=student.id,
        course_id=course.id,
        amount=Decimal(course.price or 0),
        currency=course.currency or "VND",
        payment_method=method,
        payment_status="pending",
        reference_code=reference,
        issued_at=datetime.now(timezone.utc),
    )
    db.session.add(invoice)
    db.session.flush()
    return invoice


def _ensure_enrollment(student_id: int, course_id: int) -> None:
    existing = Enrollment.query.filter_by(student_id=student_id, course_id=course_id).first()
    if existing:
        existing.status = "active"
        existing.updated_at = datetime.now(timezone.utc)
    else:
        db.session.add(
            Enrollment(
                student_id=student_id,
                course_id=course_id,
                status="active",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
        )


@payment_bp.post("/momo/create")
def create_momo_payment():
    """Create MoMo payment and pending invoice for a course."""
    payload = request.get_json(silent=True) or {}
    student_id = payload.get("student_id")
    course_id = payload.get("course_id")

    if not student_id or not course_id:
        return jsonify({"error": "student_id and course_id are required"}), 400

    student = Student.query.filter_by(id=student_id).first()
    course = Course.query.filter_by(id=course_id, is_public=True).first()
    if not student or not course:
        return jsonify({"error": "Student or course not found"}), 404

    config = _momo_config()
    required_keys = ("partner_code", "access_key", "secret_key", "endpoint")
    if not all(config.get(k) for k in required_keys):
        return jsonify({"error": "Missing MoMo configuration in environment"}), 500

    invoice = _create_invoice(student, course, method="momo")

    order_id = f"{config['partner_code']}-{invoice.invoice_number}"
    request_id = str(int(time.time() * 1000))
    amount = str(int(Decimal(course.price or 0)))
    order_info = f"Thanh toan khoa hoc {course.title}"
    redirect_url = config["redirect_url"] or payload.get("redirect_url") or ""
    ipn_url = config["ipn_url"] or payload.get("ipn_url") or ""
    extra_data = ""

    raw_signature = (
        f"accessKey={config['access_key']}&amount={amount}&extraData={extra_data}"
        f"&ipnUrl={ipn_url}&orderId={order_id}&orderInfo={order_info}"
        f"&partnerCode={config['partner_code']}&redirectUrl={redirect_url}"
        f"&requestId={request_id}&requestType=captureWallet"
    )
    signature = _hmac_sha256(config["secret_key"], raw_signature)

    body = {
        "partnerCode": config["partner_code"],
        "partnerName": "CodeCourse",
        "storeId": "CodeCourse",
        "requestType": "captureWallet",
        "ipnUrl": ipn_url,
        "redirectUrl": redirect_url,
        "orderId": order_id,
        "amount": amount,
        "lang": "vi",
        "orderInfo": order_info,
        "requestId": request_id,
        "extraData": extra_data,
        "signature": signature,
    }

    try:
        response = requests.post(config["endpoint"], json=body, timeout=15)
        data = response.json()
    except Exception as exc:  # pragma: no cover - external call
        current_app.logger.error("MoMo create payment failed: %s", exc)
        db.session.rollback()
        return jsonify({"error": "Unable to create MoMo payment"}), 502

    if data.get("resultCode") != 0:
        db.session.rollback()
        return jsonify({"error": "MoMo rejected request", "details": data}), 400

    db.session.commit()
    return jsonify(
        {
          "payUrl": data.get("payUrl"),
          "deeplink": data.get("deeplink"),
          "qrCodeUrl": data.get("qrCodeUrl"),
          "invoice_number": invoice.invoice_number,
          "order_id": order_id,
          "amount": amount,
          "currency": course.currency or "VND",
        }
    )


def _verify_momo_signature(body: dict[str, Any], secret_key: str) -> bool:
    expected_fields = [
        "accessKey",
        "amount",
        "extraData",
        "message",
        "orderId",
        "orderInfo",
        "orderType",
        "partnerCode",
        "payType",
        "requestId",
        "responseTime",
        "resultCode",
        "transId",
    ]
    if not all(k in body for k in expected_fields + ["signature"]):
        return False
    raw = "&".join(f"{k}={body.get(k, '')}" for k in expected_fields)
    sig = _hmac_sha256(secret_key, raw)
    return sig == body.get("signature")


@payment_bp.post("/momo/webhook")
def momo_webhook():
    """Handle MoMo IPN to mark invoice paid and enroll student."""
    data = request.get_json(silent=True) or {}
    config = _momo_config()
    secret_key = config.get("secret_key")
    if not secret_key:
        return jsonify({"error": "Missing MoMo secret"}), 500

    order_id = data.get("orderId", "")
    invoice_number = order_id.split("-")[-1] if order_id else ""
    invoice = Invoice.query.filter_by(invoice_number=invoice_number).first()
    if not invoice:
        return jsonify({"error": "Invoice not found"}), 404

    if not _verify_momo_signature(data, secret_key):
        current_app.logger.warning("MoMo signature mismatch for invoice %s", invoice_number)
        return jsonify({"error": "invalid signature"}), 400

    if data.get("resultCode") == 0:
        invoice.payment_status = "paid"
        invoice.reference_code = str(data.get("transId"))
        invoice.paid_at = datetime.now(timezone.utc)
        invoice.updated_at = datetime.now(timezone.utc)
        _ensure_enrollment(invoice.student_id, invoice.course_id)
    else:
        invoice.payment_status = "failed"
        invoice.updated_at = datetime.now(timezone.utc)

    db.session.commit()
    return jsonify({"message": "ok"})

