from app import create_app
from app.models import db

# Khởi tạo Flask app bằng factory
app = create_app()

def test_db_connection():
    """Hàm test kết nối database khi khởi động app."""
    try:
        with app.app_context():
            db.engine.connect()
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
    app.run(debug=True, port=5000)
