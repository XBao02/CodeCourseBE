from flask import Blueprint, request, jsonify
from db import get_db_connection
import bcrypt, datetime, sys

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    fullName = data.get('fullName')
    role = data.get('role')

    if role not in ['student', 'instructor']:
        return jsonify({"message": "Vai trò người dùng không hợp lệ"}), 400
    if not email or not password or not fullName:
        return jsonify({"message": "Thiếu thông tin"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"message": "Lỗi kết nối database"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT Id FROM Users WHERE Email = %s", (email,))
        if cursor.fetchone():
            conn.close()
            return jsonify({"message": "Email đã tồn tại"}), 409

        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        now = datetime.datetime.now()

        cursor.execute("""
            INSERT INTO Users (Email, PasswordHash, FullName, Role, IsActive, CreatedAt, UpdatedAt)
            VALUES (%s, %s, %s, %s, TRUE, %s, %s)
        """, (email, hashed, fullName, role, now, now))

        new_id = cursor.lastrowid
        if role == 'student':
            cursor.execute("INSERT INTO Students (UserId, CreatedAt, UpdatedAt) VALUES (%s, %s, %s)", (new_id, now, now))
        else:
            cursor.execute("INSERT INTO Instructors (UserId, CreatedAt, UpdatedAt) VALUES (%s, %s, %s)", (new_id, now, now))

        conn.commit()
        conn.close()
        return jsonify({"message": "Đăng ký thành công", "userId": new_id}), 201
    except Exception as e:
        print("❌ Lỗi đăng ký:", e, file=sys.stderr)
        return jsonify({"message": "Lỗi server"}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({"message": "Thiếu email hoặc mật khẩu"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"message": "Lỗi kết nối database"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT Id, FullName, Role, PasswordHash FROM Users WHERE Email = %s", (email,))
        user = cursor.fetchone()
        conn.close()

        if not user:
            return jsonify({"message": "Email hoặc mật khẩu sai"}), 401

        user_id, fullname, role, hashed = user
        if bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8')):
            return jsonify({
                "message": "Đăng nhập thành công",
                "user": {"Id": user_id, "FullName": fullname, "Email": email, "Role": role}
            }), 200
        else:
            return jsonify({"message": "Email hoặc mật khẩu sai"}), 401
    except Exception as e:
        print("❌ Lỗi đăng nhập:", e, file=sys.stderr)
        return jsonify({"message": "Lỗi server"}), 500
