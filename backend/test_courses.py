"""
Script để kiểm tra số lượng khóa học trong database
"""
from app import create_app
from app.models.model import Course, Instructor, User
from app.models import db

app = create_app()

with app.app_context():
    # Đếm số khóa học
    total_courses = Course.query.count()
    print(f"📊 Tổng số khóa học trong database: {total_courses}")
    
    # Liệt kê các khóa học
    courses = Course.query.all()
    if courses:
        print("\n📚 Danh sách khóa học:")
        for i, course in enumerate(courses, 1):
            instructor = Instructor.query.get(course.instructor_id)
            instructor_name = instructor.user.full_name if instructor and instructor.user else "N/A"
            print(f"{i}. {course.title}")
            print(f"   - ID: {course.id}")
            print(f"   - Instructor: {instructor_name}")
            print(f"   - Level: {course.level}")
            print(f"   - Price: {course.price} {course.currency}")
            print(f"   - Public: {course.is_public}")
            print()
    else:
        print("\n⚠️ Không có khóa học nào trong database!")
        print("\n💡 Để tạo khóa học mẫu, bạn cần:")
        print("1. Đăng nhập với tài khoản Instructor")
        print("2. Vào trang Instructor/Courses")
        print("3. Tạo khóa học mới")
