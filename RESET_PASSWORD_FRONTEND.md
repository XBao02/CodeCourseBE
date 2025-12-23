# Reset Password Page - Frontend Implementation

## ✅ Hoàn Thành

Đã tạo trang **Reset Password** cho frontend với đầy đủ chức năng!

## 📁 Files Đã Tạo/Sửa

### 1. **Component Mới**
- `fe/src/components/User/ResetPassword.vue`

### 2. **Router Update**
- `fe/src/router/index.js`
  - Import ResetPassword component
  - Thêm route `/reset-password`

## 🎨 Features

### ✨ UI/UX Features
- ✅ Beautiful gradient background (purple theme)
- ✅ Clean card design với shadow
- ✅ Icon 🔐 ở header
- ✅ Password visibility toggle (show/hide)
- ✅ Confirm password field
- ✅ Real-time password mismatch validation
- ✅ Loading spinner khi submit
- ✅ Success/Error alerts với icons
- ✅ Auto-redirect to login sau khi thành công
- ✅ Responsive design (mobile-friendly)

### 🔒 Security Features
- ✅ Token validation
- ✅ Password length requirement (min 6 characters)
- ✅ Password confirmation
- ✅ Disabled state khi loading
- ✅ Error handling cho expired/invalid tokens

### 💡 User Feedback
- ✅ Inline error messages
- ✅ Password mismatch warning
- ✅ Success confirmation
- ✅ Clear instructions
- ✅ Links back to Login/Home

## 🚀 Cách Sử Dụng

### 1. Click Link Từ Email
```
User nhận email → Click "Reset Password" button
→ Mở: http://localhost:5173/reset-password?token=abc123...
```

### 2. Trang Reset Password Hiển Thị
```
┌────────────────────────────────────┐
│           🔐                       │
│     Reset Your Password           │
│  Enter your new password below    │
│                                    │
│  New Password:                     │
│  ┌─────────────────────────┐ 👁️  │
│  │                         │      │
│  └─────────────────────────┘      │
│  Password must be at least 6...   │
│                                    │
│  Confirm Password:                 │
│  ┌─────────────────────────┐ 👁️  │
│  │                         │      │
│  └─────────────────────────┘      │
│                                    │
│  ┌─────────────────────────────┐  │
│  │   Reset Password            │  │
│  └─────────────────────────────┘  │
│                                    │
│  ← Back to Login  |  Home         │
└────────────────────────────────────┘
```

### 3. User Nhập Password Mới
- Nhập password (min 6 ký tự)
- Nhập lại để confirm
- Click "Reset Password"

### 4. Validation
- ❌ Passwords không match → Hiện warning
- ❌ Password < 6 ký tự → Error
- ❌ Token không hợp lệ → Error
- ✅ All valid → Gửi request

### 5. Submit Request
```javascript
POST /api/auth/reset-password
{
  "token": "abc123...",
  "newPassword": "new_password"
}
```

### 6. Response Handling

**Success:**
```
✅ Password Reset Successfully!
   Redirecting to login page...
   
[Tự động chuyển đến /login sau 2 giây]
```

**Error:**
```
❌ Error
   Token expired
   
[Hoặc error khác: Invalid token, Token already used, etc.]
```

## 🎯 Complete Flow

```
┌─────────────────────────────────────────────────────────┐
│ 1. User quên mật khẩu                                   │
│    → Vào /forgot-password                               │
│    → Nhập email → Click "Send Reset Link"              │
├─────────────────────────────────────────────────────────┤
│ 2. Backend gửi email                                    │
│    → Tạo token                                          │
│    → Gửi email qua Gmail SMTP                           │
│    → Email có link + button                             │
├─────────────────────────────────────────────────────────┤
│ 3. User check email                                     │
│    → Mở Gmail                                           │
│    → Tìm email "Reset Your Password - CodeCourse"      │
│    → Click button "Reset Password"                      │
├─────────────────────────────────────────────────────────┤
│ 4. Mở trang Reset Password                              │
│    → URL: /reset-password?token=abc123                 │
│    → Component ResetPassword.vue load                   │
│    → Lấy token từ URL query                            │
├─────────────────────────────────────────────────────────┤
│ 5. User nhập password mới                               │
│    → Nhập password                                      │
│    → Nhập confirm password                              │
│    → Validate                                           │
│    → Click "Reset Password"                             │
├─────────────────────────────────────────────────────────┤
│ 6. Frontend gọi API                                     │
│    → POST /api/auth/reset-password                     │
│    → Body: { token, newPassword }                      │
├─────────────────────────────────────────────────────────┤
│ 7. Backend xử lý                                        │
│    → Validate token (exists, not used, not expired)    │
│    → Hash password mới                                  │
│    → Update database                                    │
│    → Mark token as used                                 │
│    → Return success                                     │
├─────────────────────────────────────────────────────────┤
│ 8. Success                                              │
│    → Hiện message "Password Reset Successfully!"       │
│    → Auto redirect to /login sau 2 giây                │
│    → User login với password mới                        │
└─────────────────────────────────────────────────────────┘
```

