# 🔐 Quick Start: Password Reset Email

## ✅ Đã Hoàn Thành

1. ✅ Thêm hàm `send_reset_password_email()` vào Auth.py
2. ✅ Cập nhật endpoint `/forgot-password` để gửi email
3. ✅ Cấu hình SMTP trong .env
4. ✅ Tạo script test

## 🚀 Cách Sử Dụng

### 1. Đảm bảo Backend đang chạy

```bash
cd backend
python app.py
```

### 2. Test Email Sending

```bash
cd backend
python test_reset_password_email.py
```

**Output mong đợi:**
```
✅ SMTP connection successful!
✅ Gmail login successful!
✅ SUCCESS: Request processed successfully
📧 Message: If the email exists, a reset link has been sent to your email.

📬 Check your email inbox (or spam folder)
```

### 3. Kiểm tra Email

1. Mở Gmail: https://mail.google.com
2. Tìm email với subject: **"Reset Your Password - CodeCourse"**
3. Nếu không thấy trong Inbox, check **Spam folder**
4. Email sẽ có:
   - Tiêu đề màu xanh gradient
   - Nút "Reset Password" màu xanh
   - Link để copy/paste
   - Cảnh báo link hết hạn trong 1 giờ

### 4. Click Reset Password

- Click nút "Reset Password" trong email
- Hoặc copy link và paste vào browser
- Link có dạng: `http://localhost:5173/reset-password?token=abc123...`

### 5. Nhập Mật Khẩu Mới (Frontend)

**⚠️ Cần tạo trang reset password ở frontend:**
- Trang: `fe/src/components/ResetPassword.vue`
- Route: `/reset-password`
- Lấy token từ URL query param
- Form nhập password mới
- Gọi API: `POST /api/auth/reset-password`

## 📋 API Endpoints

### 1. Forgot Password (Gửi Email)

```bash
POST /api/auth/forgot-password
Content-Type: application/json

{
  "email": "user@example.com"
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "If the email exists, a reset link has been sent to your email.",
  "resetLink": "http://localhost:5173/reset-password?token=abc123...",
  "token": "abc123..."
}
```

**Note**: `resetLink` và `token` chỉ hiển thị khi `DEBUG=True`

### 2. Reset Password (Đổi Mật Khẩu)

```bash
POST /api/auth/reset-password
Content-Type: application/json

{
  "token": "abc123...",
  "newPassword": "new_secure_password"
}
```

**Response (Success):**
```json
{
  "success": true
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "Token expired"
}
```

## 🔧 Cấu Hình (.env)

```env
# Email SMTP
SMTP_EMAIL=captone149@gmail.com
SMTP_PASSWORD=svgdiramifdlitih

# Frontend URL
FRONTEND_URL=http://localhost:5173

# Debug Mode
DEBUG=True
FLASK_ENV=development
```

## ⚠️ Troubleshooting

### Email không gửi được

**Check 1: SMTP Credentials**
```bash
cd backend
python -c "
from dotenv import load_dotenv
import os
load_dotenv()
print('SMTP_EMAIL:', os.getenv('SMTP_EMAIL'))
print('SMTP_PASSWORD:', '***' if os.getenv('SMTP_PASSWORD') else 'NOT SET')
"
```

**Check 2: Run Test Script**
```bash
python test_reset_password_email.py
```

### Email vào Spam

- Thêm `captone149@gmail.com` vào Contacts
- Mark email là "Not Spam"
- Đợi vài phút

### Backend không chạy

```bash
# Terminal 1: Start backend
cd backend
python app.py

# Terminal 2: Test
python test_reset_password_email.py
```

## 📝 TODO: Frontend

Cần tạo trang reset password ở frontend:

```vue
<!-- fe/src/components/ResetPassword.vue -->
<template>
  <div class="reset-password">
    <h2>Reset Your Password</h2>
    <form @submit.prevent="handleSubmit">
      <input 
        v-model="newPassword" 
        type="password" 
        placeholder="New Password"
        required
      />
      <button type="submit">Reset Password</button>
    </form>
  </div>
</template>

<script>
export default {
  data() {
    return {
      newPassword: '',
      token: ''
    }
  },
  mounted() {
    this.token = this.$route.query.token
  },
  methods: {
    async handleSubmit() {
      const response = await fetch('/api/auth/reset-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          token: this.token,
          newPassword: this.newPassword
        })
      })
      const data = await response.json()
      if (data.success) {
        alert('Password reset successfully!')
        this.$router.push('/login')
      } else {
        alert('Error: ' + data.error)
      }
    }
  }
}
</script>
```

## 🎉 Testing Checklist

- [ ] Backend đang chạy (port 5000)
- [ ] SMTP credentials trong .env
- [ ] Test script chạy thành công
- [ ] Email nhận được trong Gmail
- [ ] Email không vào Spam
- [ ] Link reset password hoạt động
- [ ] Frontend có trang reset password
- [ ] Đổi password thành công
- [ ] Token hết hạn sau 1 giờ
- [ ] Token không dùng lại được

---
**Status**: ✅ Backend hoàn thành
**Next**: Tạo frontend reset password page
