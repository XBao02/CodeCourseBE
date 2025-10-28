import unittest
import json
from datetime import datetime
from run import app 
from app.models.model import db, Course, Instructor, User 
from config import MYSQL_CONN 

# ==================================
# Base Test Case cho Integration Test
# ==================================
class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        
        # SỬ DỤNG DATABASE THẬT: Ghi đè cấu hình DB bằng cấu hình MySQL thật
        self.app.config['SQLALCHEMY_DATABASE_URI'] = MYSQL_CONN 
        self.client = self.app.test_client()

        with self.app.app_context():
            # db.init_app(self.app)  <-- Bỏ dòng này
            db.session.remove()
            # KHÔNG TẠO/XÓA BẢNG: Chỉ test dữ liệu hiện có.

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()

# ==================================
# Test Case cho API Khóa học
# ==================================
class CourseAPITestCase(BaseTestCase):
    
    def test_get_courses_by_instructor_id_2(self):
        """Kiểm tra lấy đúng khóa học của Giảng viên ID 2."""
        
        response = self.client.get('/api/courses?instructor_id=2')
        
        # Kiểm tra Status Code phải là 200 (vì route đã được đăng ký)
        self.assertEqual(response.status_code, 200) 
        
        self.assertEqual(response.content_type, 'application/json')
        data = json.loads(response.data.decode('utf-8'))
        
        # Tiếp tục các assertion khác dựa trên DỮ LIỆU THẬT trong DB của bạn.
        self.assertGreaterEqual(len(data), 1, "Phải có ít nhất 1 khóa học cho instructor 2.")
        
    def test_get_courses_by_instructor_id_invalid(self):
        # ... (Test này sẽ chạy OK sau khi loại bỏ db.init_app) ...
        response = self.client.get('/api/courses?instructor_id=999')
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 0)

    def test_get_courses_missing_id(self):
        # ... (Test này sẽ chạy OK sau khi loại bỏ db.init_app) ...
        response = self.client.get('/api/courses')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn("Thiếu tham số instructor_id", data['message'])

if __name__ == '__main__':
    unittest.main()