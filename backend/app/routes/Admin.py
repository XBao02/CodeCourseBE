from flask import Blueprint, jsonify, request
from db import get_db_connection
from decimal import Decimal
import datetime, sys

admin_bp = Blueprint('admin', __name__)

# Lấy danh sách khóa học
@admin_bp.route('/api/courses', methods=['GET'])
def get_courses():
    conn = get_db_connection()
    if not conn:
        return jsonify({"message": "Lỗi kết nối database"}), 500
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.Id, c.Title, c.Description, c.Price, u.FullName AS InstructorName
            FROM Courses c
            JOIN Instructors i ON c.InstructorId = i.Id
            JOIN Users u ON i.UserId = u.Id
            LIMIT 50
        """)
        cols = [i[0] for i in cursor.description]
        rows = cursor.fetchall()
        conn.close()
        courses = []
        for row in rows:
            data = dict(zip(cols, row))
            for k, v in data.items():
                if isinstance(v, Decimal): data[k] = float(v)
            courses.append(data)
        return jsonify({"courses": courses})
    except Exception as e:
        print("❌ Lỗi lấy khóa học:", e, file=sys.stderr)
        return jsonify({"message": "Lỗi server"}), 500

# Báo cáo dashboard
@admin_bp.route('/api/reports/summary', methods=['GET'])
def get_summary():
    conn = get_db_connection()
    if not conn:
        return jsonify({"message": "Lỗi kết nối database"}), 500
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(Id) FROM Users")
        total_users = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(Id) FROM Students")
        total_students = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(Id) FROM Instructors")
        total_instructors = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(Id) FROM Courses")
        total_courses = cursor.fetchone()[0]

        conn.close()
        return jsonify({
            "totalUsers": total_users,
            "totalStudents": total_students,
            "totalInstructors": total_instructors,
            "totalCourses": total_courses,
            "reportDate": datetime.datetime.now().isoformat()
        })
    except Exception as e:
        print("❌ Lỗi báo cáo:", e, file=sys.stderr)
        return jsonify({"message": "Lỗi server"}), 500
