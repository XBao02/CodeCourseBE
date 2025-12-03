"""Payment endpoints for MoMo and VietQR course purchases."""

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
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

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


def _create_invoice(
    student: Student,
    course: Course,
    method: str,
    reference: str | None = None,
    status: str = "pending",
) -> Invoice:
    invoice = Invoice(
        invoice_number=_generate_invoice_number(),
        student_id=student.id,
        course_id=course.id,
        amount=Decimal(course.price or 0),
        currency=course.currency or "VND",
        payment_method=method,
        payment_status=status,
        reference_code=reference,
        issued_at=datetime.now(timezone.utc),
    )
    db.session.add(invoice)
    db.session.flush()
    return invoice


def _vietqr_config() -> dict[str, str]:
    return {
        "account_name": _env("VIETQR_ACCOUNT_NAME", "LE DUC MANH"),
        "account_number": _env("VIETQR_ACCOUNT_NUMBER", "0901940996"),
        "bank_name": _env("VIETQR_BANK_NAME", "VietQR"),
        "bank_bin": _env("VIETQR_BANK_BIN", ""),
        "template": _env("VIETQR_TEMPLATE", "compact"),
        "qr_image_url": _env("VIETQR_IMAGE_URL", ""),
        "transfer_prefix": _env("VIETQR_TRANSFER_PREFIX", "CODECOURSE"),
        "currency": _env("VIETQR_CURRENCY", "VND"),
    }


def _vietqr_amount_url(config: dict[str, str], amount: Decimal, transfer_note: str) -> str:
    """
    Build dynamic VietQR link that embeds amount and content so người mua không phải nhập tay.
    Requires bank_bin + account_number.
    """
    if not config.get("bank_bin") or not config.get("account_number"):
        return config.get("qr_image_url", "")
    base = f"https://img.vietqr.io/image/{config['bank_bin']}-{config['account_number']}-{config.get('template','compact')}.png"
    params = {
        "amount": str(int(amount)),
        "addInfo": transfer_note,
        "accountName": config.get("account_name", ""),
    }
    from urllib.parse import urlencode
    return f"{base}?{urlencode(params)}"


def _build_transfer_note(prefix: str, invoice_number: str, course: Course) -> str:
    suffix = invoice_number[-6:] if invoice_number else uuid.uuid4().hex[:6]
    slug_part = (course.slug or course.title or "").replace(" ", "").upper()[:6]
    slug_part = slug_part or "COURSE"
    return f"{prefix}-{slug_part}-{suffix}"


def _serialize_student(student: Student) -> dict[str, Any]:
    user = getattr(student, "user", None)
    return {
        "id": student.id,
        "full_name": getattr(user, "full_name", "") or "",
        "email": getattr(user, "email", "") or "",
    }


def _serialize_course(course: Course) -> dict[str, Any]:
    return {
        "id": course.id,
        "title": course.title,
        "price": float(course.price or 0),
        "currency": course.currency or "VND",
    }


def _invoice_response(invoice: Invoice, student: Student, course: Course, extra: dict[str, Any]) -> dict[str, Any]:
    return {
        "invoice_number": invoice.invoice_number,
        "payment_method": invoice.payment_method,
        "payment_status": invoice.payment_status,
        "amount": float(invoice.amount or 0),
        "currency": invoice.currency,
        "course": _serialize_course(course),
        "student": _serialize_student(student),
        **extra,
    }


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
    """MoMo disabled: guide clients to use VietQR."""
    return jsonify({"error": "MoMo da tat. Vui long dung VietQR."}), 410

    # Legacy MoMo flow (kept for reference, currently disabled)
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
    """MoMo webhook disabled; use VietQR manual confirmation."""
    return jsonify({"error": "MoMo da tat. Khong tiep nhan webhook."}), 410

    # Legacy MoMo IPN (kept for reference, currently disabled)
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


