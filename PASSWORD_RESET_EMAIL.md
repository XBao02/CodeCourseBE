# Password Reset Email Implementation

## Tổng Quan
Đã thêm chức năng gửi email reset password qua Gmail SMTP khi người dùng quên mật khẩu.

## Thay Đổi

### 1. **Import thêm thư viện email**
```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
```

### 2. **Hàm gửi email reset password**
```python
def send_reset_password_email(to_email, reset_link, user_name):
    """Send password reset link via Gmail SMTP"""
```

**Chức năng**:
- Gửi email HTML đẹp mắt với link reset password
- Hiển thị tên người dùng
- Có nút "Reset Password" và link copy/paste
- Cảnh báo link hết hạn trong 1 giờ
- Template responsive và professional

### 3. **Cập nhật endpoint `/forgot-password`**

**Trước**:
```python
# In real app, send email with reset link. For now, return token for testing.
reset_link = f"http://localhost:5000/api/auth/reset-password?token={token}"
return jsonify({ 'success': True, 'resetLink': reset_link, 'token': token }), 200
```

**Sau**:
```python
# Generate reset link (frontend URL)
frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
reset_link = f"{frontend_url}/reset-password?token={token}"

# Send email
user_name = user.full_name or user.email.split('@')[0]
email_sent = send_reset_password_email(user.email, reset_link, user_name)

# Return success (hiding token in production)
response = { 
    'success': True, 
    'message': 'If the email exists, a reset link has been sent to your email.'
}

# Only include link/token in development mode
if os.getenv('DEBUG') == 'True' or os.getenv('FLASK_ENV') == 'development':
    response['resetLink'] = reset_link
    response['token'] = token

return jsonify(response), 200
```

## Cấu Hình

### 1. **File `.env` (Backend)**

Thêm các biến môi trường sau vào file `.env` trong thư mục `backend/`:

```env
# Gmail SMTP Configuration
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=your_app_password_here

# Frontend URL (for reset link)
FRONTEND_URL=http://localhost:5173

# Debug mode (set to True for development)
DEBUG=True
FLASK_ENV=development
```

### 2. **Tạo Gmail App Password**

Để gửi email qua Gmail, bạn cần tạo **App Password** (không dùng mật khẩu Gmail thường):

#### Bước 1: Bật 2-Step Verification
1. Truy cập: https://myaccount.google.com/security
2. Tìm "2-Step Verification"
3. Bật tính năng này

#### Bước 2: Tạo App Password
1. Truy cập: https://myaccount.google.com/apppasswords
2. Chọn app: "Mail"
3. Chọn device: "Other" → nhập "CodeCourse Backend"
4. Click "Generate"
5. Copy mật khẩu 16 ký tự (dạng: `xxxx xxxx xxxx xxxx`)
6. Paste vào `.env` (loại bỏ khoảng trắng)

```env
SMTP_PASSWORD=xxxxxxxxxxxxxxxx
```

### 3. **Kiểm tra cấu hình**

Chạy Python để test SMTP credentials:

```python
import os
from dotenv import load_dotenv
load_dotenv()

print("SMTP_EMAIL:", os.getenv('SMTP_EMAIL'))
print("SMTP_PASSWORD:", "***" if os.getenv('SMTP_PASSWORD') else "NOT SET")
print("FRONTEND_URL:", os.getenv('FRONTEND_URL'))
```

## Luồng Hoạt Động

### 1. **User Request Reset**
```
POST /api/auth/forgot-password
Body: { "email": "user@example.com" }
```

### 2. **Backend Process**
```
1. Validate email
2. Find user in database
3. Generate secure token (URL-safe, 32 bytes)
4. Save token to database (expires in 1 hour)
5. Create reset link: {FRONTEND_URL}/reset-password?token={token}
6. Send email with reset link
7. Return success response
```

### 3. **Email Content**
```
Subject: Reset Your Password - CodeCourse
To: user@example.com

[Beautiful HTML email with:]
- Greeting with user's name
- "Reset Password" button (link to frontend)
- Copyable link
- Warning: link expires in 1 hour
- Professional footer
```

### 4. **User Clicks Link**
```
Frontend: http://localhost:5173/reset-password?token=abc123...
```

### 5. **User Submits New Password**
```
POST /api/auth/reset-password
Body: {
  "token": "abc123...",
  "newPassword": "new_secure_password"
}
```

### 6. **Backend Updates Password**
```
1. Validate token (exists, not used, not expired)
2. Hash new password
3. Update user password
4. Mark token as used
5. Return success
```

## Email Template

