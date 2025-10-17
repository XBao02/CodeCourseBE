from flask import Flask
from sqlalchemy import create_engine
from config import MYSQL_CONN

app = Flask(__name__)

# Tạo engine kết nối MySQL
engine = create_engine(MYSQL_CONN)

def test_db_connection():
    """Hàm test kết nối database khi khởi động app."""
    try:
        with engine.connect() as conn:
            print("✅ Kết nối MySQL thành công!")
    except Exception as e:
        print("❌ Lỗi kết nối MySQL:")
        print(e)
        exit(1)  # Dừng chương trình nếu không kết nối được

# Gọi test kết nối khi app khởi động
test_db_connection()

@app.route("/")
def home():
    return "Server đang chạy và đã kết nối DB thành công!"

if __name__ == "__main__":
    app.run(debug=True)
