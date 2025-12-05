# Email Verification for Registration

## Overview
Thêm tính năng xác thực email bằng OTP (One-Time Password) cho quy trình đăng ký. User phải xác thực email trước khi có thể tạo tài khoản.

## Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    REGISTRATION FLOW                         │
└─────────────────────────────────────────────────────────────┘

Step 1: User Information
┌──────────────────────┐
│  User fills form:    │
│  - Full Name         │
│  - Email             │
│  - Password          │
│  - Confirm Password  │
└──────────┬───────────┘
           │
           ▼
   Click "SEND VERIFICATION CODE"
           │
           ▼
┌──────────────────────┐
│  Backend validates   │
│  - Email format      │
│  - Email not exists  │
│  - Password length   │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Generate 6-digit    │
│  OTP code            │
│  Store in memory     │
│  (expires in 5 min)  │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Send email via      │
│  Gmail SMTP          │
│  with OTP code       │
└──────────┬───────────┘
           │
           ▼
Step 2: OTP Verification
┌──────────────────────┐
│  User enters 6-digit │
│  OTP code from email │
└──────────┬───────────┘
           │
           ▼
   Click "VERIFY & REGISTER"
           │
           ▼
┌──────────────────────┐
│  Backend validates:  │
│  - OTP exists        │
│  - Not expired       │
│  - Matches code      │
│  - Max 5 attempts    │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Mark email verified │
│  Create user account │
│  Clear OTP data      │
│  Return JWT token    │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  User redirected to  │
│  dashboard           │
└──────────────────────┘
```

## Features

### ✅ Security Features
1. **OTP Expiration:** Code expires after 5 minutes
2. **Attempt Limiting:** Max 5 verification attempts
3. **Email Validation:** Check format and existence
4. **Password Requirements:** Minimum 6 characters
5. **Single Use:** OTP cleared after successful registration

### ✅ User Experience
1. **Two-Step Process:** Clear separation of steps
2. **Real-time Validation:** Immediate feedback
3. **Resend Option:** Can request new code after 60s cooldown
4. **Progress Indication:** Shows current step
5. **Error Messages:** Clear, actionable error messages

### ✅ Email Features
1. **Professional Template:** Branded HTML email
2. **Clear Instructions:** Easy-to-follow format
3. **Expiration Warning:** Shows time limit
4. **Security Notice:** Warning not to share code

## Backend Implementation

### Files Created/Modified

#### 1. New File: `backend/app/routes/EmailVerification.py`
```python
# Endpoints:
POST /api/auth/send-otp       # Send OTP to email
POST /api/auth/verify-otp     # Verify OTP code
POST /api/auth/resend-otp     # Resend OTP code

# Helper functions:
is_email_verified(email)      # Check if email verified
clear_otp(email)              # Clear OTP after registration
```

#### 2. Modified: `backend/app.py`
```python
# Register email verification blueprint
from app.routes.EmailVerification import email_verification_bp
app.register_blueprint(email_verification_bp)
```

#### 3. Modified: `backend/app/routes/Auth.py`
```python
# Add email verification check before registration
from app.routes.EmailVerification import is_email_verified, clear_otp

if not is_email_verified(email):
    return jsonify({"error": "Email chưa được xác thực..."}), 403

