# run.py (Cấu trúc lý tưởng)
from flask import Flask
from flask_cors import CORS
# ... (Các imports khác)
from app.routes.Instructor import instructor_bp 
from app.models.model import db 
from config import MYSQL_CONN 

app = Flask(__name__)

CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})
# CẤU HÌNH DB
app.config['SQLALCHEMY_DATABASE_URI'] = MYSQL_CONN
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ************ ĐẢM BẢO DÒNG NÀY ĐƯỢC GỌI ************
# Đăng ký Blueprint để các routes có sẵn khi test.py import run.py
app.register_blueprint(instructor_bp, url_prefix='/api') 
# ****************************************************

db.init_app(app) 

# ... (các hàm khác) ...

if __name__ == "__main__":
    app.run(debug=True)