## 🧪 Testing

### Test Case 1: Valid Token
```bash
# 1. Request forgot password
curl -X POST http://localhost:5000/api/auth/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'

# 2. Get token from response or email
# 3. Open browser: http://localhost:5173/reset-password?token=abc123...
# 4. Enter new password
# 5. Submit → Should show success
```

### Test Case 2: Invalid Token
```bash
# Open: http://localhost:5173/reset-password?token=invalid_token
# Enter password → Submit
# Should show error: "Invalid token"
```

### Test Case 3: Expired Token
```bash
# Wait 1 hour after forgot-password request
# Try to reset
# Should show error: "Token expired"
```

### Test Case 4: Password Mismatch
```bash
# Enter different passwords in two fields
# Should show warning immediately
# Submit button should be disabled
```

### Test Case 5: No Token
```bash
# Open: http://localhost:5173/reset-password
# Should show error: "Invalid reset link. Token not found."
```

## 📱 Responsive Design

### Desktop (> 640px)
- Card width: 480px
- Font sizes: normal
- Padding: 40px

### Mobile (≤ 640px)
- Card width: 100%
- Smaller fonts
- Padding: 30px 24px
- Smaller icon

## 🎨 Color Scheme

### Background
- Gradient: `#667eea` → `#764ba2` (Purple)

### Card
- Background: White
- Border-radius: 16px
- Shadow: 0 20px 60px rgba(0, 0, 0, 0.3)

### Button
- Gradient: `#667eea` → `#764ba2`
- Hover: translateY(-2px) + shadow

### Alerts
- Success: Green (#d1fae5)
- Error: Red (#fee2e2)
- Warning: Yellow (#fef3c7)

## 🔧 Customization

### Change API Endpoint
```javascript
// In ResetPassword.vue, line ~153
const response = await axios.post('http://localhost:5000/api/auth/reset-password', {
    token: this.token,
    newPassword: this.newPassword
});
```

### Change Redirect Delay
```javascript
// In ResetPassword.vue, line ~163
setTimeout(() => {
    this.$router.push('/login');
}, 2000); // Change 2000 to desired milliseconds
```

### Change Password Requirements
```javascript
// In ResetPassword.vue, line ~142
if (this.newPassword.length < 6) {
    // Change 6 to desired minimum length
}
```

```html
<!-- In template, line ~52 -->
<input
    minlength="6"  <!-- Change minimum length -->
/>
```

## 📝 Code Structure

### Template
1. **Header** - Icon, title, subtitle
2. **Alerts** - Success/Error/Warning messages
3. **Form** - Password inputs with toggle visibility
4. **Footer** - Links back to Login/Home

### Script
- **Data**: Form fields, state flags
- **Computed**: Password mismatch validation
- **Mounted**: Get token from URL
- **Methods**: Submit handler, API call, error handling

### Style
- **Scoped CSS** - Component-specific styles
- **Responsive** - Media queries for mobile
- **Animations** - Spinner, hover effects
- **Colors** - Purple theme matching brand

## ⚠️ Notes

### Token Security
- Token validated on backend
- One-time use (marked as used after reset)
- Expires after 1 hour
- Cannot be reused

### Error Handling
- Network errors → "Cannot connect to server"
- Server errors → Display error message from backend
- Client errors → Display validation errors

### UX Improvements
- Disabled submit when loading
- Clear visual feedback
- Auto-redirect after success
- Links back to login/home

## 🎉 Completion Checklist

- [x] ResetPassword.vue component created
- [x] Router updated with /reset-password route
- [x] Token extraction from URL
- [x] Password input with visibility toggle
- [x] Confirm password validation
- [x] API integration
- [x] Success/Error handling
- [x] Auto-redirect after success
- [x] Responsive design
- [x] Loading states
- [x] Error messages
- [x] Footer links
- [x] Console logs for debugging

## 🚀 Deploy & Test

```bash
# Start Frontend
cd fe
npm run dev

# Start Backend
cd backend
python app.py

# Test Flow:
# 1. Go to: http://localhost:5173/forgot-password
# 2. Enter email → Get reset email
# 3. Click link in email
# 4. Reset password page opens
# 5. Enter new password → Submit
# 6. Success → Auto redirect to login
# 7. Login with new password
```

---
**Status**: ✅ HOÀN THÀNH
**Date**: December 21, 2025
**Components**: ResetPassword.vue, router/index.js
