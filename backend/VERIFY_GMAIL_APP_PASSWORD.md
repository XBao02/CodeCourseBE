# ✅ Cách Kiểm Tra và Tạo Gmail App Password Đúng

## Bước 1: Kiểm tra 2FA đã bật chưa
1. Mở: https://myaccount.google.com/security
2. Tìm **"2-Step Verification"** (Xác minh 2 bước)
3. Phải có trạng thái **"ON"** (Đã bật)
4. Nếu chưa bật → Bật lên trước

## Bước 2: Tạo App Password MỚI
1. Mở: https://myaccount.google.com/apppasswords
2. Nếu không thấy trang này:
   - Kiểm tra 2FA đã bật chưa (Bước 1)
   - Hoặc tìm "App passwords" trong Security settings
3. Click **"Select app"** → Chọn **"Other"** (Custom name)
4. Nhập tên: `CodeCourse Backend`
5. Click **"Generate"**

## Bước 3: Copy App Password
**App Password sẽ hiển thị 1 LẦN DUY NHẤT:**
```
abcd efgh ijkl mnop
```
- Đây là 16 ký tự (có dấu cách để dễ đọc)
- **COPY NGAY** vào Notepad
- Khi dán vào `.env`, **XÓA TẤT CẢ DẤU CÁCH**:
  ```
  SMTP_PASSWORD=abcdefghijklmnop
  ```

## Bước 4: Cập nhật .env
```properties
SMTP_EMAIL=captone149@gmail.com
SMTP_PASSWORD=abcdefghijklmnop  # ← 16 ký tự, KHÔNG CÓ DẤU CÁCH

GMAIL_USER=captone149@gmail.com
GMAIL_APP_PASSWORD=abcdefghijklmnop  # ← Giống như trên
```

## ⚠️ LƯU Ý QUAN TRỌNG:

### App Password PHẢI:
- ✅ 16 ký tự (a-z, không có số hoặc ký tự đặc biệt trong ví dụ của Google)
- ✅ Vừa mới tạo (không dùng code cũ)
- ✅ Copy chính xác (không thêm/bớt ký tự)

### App Password KHÔNG PHẢI:
- ❌ Mật khẩu Gmail thường của bạn
- ❌ Token hay API key khác
- ❌ Một chuỗi bạn tự nghĩ ra

## Bước 5: Test
Sau khi cập nhật `.env`:
1. **Khởi động lại backend:**
   ```powershell
   cd d:\UnityProject\CodeCourseBE\backend
   python app.py
   ```

2. **Test gửi OTP:**
   - Mở frontend
   - Vào trang Register
   - Nhập email và click "Send OTP"
   - Kiểm tra email (cả Inbox và Spam)

## 🚨 Nếu vẫn lỗi "Username and Password not accepted":

### Nguyên nhân thường gặp:
1. **App Password SAI** (phổ biến nhất)
   - Đã copy sai
   - Còn dấu cách
   - Dùng mật khẩu thường thay vì App Password

2. **Tài khoản Google bị khóa tạm thời**
   - Google phát hiện đăng nhập bất thường
   - Giải pháp: https://accounts.google.com/DisplayUnlockCaptcha

3. **2FA chưa bật đúng cách**
   - Phải bật 2FA xong mới tạo App Password được

4. **Less Secure Apps bị chặn**
   - Google đã tắt tính năng này từ 2022
   - PHẢI dùng App Password

## 🔧 Debug Step-by-Step:

### Test 1: Kiểm tra format App Password
```python
# Chạy trong Python shell
password = "frugixmwlpjmwpf"
print(f"Length: {len(password)}")  # Phải = 16
print(f"Has spaces: {' ' in password}")  # Phải = False
print(f"Password: {password}")  # In ra để kiểm tra
```

### Test 2: Tạo App Password MỚI
- Xóa App Password cũ nếu có
- Tạo App Password mới
- Copy cẩn thận (dùng Ctrl+C, không gõ tay)

### Test 3: Test SMTP trực tiếp
Tạo file `test_smtp_direct.py`:
```python
import smtplib

email = "captone149@gmail.com"
password = "frugixmwlpjmwpf"  # ← App Password của bạn

try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(email, password)
    print("✅ Login thành công!")
    server.quit()
except Exception as e:
    print(f"❌ Lỗi: {e}")
```

Chạy:
```powershell
cd d:\UnityProject\CodeCourseBE\backend
python test_smtp_direct.py
```

## 📧 Email hỗ trợ từ Google:
Nếu vẫn không được, kiểm tra email từ Google:
- "Critical security alert"
- "Unusual sign-in activity"
- Theo link trong email để cho phép truy cập

## ✅ Khi nào coi như THÀNH CÔNG?
- Backend không báo lỗi khi gửi OTP
- Email OTP xuất hiện trong Inbox (hoặc Spam)
- Console log hiển thị: "OTP sent successfully"
