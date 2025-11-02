from flask import Blueprint, jsonify, request
import MYSQL_CONN
import os
import json

# Tạo Blueprint cho module sinh viên
student_bp = Blueprint('student', __name__)

# File tạm lưu thông tin hồ sơ (không đụng DB)
PROFILE_FILE = "student_profiles.json"

# ===============================
# 🔗 Hàm kết nối MySQL
# ===============================
def get_db_connection():
    return MYSQL_CONN.connect(
        host="localhost",
        user="root",
        password="",
        database="your_database_name",
    )


# ===============================
# 🧭 DASHBOARD SINH VIÊN
# ===============================

# Lấy danh sách sinh viên
@student_bp.route('/students', methods=['GET'])
def get_students():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, email, major, created_at FROM students")
        students = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({"status": "success", "data": students}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# Thêm sinh viên mới
@student_bp.route('/students', methods=['POST'])
def add_student():
    try:
        data = request.json
        name = data.get("name")
        email = data.get("email")
        major = data.get("major")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO students (name, email, major) VALUES (%s, %s, %s)",
            (name, email, major),
        )
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"status": "success", "message": "Student added successfully!"}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# Xem thông tin chi tiết 1 sinh viên
@student_bp.route('/students/<int:id>', methods=['GET'])
def get_student(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM students WHERE id = %s", (id,))
        student = cursor.fetchone()
        cursor.close()
        conn.close()
        if not student:
            return jsonify({"status": "error", "message": "Student not found"}), 404
        return jsonify({"status": "success", "data": student}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# Cập nhật thông tin sinh viên
@student_bp.route('/students/<int:id>', methods=['PUT'])
def update_student(id):
    try:
        data = request.json
        name = data.get("name")
        email = data.get("email")
        major = data.get("major")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE students SET name=%s, email=%s, major=%s WHERE id=%s",
            (name, email, major, id),
        )
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"status": "success", "message": "Student updated successfully!"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# Xóa sinh viên
@student_bp.route('/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM students WHERE id=%s", (id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"status": "success", "message": "Student deleted successfully!"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ===============================
# 👤 API HỒ SƠ SINH VIÊN (Profile)
# ===============================

# Đọc dữ liệu hồ sơ từ file JSON (tạm)
def load_profiles():
    if not os.path.exists(PROFILE_FILE):
        return {}
    with open(PROFILE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# Ghi dữ liệu hồ sơ vào file JSON
def save_profiles(profiles):
    with open(PROFILE_FILE, "w", encoding="utf-8") as f:
        json.dump(profiles, f, ensure_ascii=False, indent=4)


# Lấy hồ sơ sinh viên
@student_bp.route('/students/<int:id>/profile', methods=['GET'])
def get_student_profile(id):
    try:
        # Lấy dữ liệu sinh viên cơ bản
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, email, major FROM students WHERE id = %s", (id,))
        student = cursor.fetchone()
        cursor.close()
        conn.close()

        if not student:
            return jsonify({"status": "error", "message": "Student not found"}), 404

        # Lấy thông tin profile tạm từ file JSON
        profiles = load_profiles()
        profile_data = profiles.get(str(id), {
            "dob": None,
            "phone": None,
            "address": None,
            "photo": None
        })

        # Gộp dữ liệu trả về
        student.update(profile_data)
        student["courses"] = [
            {"id": 1, "title": "Frontend Development", "progress": 75},
            {"id": 2, "title": "Database Management", "progress": 50},
            {"id": 3, "title": "Backend Development", "progress": 20},
        ]

        return jsonify({"status": "success", "data": student}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# Cập nhật hồ sơ sinh viên (tạm)
@student_bp.route('/students/<int:id>/profile', methods=['PUT'])
def update_student_profile(id):
    try:
        data = request.json
        profiles = load_profiles()

        profiles[str(id)] = {
            "dob": data.get("dob"),
            "phone": data.get("phone"),
            "address": data.get("address"),
            "photo": data.get("photo")
        }

        save_profiles(profiles)
        return jsonify({"status": "success", "message": "Profile updated successfully!"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# Upload ảnh hồ sơ (tạm)
@student_bp.route('/students/<int:id>/photo', methods=['POST'])
def upload_student_photo(id):
    try:
        file = request.files.get("photo")
        if not file:
            return jsonify({"status": "error", "message": "No file uploaded"}), 400

        upload_folder = "static/uploads"
        os.makedirs(upload_folder, exist_ok=True)

        filename = f"student_{id}.jpg"
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)

        profiles = load_profiles()
        if str(id) not in profiles:
            profiles[str(id)] = {}
        profiles[str(id)]["photo"] = f"/{file_path}"
        save_profiles(profiles)

        return jsonify({
            "status": "success",
            "message": "Photo uploaded successfully!",
            "photo_url": f"/{file_path}"
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
