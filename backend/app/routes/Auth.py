from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from werkzeug.security import check_password_hash, generate_password_hash
from app.models import db
from app.models.model import User, Student, Instructor, Admin
import re
import bcrypt
from datetime import datetime, timedelta
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

ROLE_TO_ROUTE = {
    "admin": "/admin",
    "instructor": "/instructor",
    "student": "/student",
}

# Simple password reset token store (DB table recommended in production)
class PasswordResetToken(db.Model):
    __tablename__ = 'PasswordResetTokens'
    id = db.Column('Id', db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column('UserId', db.BigInteger, db.ForeignKey('Users.Id'), nullable=False)
    token = db.Column('Token', db.String(120), unique=True, nullable=False)
    expires_at = db.Column('ExpiresAt', db.DateTime(timezone=True), nullable=False)
    used_at = db.Column('UsedAt', db.DateTime(timezone=True))
    created_at = db.Column('CreatedAt', db.DateTime(timezone=True), default=datetime.utcnow)


# Helpers

def _valid_email(email: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", (email or "").strip()))


def _role_redirect_path(role: str) -> str:
    return ROLE_TO_ROUTE.get(role, "/")


def _get_or_create_role_row(user_id: int, role: str):
    """Ensure role sub-record exists for the user."""
    try:
        if role == "student":
            if not Student.query.filter_by(user_id=user_id).first():
                db.session.add(Student(user_id=user_id))
        elif role == "instructor":
            if not Instructor.query.filter_by(user_id=user_id).first():
                db.session.add(Instructor(user_id=user_id))
        elif role == "admin":
            if not Admin.query.filter_by(user_id=user_id).first():
                db.session.add(Admin(user_id=user_id))
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error ensuring role row: {e}")


def _resolve_role(user: User) -> str:
    """Resolve role from sub-tables if needed; fallback to user.role."""
    if Admin.query.filter_by(user_id=user.id).first():
        return "admin"
    if Instructor.query.filter_by(user_id=user.id).first():
        return "instructor"
    if Student.query.filter_by(user_id=user.id).first():
        return "student"
    return user.role or "student"


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    full_name = (data.get("full_name") or data.get("fullname") or "").strip()
    role = (data.get("role") or "student").strip().lower()

    if not _valid_email(email):
        return jsonify({"error": "Email không hợp lệ"}), 400
    if len(password) < 6:
        return jsonify({"error": "Mật khẩu tối thiểu 6 ký tự"}), 400
    if role not in ("student", "instructor", "admin"):
        return jsonify({"error": "Role không hợp lệ"}), 400

    # ✅ Check email verification
    from app.routes.EmailVerification import is_email_verified, clear_otp
    if not is_email_verified(email):
        return jsonify({"error": "Email chưa được xác thực. Vui lòng xác thực email trước khi đăng ký."}), 403

    try:
        # Check duplicate
        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email đã tồn tại"}), 409

        user = User(
            email=email,
            password_hash=generate_password_hash(password),
            full_name=full_name or email.split("@")[0],
            role=role,
            is_active=True,
        )
        db.session.add(user)
        db.session.commit()

        # Ensure role sub-record
        _get_or_create_role_row(user.id, role)

        instructor_id = None
        student_id = None
        if role == "instructor":
            inst = Instructor.query.filter_by(user_id=user.id).first()
            instructor_id = inst.id if inst else None
        if role == "student":
            stu = Student.query.filter_by(user_id=user.id).first()
            student_id = stu.id if stu else None

        # Create token with user_id as string identity, but add role in additional claims
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={"role": role}
        )
        next_route = _role_redirect_path(role)
        
        # Debug: Log full token
        print(f"\n{'='*80}")
        print(f"✅ REGISTER - Token created:")
        print(f"   Full Token: {access_token}")
        print(f"   Identity (user_id): {user.id}")
        print(f"   Role (claim): {role}")
        print(f"{'='*80}\n")
        
        # ✅ Clear OTP after successful registration
        from app.routes.EmailVerification import clear_otp
        clear_otp(email)
        
        return jsonify({
            "access_token": access_token,
            "user": {
                "id": user.id,
                "email": user.email,
                "role": role,
                "full_name": user.full_name,
                "instructorId": instructor_id,
                "studentId": student_id,
            },
            "nextRoute": next_route,
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error register: {e}")
        return jsonify({"error": "Server error"}), 500


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "Email và password là bắt buộc"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Sai email hoặc mật khẩu"}), 401

    stored = user.password_hash or ""
    ok = False
    # Try Werkzeug hash first
    try:
        ok = check_password_hash(stored, password)
    except Exception:
        ok = False
    # Fallback: bcrypt stored hashes ($2a/$2b/$2y$)
    if not ok and stored.startswith(("$2a$", "$2b$", "$2y$")):
        try:
            ok = bcrypt.checkpw(password.encode("utf-8"), stored.encode("utf-8"))
        except Exception:
            ok = False
    # Legacy: plain text (no $ markers)
    if not ok and "$" not in stored:
        ok = (password == stored)

    if not ok:
        return jsonify({"error": "Sai email hoặc mật khẩu"}), 401

    # Resolve role based on sub-tables to be consistent
    role = _resolve_role(user)
    # Create token with user_id as string identity, but add role in additional claims
    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": role}
    )
    next_route = _role_redirect_path(role)
    
    # Debug: Log full token
    print(f"\n{'='*80}")
    print(f"✅ LOGIN - Token created:")
    print(f"   Full Token: {access_token}")
    print(f"   Identity (user_id): {user.id}")
    print(f"   Role (claim): {role}")
    print(f"   Email: {user.email}")
    print(f"{'='*80}\n")

    instructor_id = None
    student_id = None
    if role == "instructor":
        inst = Instructor.query.filter_by(user_id=user.id).first()
        instructor_id = inst.id if inst else None
    if role == "student":
        stu = Student.query.filter_by(user_id=user.id).first()
        student_id = stu.id if stu else None

    return jsonify({
        "access_token": access_token,
        "user": {
            "id": user.id,
            "email": user.email,
            "role": role,
            "full_name": user.full_name,
            "instructorId": instructor_id,
            "studentId": student_id,
        },
        "nextRoute": next_route,
    })


@auth_bp.get("/me")
@jwt_required()
def me():
    user_id = get_jwt_identity()  # Now it's a string
    user_id = int(user_id) if isinstance(user_id, str) else user_id
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Not found"}), 404
    
    claims = get_jwt()
    role = claims.get('role', 'student')
    
    return jsonify({"user": {"id": user.id, "email": user.email, "role": role}})


@auth_bp.post("/logout")
@jwt_required()
def logout():
    return jsonify({"message": "Logged out (client remove token)"}), 200


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    try:
        data = request.get_json() or {}
        email = (data.get('email') or '').strip().lower()
        if not email:
            return jsonify({ 'success': False, 'error': 'Email is required' }), 400

        user = User.query.filter(db.func.lower(User.email) == email).first()
        if not user:
            # Do not reveal user existence for security
            # Still return success to prevent email enumeration
            return jsonify({ 'success': True, 'message': 'If the email exists, a reset link has been sent.' }), 200

        # Create token
        token = secrets.token_urlsafe(32)
        expires = datetime.utcnow() + timedelta(hours=1)
        prt = PasswordResetToken(user_id=user.id, token=token, expires_at=expires)
        db.session.add(prt)
        db.session.commit()

        # Generate reset link (update with frontend URL)
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
        reset_link = f"{frontend_url}/reset-password?token={token}"
        
        # Send reset password email
        user_name = user.full_name or user.email.split('@')[0]
        email_sent = send_reset_password_email(user.email, reset_link, user_name)
        
        if email_sent:
            print(f"✅ Password reset email sent successfully to {user.email}")
        else:
            print(f"⚠️ Failed to send password reset email to {user.email}")

        # Return success with message
        response = { 
            'success': True, 
            'message': 'If the email exists, a reset link has been sent to your email.'
        }
        
        # Include reset link in development mode for testing
        if os.getenv('DEBUG') == 'True' or os.getenv('FLASK_ENV') == 'development':
            response['resetLink'] = reset_link
            response['token'] = token
        
        return jsonify(response), 200
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error in forgot_password: {e}")
        return jsonify({ 'success': False, 'error': 'Server error' }), 500


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    try:
        data = request.get_json() or {}
        token = data.get('token')
        new_password = data.get('newPassword')
        if not token or not new_password:
            return jsonify({ 'success': False, 'error': 'Token and newPassword are required' }), 400

        prt = PasswordResetToken.query.filter_by(token=token).first()
        if not prt:
            return jsonify({ 'success': False, 'error': 'Invalid token' }), 400
        if prt.used_at:
            return jsonify({ 'success': False, 'error': 'Token already used' }), 400
        if prt.expires_at < datetime.utcnow():
            return jsonify({ 'success': False, 'error': 'Token expired' }), 400

        user = User.query.get(prt.user_id)
        if not user:
            return jsonify({ 'success': False, 'error': 'User not found' }), 400

        # Hash password (use proper hashing in production, e.g., werkzeug.security)
        from werkzeug.security import generate_password_hash
        user.password_hash = generate_password_hash(new_password)
        prt.used_at = datetime.utcnow()
        db.session.commit()
        return jsonify({ 'success': True }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({ 'success': False, 'error': 'Server error' }), 500


# Helper function to send password reset email
def send_reset_password_email(to_email, reset_link, user_name):
    """Send password reset link via Gmail SMTP"""
    try:
        # Get email credentials from environment
        smtp_email = os.getenv('SMTP_EMAIL') or os.getenv('GMAIL_USER')
        smtp_password = os.getenv('SMTP_PASSWORD') or os.getenv('GMAIL_APP_PASSWORD')
        
        if not smtp_email or not smtp_password:
            print("⚠️ SMTP credentials not configured. Email will not be sent.")
            return False
        
        # Create email message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Reset Your Password - CodeCourse'
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
                .button {{ display: inline-block; background: #3b82f6; color: white; padding: 15px 30px; text-decoration: none; border-radius: 6px; font-weight: bold; margin: 20px 0; }}
                .button:hover {{ background: #2563eb; }}
                .link-box {{ background: white; border: 1px solid #d1d5db; padding: 15px; margin: 20px 0; border-radius: 6px; word-break: break-all; }}
                .footer {{ text-align: center; color: #666; font-size: 14px; margin-top: 20px; }}
                .warning {{ background: #fef3c7; border-left: 4px solid #f59e0b; padding: 12px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 Reset Your Password</h1>
                </div>
                <div class="content">
                    <p>Hi {user_name},</p>
                    <p>We received a request to reset your password for your CodeCourse account. Click the button below to create a new password:</p>
                    
                    <div style="text-align: center;">
                        <a href="{reset_link}" class="button">Reset Password</a>
                    </div>
                    
                    <p>Or copy and paste this link into your browser:</p>
                    <div class="link-box">
                        {reset_link}
                    </div>
                    
                    <div class="warning">
                        <strong>⚠️ Important:</strong> This link will expire in 1 hour. For your security, do not share this link with anyone.
                    </div>
                    
                    <p>If you didn't request a password reset, please ignore this email or contact support if you have concerns.</p>
                    
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
        
        print(f"✅ Password reset email sent to {to_email}")
        return True
    except Exception as e:
        print(f"❌ Error sending password reset email: {e}")
        return False