### HTML Email Features
✅ Responsive design (looks good on mobile/desktop)
✅ Professional gradient header
✅ Clear call-to-action button
✅ Copyable link for manual paste
✅ Security warning (expiration, don't share)
✅ CodeCourse branding
✅ Footer with copyright

### Preview
```
┌─────────────────────────────────────┐
│   🔐 Reset Your Password           │ (Blue gradient)
├─────────────────────────────────────┤
│ Hi Nguyen Van A,                    │
│                                     │
│ We received a request to reset...  │
│                                     │
│  ┌─────────────────────────────┐   │
│  │    [Reset Password]         │   │ (Blue button)
│  └─────────────────────────────┘   │
│                                     │
│ Or copy this link:                  │
│ ┌─────────────────────────────────┐│
│ │ http://localhost:5173/reset...  ││
│ └─────────────────────────────────┘│
│                                     │
│ ⚠️ Important: Link expires in 1 hour│
│                                     │
│ © 2024 CodeCourse                   │
└─────────────────────────────────────┘
```

## Security Features

### 1. **Token Security**
- ✅ URL-safe random token (32 bytes = 256 bits entropy)
- ✅ Stored in database with expiration (1 hour)
- ✅ One-time use (marked as used after reset)
- ✅ Cannot be guessed or brute-forced

### 2. **Email Enumeration Protection**
```python
if not user:
    # Don't reveal if email exists or not
    return jsonify({ 'success': True, 'message': '...' }), 200
```
- Always return success, even if email doesn't exist
- Prevents attackers from discovering registered emails

### 3. **Production Mode**
```python
# Only show token/link in development
if os.getenv('DEBUG') == 'True':
    response['resetLink'] = reset_link  # For testing
```
- Token/link hidden in production responses
- User must check email to get reset link

### 4. **SMTP Security**
- Uses TLS encryption (port 587)
- App-specific password (not main Gmail password)
- Credentials stored in `.env` (not committed to git)

## Testing

### 1. **Test Email Sending (Development)**

```bash
# Start backend
cd backend
python app.py

# Send request
curl -X POST http://localhost:5000/api/auth/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'

# Response (DEBUG=True):
{
  "success": true,
  "message": "If the email exists, a reset link has been sent to your email.",
  "resetLink": "http://localhost:5173/reset-password?token=abc123...",
  "token": "abc123..."
}
```

### 2. **Check Email**
- Đăng nhập vào Gmail của user
- Kiểm tra Inbox (hoặc Spam nếu không thấy)
- Email phải có subject: "Reset Your Password - CodeCourse"
- Click nút "Reset Password" hoặc copy link

### 3. **Test Reset Password**

```bash
# User submits new password via frontend
curl -X POST http://localhost:5000/api/auth/reset-password \
  -H "Content-Type: application/json" \
  -d '{
    "token": "abc123...",
    "newPassword": "new_secure_pass123"
  }'

# Response:
{
  "success": true
}
```

### 4. **Test Token Expiration**

```bash
# Wait 1 hour + 1 minute, then try reset
curl -X POST http://localhost:5000/api/auth/reset-password \
  -H "Content-Type: application/json" \
  -d '{"token": "expired_token", "newPassword": "new_pass"}'

# Response:
{
  "success": false,
  "error": "Token expired"
}
```

### 5. **Test Token Reuse**

```bash
# Try using same token twice
# First time: Success
# Second time: Error "Token already used"
```

## Troubleshooting

### Problem: Email không gửi được

**Check 1: SMTP Credentials**
```python
import os
from dotenv import load_dotenv
load_dotenv()

smtp_email = os.getenv('SMTP_EMAIL')
smtp_password = os.getenv('SMTP_PASSWORD')

print(f"SMTP_EMAIL: {smtp_email}")
print(f"SMTP_PASSWORD: {'***' if smtp_password else 'NOT SET'}")
```

**Check 2: Gmail Settings**
- Đã bật 2-Step Verification?
- Đã tạo App Password?
- App Password không có khoảng trắng?

**Check 3: Firewall/Network**
```bash
# Test Gmail SMTP connection
telnet smtp.gmail.com 587
```

**Check 4: Console Logs**
```
✅ Password reset email sent to user@example.com  # Success
❌ Error sending password reset email: ...        # Failed
```

### Problem: Email vào Spam

**Solution:**
- Thêm sender vào Contacts
- Mark email as "Not Spam"
- Đợi vài phút (Gmail learning)

### Problem: Link không hoạt động

**Check Frontend URL:**
```env
FRONTEND_URL=http://localhost:5173  # Must match frontend
```

**Check Token:**
- Token có trong database?
- Token chưa hết hạn?
- Token chưa được sử dụng?

## Production Deployment

### 1. **Environment Variables**
```env
# Production .env
SMTP_EMAIL=noreply@yourdomain.com
SMTP_PASSWORD=production_app_password
FRONTEND_URL=https://yourdomain.com
DEBUG=False
FLASK_ENV=production
```

### 2. **Email Service Alternatives**
Thay vì Gmail SMTP, có thể dùng:
- **SendGrid** (99% deliverability)
- **Mailgun** (API-based)
- **AWS SES** (scalable)
- **Postmark** (fast)

### 3. **Security Checklist**
- [ ] Sử dụng HTTPS cho frontend
- [ ] Ẩn token/link trong production response
- [ ] Rate limit forgot-password endpoint
- [ ] Log failed attempts
- [ ] Monitor email sending failures
- [ ] Set up SPF/DKIM/DMARC records

## Files Modified

1. **backend/app/routes/Auth.py**
   - Added `send_reset_password_email()` function
   - Updated `/forgot-password` endpoint
   - Added email imports

2. **backend/.env** (need to create/update)
   - Add SMTP credentials
   - Add FRONTEND_URL

## Next Steps

1. ✅ Cấu hình `.env` với Gmail credentials
2. ✅ Test gửi email
3. ⚠️ Tạo trang reset password ở frontend
4. ⚠️ Thêm rate limiting (tránh spam)
5. ⚠️ Thêm analytics (track email open rate)

---
**Status**: ✅ HOÀN THÀNH (Backend)
**Date**: December 21, 2025
**Requires**: Gmail App Password, Frontend reset page