@payment_bp.post("/vietqr/checkout")
def create_vietqr_checkout():
    """Create a VietQR invoice and return checkout details."""
    payload = request.get_json(silent=True) or {}
    student_id = payload.get("student_id")
    course_id = payload.get("course_id")

    # Try resolve student from JWT if not provided
    student = None
    if student_id:
        student = Student.query.filter_by(id=student_id).first()
    else:
        try:
            verify_jwt_in_request(optional=True)
            ident = get_jwt_identity()
            if ident:
                student = Student.query.filter_by(user_id=int(ident)).first()
        except Exception:
            student = None

    if not student or not course_id:
        return jsonify({"error": "student_id and course_id are required"}), 400

    course = Course.query.filter_by(id=course_id, is_public=True).first()
    if not student or not course:
        return jsonify({"error": "Student or course not found"}), 404

    config = _vietqr_config()
    existing_invoice = (
        Invoice.query.filter_by(student_id=student.id, course_id=course.id)
        .filter(Invoice.payment_status.in_(["pending"]))
        .order_by(Invoice.created_at.desc())
        .first()
    )

    if existing_invoice:
        invoice = existing_invoice
    else:
        transfer_note = _build_transfer_note(config["transfer_prefix"], "", course)
        invoice = _create_invoice(
            student,
            course,
            method="online",  # use allowed value to satisfy DB constraint
            reference=transfer_note,
            status="pending",
        )
        # Persist the generated note on the newly created invoice
        invoice.reference_code = _build_transfer_note(config["transfer_prefix"], invoice.invoice_number, course)
        db.session.flush()

    qr_with_amount = _vietqr_amount_url(config, invoice.amount or Decimal(0), invoice.reference_code or transfer_note)

    response = _invoice_response(
        invoice,
        student,
        course,
        {
            "account_name": config["account_name"],
            "account_number": config["account_number"],
            "bank_name": config["bank_name"],
            "qr_image_url": config["qr_image_url"],
            "qr_with_amount_url": qr_with_amount,
            "transfer_note": invoice.reference_code,
            "instructions": [
                "Quet ma VietQR bang ung dung ngan hang cua ban.",
                "Nhap dung so tien va noi dung chuyen khoan theo transfer_note.",
                "Nhan 'Toi da thanh toan' sau khi hoan tat de gui yeu cau xac nhan.",
            ],
        },
    )
    db.session.commit()
    return jsonify(response)


@payment_bp.post("/vietqr/confirm")
def confirm_vietqr_payment():
    """Mark a VietQR invoice as awaiting review after the student transfers."""
    payload = request.get_json(silent=True) or {}
    invoice_number = payload.get("invoice_number")
    transfer_reference = payload.get("transfer_reference")  # user-entered content/message

    if not invoice_number:
        return jsonify({"error": "invoice_number is required"}), 400

    invoice = Invoice.query.filter_by(invoice_number=invoice_number).first()
    if not invoice:
        return jsonify({"error": "Invoice not found"}), 404

    if invoice.payment_status == "paid":
        return jsonify({"message": "Invoice already paid", "status": invoice.payment_status})

    invoice.payment_status = "pending"
    if transfer_reference:
        invoice.reference_code = transfer_reference[:120]
    invoice.updated_at = datetime.now(timezone.utc)
    db.session.commit()

    student = Student.query.filter_by(id=invoice.student_id).first()
    course = Course.query.filter_by(id=invoice.course_id).first()
    if not student or not course:
        return jsonify({"message": "Invoice updated", "status": invoice.payment_status})

    config = _vietqr_config()
    return jsonify(
        _invoice_response(
            invoice,
            student,
            course,
            {
                "qr_image_url": config["qr_image_url"],
                "transfer_note": invoice.reference_code,
                "next_step": "Doi admin/CSKH xac nhan chuyen khoan va kich hoat khoa hoc.",
            },
        )
    )


@payment_bp.get("/vietqr/<invoice_number>")
def get_vietqr_invoice(invoice_number: str):
    """Fetch VietQR invoice details for polling checkout status."""
    invoice = Invoice.query.filter_by(invoice_number=invoice_number).first()
    if not invoice:
        return jsonify({"error": "Invoice not found"}), 404

    student = Student.query.filter_by(id=invoice.student_id).first()
    course = Course.query.filter_by(id=invoice.course_id).first()
    if not student or not course:
        return jsonify({"error": "Invoice data incomplete"}), 500

    config = _vietqr_config()
    return jsonify(
        _invoice_response(
            invoice,
            student,
            course,
            {
                "qr_image_url": config["qr_image_url"],
                "qr_with_amount_url": _vietqr_amount_url(config, invoice.amount or Decimal(0), invoice.reference_code or ""),
                "transfer_note": invoice.reference_code,
            },
        )
    )

