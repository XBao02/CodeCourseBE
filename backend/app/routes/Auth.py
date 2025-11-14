from flask import Blueprint, request, jsonify
from sqlalchemy import text
from app.utils.db import engine
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)
from werkzeug.security import check_password_hash, generate_password_hash
import bcrypt   # dùng nếu bạn đã lưu hash bằng bcrypt
import re

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

def _fetch_user_by_email(email: str):
    # Đồng bộ theo schema bảng Users (viết hoa) và cột PascalCase
    sql = (
        """
        SELECT
            Id AS id,
            Email AS email,
            PasswordHash AS password_hash,
            NULL AS password
        FROM Users
        WHERE Email = :email
        LIMIT 1
        """
    )
    with engine.begin() as conn:
        row = conn.execute(text(sql), {"email": email}).mappings().first()
    return row

def _valid_email(email: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", (email or "").strip()))

@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    full_name = (data.get("full_name") or data.get("fullname") or "").strip()
    role = (data.get("role") or "student").strip().lower()

    if not _valid_email(email):
        return jsonify({"error": "Email không hợp lệ"}), 400
    if len(password) < 6:
        return jsonify({"error": "Mật khẩu tối thiểu 6 ký tự"}), 400
    if role not in ("student", "instructor", "admin"):
        return jsonify({"error": "Role không hợp lệ"}), 400

    pwd_hash = generate_password_hash(password)

    with engine.begin() as conn:
        # Check duplicate
        exists = conn.execute(text("SELECT 1 FROM Users WHERE Email=:email LIMIT 1"), {"email": email}).scalar()
        if exists:
            return jsonify({"error": "Email đã tồn tại"}), 409

        user_id = None
        # Try verbose insert (email, password_hash, full_name, role)
        try:
            res = conn.execute(
                text(
                    """
                    INSERT INTO Users (Email, PasswordHash, FullName, Role)
                    VALUES (:email, :password_hash, :full_name, :role)
                    """
                ),
                {"email": email, "password_hash": pwd_hash, "full_name": full_name, "role": role},
            )
            user_id = res.lastrowid or res.inserted_primary_key[0]
        except Exception:
            # Fallback minimal columns
            res = conn.execute(
                text(
                    """
                    INSERT INTO Users (Email, PasswordHash)
                    VALUES (:email, :password_hash)
                    """
                ),
                {"email": email, "password_hash": pwd_hash},
            )
            user_id = res.lastrowid or res.inserted_primary_key[0]

        # Try create role-row if sub-tables exist
        role_table = {"student": "Students", "instructor": "Instructors", "admin": "Admins"}[role]
        try:
            conn.execute(text(f"INSERT INTO {role_table} (UserId) VALUES (:uid)"), {"uid": user_id})
        except Exception:
            pass  # ignore if table/column not exist

    access_token = create_access_token(identity={"user_id": user_id, "role": role})
    return jsonify({
        "access_token": access_token,
        "user": {"id": user_id, "email": email, "role": role, "full_name": full_name},
    }), 201

@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email và password là bắt buộc"}), 400

    user = _fetch_user_by_email(email)
    if not user:
        return jsonify({"error": "Sai email hoặc mật khẩu"}), 401

    ok = False
    # ƯU TIÊN: password_hash (pbkdf2/bcrypt). DỰ PHÒNG: plain text 'password'
    if user.get("password_hash"):
        try:
            ok = check_password_hash(user["password_hash"], password)
        except Exception:
            # trường hợp bạn đã hash bằng bcrypt thủ công:
            try:
                ok = bcrypt.checkpw(password.encode("utf-8"),
                                    user["password_hash"].encode("utf-8"))
            except Exception:
                ok = False
    elif user.get("password"):
        ok = (password == user["password"])

    if not ok:
        return jsonify({"error": "Sai email hoặc mật khẩu"}), 401

    from app.routes import resolve_role  # Lazy import to avoid circular dependency
    role = resolve_role(user["id"])
    access_token = create_access_token(identity={"user_id": user["id"], "role": role})

    return jsonify({
        "access_token": access_token,
        "user": {"id": user["id"], "email": user["email"], "role": role}
    })

@auth_bp.get("/me")
@jwt_required()
def me():
    ident = get_jwt_identity()
    # đồng bộ role mới nhất
    from app.routes import resolve_role  # Lazy import to avoid circular dependency
    current_role = resolve_role(ident["user_id"])
    return jsonify({"user": {**ident, "role": current_role}})

@auth_bp.post("/logout")
@jwt_required()
def logout():
    # Với JWT stateless, FE chỉ cần xoá token.
    # Nếu muốn blocklist, bạn có thể lưu jti vào DB/Redis tại đây.
    return jsonify({"message": "Logged out (client remove token)"}), 200
 

