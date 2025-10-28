from flask import Blueprint, jsonify, request
import mysql.connector

# Tạo Blueprint cho module sinh viên
student_bp = Blueprint('student', __name__)

# Hàm kết nối MySQL
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="your_database_name",
    )

# ===============================
# 🧠 API DASHBOARD SINH VIÊN
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