# Clear OTP after successful registration
clear_otp(email)
```

### API Endpoints

#### POST /api/auth/send-otp
Send OTP verification code to email

**Request:**
```json
{
  "email": "user@example.com"
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "OTP code sent to your email",
  "email": "user@example.com",
  "expiresIn": 300
}
```

**Response (Error):**
```json
{
  "error": "Email already registered"
}
```

#### POST /api/auth/verify-otp
Verify OTP code

**Request:**
```json
{
  "email": "user@example.com",
  "code": "123456"
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Email verified successfully",
  "email": "user@example.com"
}
```

**Response (Error):**
```json
{
  "error": "Invalid OTP code. 3 attempts remaining.",
  "remaining": 3
}
```

#### POST /api/auth/resend-otp
Resend OTP code

**Request:**
```json
{
  "email": "user@example.com"
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "New OTP code sent to your email",
  "email": "user@example.com",
  "expiresIn": 300
}
```

### Email Configuration

#### Setup Gmail App Password

1. **Enable 2-Factor Authentication** on your Google account
2. **Generate App Password:**
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and your device
   - Copy the 16-character password

3. **Update .env file:**
```env
SMTP_EMAIL=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
```

#### Email Template
Professional HTML email with:
- Branded header with gradient
- Large, centered OTP code
- Expiration warning
- Security notice
- Professional footer

## Frontend Implementation

### Files Modified

#### `fe/src/components/User/Register.vue`

**New Features:**
1. **Two-Step Form:**
   - Step 1: Registration information
   - Step 2: OTP verification

2. **State Management:**
```javascript
data() {
  return {
    step: 1,                    // Current step (1 or 2)
    otpCode: "",                // 6-digit OTP
    resendCooldown: 0,          // Resend button cooldown
    // ...existing fields
  }
}
```

3. **Methods:**
```javascript
handleSendOTP()              // Step 1: Send OTP
handleVerifyAndRegister()    // Step 2: Verify & Register
handleResendOTP()            // Resend OTP code
goBackToStep1()             // Go back to step 1
startResendCooldown(seconds) // Cooldown timer
```

### UI Components

#### Step 1: Registration Form
```vue
<form @submit.prevent="handleSendOTP">
  <input v-model="username" placeholder="Full name" />
  <input v-model="email" type="email" placeholder="Email" />
  <input v-model="password" type="password" placeholder="Password" />
  <input v-model="confirmPassword" type="password" placeholder="Confirm" />
  <button type="submit">SEND VERIFICATION CODE</button>
</form>
```

#### Step 2: OTP Verification
```vue
<form @submit.prevent="handleVerifyAndRegister">
  <input 
    v-model="otpCode" 
    maxlength="6" 
    pattern="[0-9]{6}"
    placeholder="Enter 6-digit code" 
  />
  <div class="button-row">
    <button type="button" @click="goBackToStep1">← Back</button>
    <button type="submit">VERIFY & REGISTER</button>
  </div>
  <button 
    type="button" 
    @click="handleResendOTP"
    :disabled="resendCooldown > 0"
  >
    {{ resendCooldown > 0 ? `Resend (${resendCooldown}s)` : 'Resend code' }}
  </button>
</form>
```

## User Experience Flow

### Scenario 1: Successful Registration

1. **User fills registration form**
   - Name: "Nguyen Van A"
   - Email: "user@example.com"
   - Password: "******"

2. **Click "SEND VERIFICATION CODE"**
   - ✅ Validates inputs
   - ✅ Sends OTP via email
   - ✅ Shows success: "Verification code sent!"
   - ✅ Auto-advances to Step 2 after 1.5s

3. **User checks email**
   - 📧 Receives email with 6-digit code: `123456`
   - ⏰ Sees expiration warning: "Expires in 5 minutes"

4. **User enters OTP code**
   - Types: `123456`
   - Click "VERIFY & REGISTER"

5. **System verifies and creates account**
   - ✅ Verifies OTP
   - ✅ Creates user account
   - ✅ Generates JWT token
   - ✅ Redirects to dashboard

### Scenario 2: Wrong OTP Code

1. **User enters wrong code:** `111111`
2. **System shows error:** "Invalid OTP code. 4 attempts remaining."
3. **User tries again** (up to 5 attempts)
4. **After 5 wrong attempts:** "Too many failed attempts. Please request a new code."

### Scenario 3: OTP Expired

1. **User waits > 5 minutes**
2. **Tries to verify**
3. **System shows:** "OTP code has expired. Please request a new one."
4. **User clicks "Resend code"**
5. **New OTP sent**

### Scenario 4: Email Already Registered

1. **User enters existing email**
2. **System shows:** "Email already registered"
3. **User can go to login page**

## Error Handling

### Backend Errors
```python
400 Bad Request          # Invalid input
403 Forbidden            # Email not verified
409 Conflict             # Email already exists
410 Gone                 # OTP expired
429 Too Many Requests    # Too many attempts
500 Internal Server      # Server error
```

### Frontend Error Messages
```javascript
"Please provide your full name."
"Passwords do not match."
"Password must be at least 6 characters."
"Failed to send verification code."
"Please enter the 6-digit verification code."
"Verification failed. Please try again."
"OTP code has expired."
"Too many failed attempts."
```

## Security Considerations

### ✅ Implemented
1. **OTP expiration** (5 minutes)
2. **Attempt limiting** (5 max)
3. **Email format validation**
4. **Password strength requirement**
5. **HTTPS for email transmission** (Gmail SMTP with TLS)
6. **One-time use** (OTP cleared after registration)

### ⚠️ Production Recommendations
1. **Use Redis** instead of in-memory storage
2. **Rate limiting** on send-otp endpoint
3. **Email verification** table in database
4. **Audit logging** for security events
5. **CAPTCHA** to prevent spam
6. **IP tracking** for abuse detection

## Testing

### Manual Testing Steps

1. **Test successful flow:**
   ```
   1. Fill registration form
   2. Click "Send verification code"
   3. Check email inbox
   4. Enter correct OTP
   5. Verify account created
   ```

2. **Test wrong OTP:**
   ```
   1. Enter wrong code 3 times
   2. Verify error message shows remaining attempts
   3. Enter correct code
   4. Verify registration succeeds
   ```

3. **Test OTP expiration:**
   ```
   1. Send OTP
   2. Wait 6 minutes
   3. Try to verify
   4. Verify expiration error
   5. Resend OTP
   6. Verify with new code
   ```

4. **Test resend:**
   ```
   1. Send OTP
   2. Click "Resend" (should be disabled)
   3. Wait 60 seconds
   4. Click "Resend" (should work)
   5. Check email for new code
   ```

5. **Test back button:**
   ```
   1. Go to Step 2
   2. Click "Back" button
   3. Verify returns to Step 1
   4. Verify form data preserved
   ```

### Automated Tests

```bash
# Test send OTP
curl -X POST http://localhost:5000/api/auth/send-otp \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com"}'

