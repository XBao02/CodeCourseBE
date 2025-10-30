from flask import Blueprint, jsonify
from db import get_db_connection
import sys

# Tạo Blueprint cho Instructor Reports
instructor_bp = Blueprint('instructor', __name__)

# ✅ Lấy danh sách khóa học của giảng viên
@instructor_bp.route('/api/instructor/<int:instructor_id>/courses', methods=['GET'])
def get_instructor_courses(instructor_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"message": "Lỗi kết nối database"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                c.Id, 
                c.Title, 
                c.Price, 
                c.CreatedAt,
                (SELECT COUNT(*) FROM Enrollments e WHERE e.CourseId = c.Id) AS StudentCount
            FROM Courses c
            WHERE c.InstructorId = %s
        """, (instructor_id,))
        columns = [col[0] for col in cursor.description]
        data = cursor.fetchall()
        conn.close()

        courses = [dict(zip(columns, row)) for row in data]
        return jsonify(courses)
    except Exception as e:
        print("❌ Lỗi lấy khóa học giảng viên:", e, file=sys.stderr)
        return jsonify({"message": "Lỗi server"}), 500


# ✅ Lấy thống kê báo cáo giảng viên
@instructor_bp.route('/api/instructor/<int:instructor_id>/reports', methods=['GET'])
def get_instructor_reports(instructor_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"message": "Lỗi kết nối database"}), 500

    try:
        cursor = conn.cursor()

        # Tổng số khóa học
        cursor.execute("SELECT COUNT(*) FROM Courses WHERE InstructorId = %s", (instructor_id,))
        total_courses = cursor.fetchone()[0]

        # Tổng số học viên đăng ký trong tất cả các khóa học của giảng viên
        cursor.execute("""
            SELECT COUNT(*) 
            FROM Enrollments e 
            INNER JOIN Courses c ON e.CourseId = c.Id 
            WHERE c.InstructorId = %s
        """, (instructor_id,))
        total_students = cursor.fetchone()[0]

        # Tổng doanh thu (nếu có bảng Enrollments.Price hoặc Courses.Price)
        cursor.execute("""
            SELECT COALESCE(SUM(c.Price), 0)
            FROM Enrollments e
            INNER JOIN Courses c ON e.CourseId = c.Id
            WHERE c.InstructorId = %s
        """, (instructor_id,))
        total_revenue = cursor.fetchone()[0]

        conn.close()

        return jsonify({
            "total_courses": total_courses,
            "total_students": total_students,
            "total_revenue": total_revenue
        })
    except Exception as e:
        print("❌ Lỗi lấy báo cáo giảng viên:", e, file=sys.stderr)
        return jsonify({"message": "Lỗi server"}), 500
