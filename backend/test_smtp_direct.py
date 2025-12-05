"""
Test SMTP Gmail connection trực tiếp
Dùng để kiểm tra App Password có đúng không
"""
import smtplib
from email.mime.text import MIMEText

# ❌ App Password SAI - "svgd iram ifdl itih" không phải App Password thật
# ✅ App Password phải là 16 ký tự liền, không có dấu cách
# Ví dụ: "abcdefghijklmnop" hoặc "xyzw1234abcd5678"

email = "captone149@gmail.com"
# Thay "your_app_password_here" bằng App Password 16 ký tự từ Google
app_password = "svgdiramifdlitih"  # ← XÓA DẤU CÁCH: svgd iram ifdl itih → svgdiramitih

print("=" * 60)
print("🔍 KIỂM TRA GMAIL APP PASSWORD")
print("=" * 60)
print(f"\n📧 Email: {email}")
print(f"🔑 App Password: {app_password}")
print(f"📏 Độ dài: {len(app_password)} ký tự (phải = 16)")
print(f"🚫 Có dấu cách: {' ' in app_password}")

if len(app_password) != 16:
    print("\n❌ LỖI: App Password phải có ĐÚNG 16 ký tự!")
    print("⚠️  Đây không phải App Password thật từ Google")
    print("\n📝 Cách lấy App Password ĐÚNG:")
    print("1. Vào: https://myaccount.google.com/apppasswords")
    print("2. Tạo App Password mới")
    print("3. Google sẽ hiển thị: 'abcd efgh ijkl mnop'")
    print("4. Copy và XÓA DẤU CÁCH: 'abcdefghijklmnop'")
    print("5. Dán vào file này và .env")
    exit(1)

if ' ' in app_password:
    print("\n❌ LỖI: App Password KHÔNG được có dấu cách!")
    print(f"⚠️  Bạn nhập: '{app_password}'")
    print(f"✅ Phải là: '{app_password.replace(' ', '')}'")
    exit(1)

print("\n🔄 Đang kết nối SMTP Gmail...\n")

try:
    # Kết nối SMTP
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.set_debuglevel(1)  # Hiển thị log chi tiết
    
    print("\n🔐 Đang bật TLS...\n")
    server.starttls()
    
    print("\n🔑 Đang đăng nhập...\n")
    server.login(email, app_password)
    
    print("\n" + "=" * 60)
    print("✅ THÀNH CÔNG! App Password ĐÚNG!")
    print("=" * 60)
    print("\n📌 Bây giờ cập nhật vào file .env:")
    print(f"   SMTP_EMAIL={email}")
    print(f"   SMTP_PASSWORD={app_password}")
    print(f"   GMAIL_USER={email}")
    print(f"   GMAIL_APP_PASSWORD={app_password}")
    
    # Test gửi email
    print("\n📨 Test gửi email OTP...\n")
    
    msg = MIMEText("Đây là email test từ CodeCourse Backend.\n\nMã OTP của bạn: 123456")
    msg['Subject'] = 'Test Email - CodeCourse OTP'
    msg['From'] = email
    msg['To'] = email  # Gửi cho chính mình để test
    
    server.send_message(msg)
    print(f"✅ Đã gửi email test đến {email}")
    print("📬 Kiểm tra hộp thư của bạn (cả Inbox và Spam)")
    
    server.quit()
    
    print("\n" + "=" * 60)
    print("✅ TẤT CẢ ĐỀU HOẠT ĐỘNG!")
    print("=" * 60)
    
except smtplib.SMTPAuthenticationError as e:
    print("\n" + "=" * 60)
    print("❌ LỖI ĐĂNG NHẬP - App Password SAI!")
    print("=" * 60)
    print(f"\nChi tiết lỗi: {e}")
    print("\n🔧 NGUYÊN NHÂN:")
    print("1. ❌ App Password không đúng (phổ biến nhất)")
    print("2. ❌ Chưa bật 2-Step Verification")
    print("3. ❌ Dùng mật khẩu Gmail thường thay vì App Password")
    print("4. ❌ Tài khoản bị khóa tạm thời")
    
    print("\n🔍 GIẢI PHÁP:")
    print("1. Kiểm tra 2FA: https://myaccount.google.com/security")
    print("2. Tạo App Password MỚI: https://myaccount.google.com/apppasswords")
    print("3. Copy CHÍNH XÁC 16 ký tự (xóa dấu cách)")
    print("4. Unlock account: https://accounts.google.com/DisplayUnlockCaptcha")
    
except Exception as e:
    print("\n" + "=" * 60)
    print("❌ LỖI KẾT NỐI")
    print("=" * 60)
    print(f"\nChi tiết: {e}")
    print("\n🔧 Kiểm tra:")
    print("1. Kết nối Internet")
    print("2. Firewall/Antivirus chặn port 587")
    print("3. Gmail có bị khóa không")