# Test verify OTP
curl -X POST http://localhost:5000/api/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","code":"123456"}'

# Test resend OTP
curl -X POST http://localhost:5000/api/auth/resend-otp \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com"}'
```

## Configuration

### Required Environment Variables

```env
# Gmail SMTP Configuration
SMTP_EMAIL=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Alternative variable names (fallback)
GMAIL_USER=your-email@gmail.com
GMAIL_APP_PASSWORD=your-app-password
```

### OTP Configuration (in code)

```python
# backend/app/routes/EmailVerification.py
OTP_EXPIRATION_MINUTES = 5    # OTP expires after 5 minutes
MAX_ATTEMPTS = 5                # Max verification attempts
OTP_LENGTH = 6                  # 6-digit code
RESEND_COOLDOWN = 60            # 60 seconds between resends
```

## Deployment Checklist

- [ ] Set up Gmail App Password
- [ ] Add SMTP credentials to .env
- [ ] Test email delivery in production
- [ ] Configure email template with production branding
- [ ] Set up Redis for OTP storage (production)
- [ ] Add rate limiting
- [ ] Add monitoring for failed attempts
- [ ] Test spam folder delivery
- [ ] Add email delivery logging
- [ ] Set up alerts for high failure rates

## Troubleshooting

### Email not received

1. **Check spam folder**
2. **Verify SMTP credentials** in .env
3. **Check Gmail security settings**
4. **Verify App Password** is correct
5. **Check backend logs** for email errors

### "Failed to send email" error

```python
# Check these:
1. SMTP_EMAIL and SMTP_PASSWORD set in .env
2. Gmail App Password (not regular password)
3. 2FA enabled on Google account
4. Less secure app access disabled (use App Password)
5. SMTP port 587 not blocked by firewall
```

### OTP not verifying

```python
# Debug steps:
1. Check OTP_STORAGE in memory
2. Verify email matches (case-insensitive)
3. Check if OTP expired
4. Verify code matches exactly (6 digits)
5. Check attempt count
```

## Files Changed

### Backend
- ✅ `backend/app/routes/EmailVerification.py` (NEW)
- ✅ `backend/app.py` (Modified)
- ✅ `backend/app/routes/Auth.py` (Modified)
- ✅ `backend/.env.example` (NEW)

### Frontend
- ✅ `fe/src/components/User/Register.vue` (Modified)

### Documentation
- ✅ `EMAIL_VERIFICATION_SETUP.md` (THIS FILE)

---

**Status:** ✅ Complete and Ready for Testing
**Last Updated:** 2024-12-05
**Version:** 1.0.0
