# 🚀 Quick Setup: Email Verification

## Step 1: Setup Gmail App Password (2 minutes)

1. Go to https://myaccount.google.com/apppasswords
2. Sign in to your Google account
3. Create app password:
   - Select app: **Mail**
   - Select device: **Windows Computer** (or your device)
   - Click **Generate**
4. Copy the 16-character password (looks like: `xxxx xxxx xxxx xxxx`)

## Step 2: Update Backend .env (1 minute)

```bash
cd backend
```

Edit `.env` file and add:
```env
SMTP_EMAIL=your-email@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx  # Your app password from step 1
```

## Step 3: Test Email Sending (1 minute)

```bash
# Start backend server
python app.py
```

Test send OTP:
```bash
curl -X POST http://localhost:5000/api/auth/send-otp \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"your-test-email@gmail.com\"}"
```

Check your email inbox (and spam folder)!

## Step 4: Test Frontend (2 minutes)

```bash
# Start frontend
cd ../fe
npm run dev
```

1. Go to http://localhost:5173/register
2. Fill in registration form
3. Click "SEND VERIFICATION CODE"
4. Check email for 6-digit code
5. Enter code and complete registration

## ✅ Done!

Your email verification is now working!

## 🔧 Troubleshooting

**Email not received?**
- Check spam folder
- Verify SMTP_EMAIL and SMTP_PASSWORD in .env
- Make sure you used **App Password**, not regular password
- Ensure 2FA is enabled on Google account

**"Failed to send email" error?**
- Double-check App Password (no spaces)
- Verify SMTP_EMAIL matches your Gmail address
- Check backend logs for detailed error

**Need help?**
See full documentation: `EMAIL_VERIFICATION_SETUP.md`

---

**🎉 Registration Flow:**
```
Register Form → Send OTP → Check Email → Enter Code → Verified!
     📝             📧          ✉️          🔢          ✅
```
