from flask import Flask
from flask_cors import CORS
from app.routes import student_bp, auth_bp, admin_bp, instructor_bp
from app.models import db
from config import MYSQL_CONN
def create_app():
    app = Flask(__name__)
    
    # Cấu hình CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Cấu hình Database
    app.config['SQLALCHEMY_DATABASE_URI'] = MYSQL_CONN
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Khởi tạo SQLAlchemy với app
    db.init_app(app)
    
    # Đăng ký các blueprint
    app.register_blueprint(student_bp, url_prefix="/api/student")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(instructor_bp, url_prefix="/api/instructor")

    return app
