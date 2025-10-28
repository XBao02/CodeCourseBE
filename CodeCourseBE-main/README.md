# CodeCourseBE 🎓

## Giới thiệu
**CodeCourseBE** là dự án quản lý khóa học trực tuyến, gồm **backend** và **frontend**.  
Mục tiêu: xây dựng hệ thống cho phép quản lý khóa học, giảng viên, học viên và nội dung bài giảng.

## Cấu trúc thư mục
backend/
│
└── app/
    ├── models/                        # Chứa các model ORM (SQLAlchemy, peewee, v.v.)
    │   ├── __init__.py                 # Dùng để khai báo package + import model vào đây
    │   # Ví dụ: user.py, course.py → ánh xạ bảng users, courses trong DB
    │
    ├── routes/                        # Định nghĩa API endpoint (controller)
    │   ├── Admin/                      # API cho admin (quản lý user, course, thống kê...)
    │   ├── Auth/                       # API cho login, register, refresh token
    │   ├── Instructor/                 # API cho giảng viên (quản lý khóa học, tạo bài giảng...)
    │   └── Student/                    # API cho sinh viên (đăng ký khóa học, làm bài test...)
    │   # Mỗi folder có __init__.py + file route riêng (VD: admin_routes.py)
    │
    ├── services/                      # Business logic (xử lý nghiệp vụ, tách khỏi routes)
    │   ├── AI/                         # Thư mục xử lý AI (VD: YOLOv8 training, CV scan, chatbot)
    │   └── recommender.py              # Service gợi ý khóa học/lộ trình học
    │
    ├── utils/                         # Các tiện ích dùng chung (helper)
    │   ├── __init__.py                 # Khai báo package
    │   └── db.py                       # Kết nối database (SQLAlchemy, session, Base)
    │   # Có thể thêm: security.py (JWT, hash mật khẩu), helpers.py (format data)
    │
    ├── __init__.py                    # Biến thư mục app thành Python package
    │                                   # Thường để khởi tạo Flask app/FastAPI, load config
    │
    ├── app.py                         # File chính chạy server
    │                                   # - Khởi tạo app Flask/FastAPI
    │                                   # - Gắn routes
    │                                   # - Middleware (CORS, logging, auth)
    │
    ├── config.py                      # Cấu hình ứng dụng
    │                                   # - DB_URL (MySQL/Postgres/SQLite)
    │                                   # - SECRET_KEY, JWT_EXPIRE
    │                                   # - Debug/Production config
    │
    └── requirements.txt               # Danh sách package Python cần cài
                                        # Ví dụ: flask, fastapi, sqlalchemy, uvicorn, bcrypt, pydantic
                                        
fe/                             # Thư mục gốc của frontend project
│── .vscode/                    # Cấu hình riêng cho VS Code (extension, setting, debug)
│── node_modules/               # Thư viện cài đặt bởi npm/yarn (tự sinh ra, không commit)
│── public/                     # Chứa file tĩnh (ảnh)
│
├── src/                        # Source code chính của ứng dụng Vue
│   ├── assets/                 # Tài nguyên tĩnh: ảnh, font, icon, style dùng chung
│   │
│   ├── components/             # Component tái sử dụng chung
│   │
│   ├── Admin/                  # Module/Component dành cho Admin (giao diện quản trị)
│   ├── common/                 # Component dùng avatar
│   ├── Instructor/             # Module/Component dành cho Giảng viên
│   ├── Student/                # Module/Component dành cho Sinh viên
│   ├── User/                   # Module/Component dành cho User Đăng kí, đăng nhập
│   │
│   ├── layout/                 # Quản lý layout tổng thể
│   │   ├── components/         # Component nhỏ trong layout (VD: Sidebar, Navbar)
│   │   └── wrapper/            # Wrapper layout cho từng vai trò (MenuAdmin, MenuStudent...)
│   │
│   ├── router/                 # Cấu hình router Vue (định nghĩa các route)
│   │   └── index.js            # File chính chứa router config
│   │
│   ├── App.vue                 # Root component (nơi mount toàn bộ app)
│   ├── main.js                 # Điểm khởi chạy ứng dụng Vue (tạo app, mount vào DOM)
│   └── style.css               # File CSS chung (global style)
│
│── .gitignore                  # Quy định file/thư mục bị bỏ qua khi commit git
│── index.html                  # File HTML gốc, nơi mount ứng dụng Vue
│── package.json                # Khai báo package, script, metadata của project
│── package-lock.json           # Lock version thư viện để đảm bảo đồng nhất
│── README.md                   # File hướng dẫn dự án
│── vite.config.js              # Cấu hình Vite (bundler cho Vue project)


---

##  Công nghệ sử dụng
- **Backend**  
  - [Python 3.x](https://www.python.org/)  
  - [Flask](https://flask.palletsprojects.com/) – Web framework  
  - [SQL Server](https://www.microsoft.com/en-us/sql-server) – Cơ sở dữ liệu  

- **Frontend**  
  - [Vue.js 3](https://vuejs.org/)  
  - [Vite](https://vitejs.dev/)  
  - [Axios](https://axios-http.com/)  

---

##  Cài đặt và chạy dự án

### 1. Clone repo
--bash
git clone https://github.com/XBao02/CodeCourseBE.git
cd CodeCourseBE

--môi trường be 
cd backend
python -m venv venv
venv\Scripts\activate     # Windows
# hoặc
source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt

-- chạy Flask server
cd backend 
python app.py
-- chạy fe 
cd fe
npm install
npm run dev








