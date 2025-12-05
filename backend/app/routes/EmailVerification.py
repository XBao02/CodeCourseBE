"""Email verification endpoints for user registration"""

from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

email_verification_bp = Blueprint('email_verification', __name__, url_prefix='/api/auth')

# In-memory storage for OTP codes (in production, use Redis or database)
# Format: { email: { code: "123456", expires_at: datetime, verified: bool } }
_OTP_STORAGE = {}

# OTP expiration time (5 minutes)
OTP_EXPIRATION_MINUTES = 5

def generate_otp(length=6):
    """Generate a random 6-digit OTP code"""
    return ''.join(random.choices(string.digits, k=length))

def send_otp_email(to_email, otp_code):
    """Send OTP code via Gmail SMTP"""
    try:
        # Get email credentials from environment
        smtp_email = os.getenv('SMTP_EMAIL') or os.getenv('GMAIL_USER')
        smtp_password = os.getenv('SMTP_PASSWORD') or os.getenv('GMAIL_APP_PASSWORD')
        
        if not smtp_email or not smtp_password:
            raise Exception("SMTP credentials not configured. Set SMTP_EMAIL and SMTP_PASSWORD in .env")
        
        # Create email message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Verify Your Email - CodeCourse'
        msg['From'] = f"CodeCourse <{smtp_email}>"
        msg['To'] = to_email
        
        # HTML email template
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 8px 8px; }}
                .otp-box {{ background: white; border: 2px dashed #3b82f6; padding: 20px; text-align: center; margin: 20px 0; border-radius: 8px; }}
                .otp-code {{ font-size: 32px; font-weight: bold; color: #3b82f6; letter-spacing: 8px; }}
                .footer {{ text-align: center; color: #666; font-size: 14px; margin-top: 20px; }}
                .warning {{ background: #fef3c7; border-left: 4px solid #f59e0b; padding: 12px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎓 Email Verification</h1>
                    <p>Welcome to CodeCourse!</p>
                </div>
                <div class="content">
                    <p>Hi there! 👋</p>
                    <p>Thank you for registering with CodeCourse. To complete your registration, please verify your email address using the code below:</p>
                    
                    <div class="otp-box">
                        <p style="margin: 0; color: #666; font-size: 14px;">Your verification code:</p>
                        <div class="otp-code">{otp_code}</div>
                    </div>
                    
                    <div class="warning">
                        <strong>⚠️ Important:</strong> This code will expire in {OTP_EXPIRATION_MINUTES} minutes. Do not share this code with anyone.
                    </div>
                    
                    <p>If you didn't request this code, please ignore this email.</p>
                    
                    <div class="footer">
                        <p>© 2024 CodeCourse. All rights reserved.</p>
                        <p>This is an automated email. Please do not reply.</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Attach HTML content
        part = MIMEText(html, 'html')
        msg.attach(part)
        
        # Send email via Gmail SMTP
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(smtp_email, smtp_password)
            server.send_message(msg)
        
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        raise

@email_verification_bp.post('/send-otp')
def send_otp():
    """
    Send OTP code to email for verification
    Request body: { "email": "user@example.com" }
    """
    try:
        data = request.get_json() or {}
        email = (data.get('email') or '').strip().lower()
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        # Validate email format
        import re
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Check if user already exists
        from app.models.model import User
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'error': 'Email already registered'}), 409
        
        # Generate OTP
        otp_code = generate_otp()
        expires_at = datetime.utcnow() + timedelta(minutes=OTP_EXPIRATION_MINUTES)
        
        # Store OTP
        _OTP_STORAGE[email] = {
            'code': otp_code,
            'expires_at': expires_at,
            'verified': False,
            'attempts': 0
        }
        
        # Send email
        try:
            send_otp_email(email, otp_code)
        except Exception as e:
            return jsonify({'error': f'Failed to send email: {str(e)}'}), 500
        
        return jsonify({
            'success': True,
            'message': 'OTP code sent to your email',
            'email': email,
            'expiresIn': OTP_EXPIRATION_MINUTES * 60  # seconds
        }), 200
        
    except Exception as e:
        print(f"Error in send_otp: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@email_verification_bp.post('/verify-otp')
def verify_otp():
    """
    Verify OTP code
    Request body: { "email": "user@example.com", "code": "123456" }
    """
    try:
        data = request.get_json() or {}
        email = (data.get('email') or '').strip().lower()
        code = (data.get('code') or '').strip()
        
        if not email or not code:
            return jsonify({'error': 'Email and code are required'}), 400
        
        # Check if OTP exists
        if email not in _OTP_STORAGE:
            return jsonify({'error': 'No OTP found for this email. Please request a new one.'}), 404
        
        otp_data = _OTP_STORAGE[email]
        
        # Check expiration
        if datetime.utcnow() > otp_data['expires_at']:
            del _OTP_STORAGE[email]
            return jsonify({'error': 'OTP code has expired. Please request a new one.'}), 410
        
        # Check attempts (max 5 attempts)
        if otp_data['attempts'] >= 5:
            del _OTP_STORAGE[email]
            return jsonify({'error': 'Too many failed attempts. Please request a new code.'}), 429
        
        # Verify code
        if code != otp_data['code']:
            otp_data['attempts'] += 1
            remaining = 5 - otp_data['attempts']
            return jsonify({
                'error': f'Invalid OTP code. {remaining} attempts remaining.',
                'remaining': remaining
            }), 400
        
        # Mark as verified
        otp_data['verified'] = True
        
        return jsonify({
            'success': True,
            'message': 'Email verified successfully',
            'email': email
        }), 200
        
    except Exception as e:
        print(f"Error in verify_otp: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@email_verification_bp.post('/resend-otp')
def resend_otp():
    """
    Resend OTP code to email
    Request body: { "email": "user@example.com" }
    """
    try:
        data = request.get_json() or {}
        email = (data.get('email') or '').strip().lower()
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        # Check if there's an existing OTP
        if email in _OTP_STORAGE:
            old_otp = _OTP_STORAGE[email]
            # Check if already verified
            if old_otp.get('verified'):
                return jsonify({'error': 'Email already verified'}), 400
        
        # Generate new OTP
        otp_code = generate_otp()
        expires_at = datetime.utcnow() + timedelta(minutes=OTP_EXPIRATION_MINUTES)
        
        # Store new OTP
        _OTP_STORAGE[email] = {
            'code': otp_code,
            'expires_at': expires_at,
            'verified': False,
            'attempts': 0
        }
        
        # Send email
        try:
            send_otp_email(email, otp_code)
        except Exception as e:
            return jsonify({'error': f'Failed to send email: {str(e)}'}), 500
        
        return jsonify({
            'success': True,
            'message': 'New OTP code sent to your email',
            'email': email,
            'expiresIn': OTP_EXPIRATION_MINUTES * 60
        }), 200
        
    except Exception as e:
        print(f"Error in resend_otp: {e}")
        return jsonify({'error': 'Internal server error'}), 500

def is_email_verified(email):
    """Check if email has been verified"""
    email = email.strip().lower()
    if email not in _OTP_STORAGE:
        return False
    return _OTP_STORAGE[email].get('verified', False)

def clear_otp(email):
    """Clear OTP data after successful registration"""
    email = email.strip().lower()
    if email in _OTP_STORAGE:
        del _OTP_STORAGE[email]

__all__ = ['email_verification_bp', 'is_email_verified', 'clear_otp']
