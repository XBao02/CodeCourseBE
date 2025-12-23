"""
Test script to verify password reset email functionality
Run: python test_reset_password_email.py
"""

import sys
import os

# Add parent directory to path to import from app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
import requests
import json

# Load environment variables
load_dotenv()

def test_forgot_password():
    """Test the forgot password endpoint"""
    
    print("\n" + "="*80)
    print("🔐 Testing Password Reset Email Functionality")
    print("="*80 + "\n")
    
    # Configuration
    API_URL = "http://localhost:5000/api/auth/forgot-password"
    TEST_EMAIL = "captone149@gmail.com"  # Change this to a valid email in your DB
    
    print(f"📧 Test Email: {TEST_EMAIL}")
    print(f"🌐 API URL: {API_URL}")
    print(f"🔧 SMTP Email: {os.getenv('SMTP_EMAIL')}")
    print(f"🔧 Frontend URL: {os.getenv('FRONTEND_URL')}")
    print(f"🔧 Debug Mode: {os.getenv('DEBUG')}")
    print()
    
    # Check SMTP credentials
    if not os.getenv('SMTP_EMAIL') or not os.getenv('SMTP_PASSWORD'):
        print("❌ ERROR: SMTP credentials not configured!")
        print("   Please set SMTP_EMAIL and SMTP_PASSWORD in .env file")
        return False
    
    print("✅ SMTP credentials configured")
    print()
    
    # Send request
    print("📤 Sending forgot password request...")
    try:
        response = requests.post(
            API_URL,
            json={"email": TEST_EMAIL},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📥 Response Status: {response.status_code}")
        print(f"📥 Response Body:")
        print(json.dumps(response.json(), indent=2))
        print()
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                print("✅ SUCCESS: Request processed successfully")
                print(f"📧 Message: {data.get('message')}")
                
                # If in development mode, show the reset link
                if data.get('resetLink'):
                    print()
                    print("🔗 Reset Link (Development Only):")
                    print(f"   {data['resetLink']}")
                    print()
                    print("💡 In production, this link is only sent via email")
                
                print()
                print("="*80)
                print("📬 Check your email inbox (or spam folder)")
                print("="*80)
                print()
                print("Expected Email:")
                print("  ✉️  Subject: Reset Your Password - CodeCourse")
                print("  📧 From: CodeCourse <captone149@gmail.com>")
                print(f"  👤 To: {TEST_EMAIL}")
                print("  🔘 Contains: 'Reset Password' button")
                print()
                
                return True
            else:
                print(f"❌ FAILED: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to backend server")
        print("   Make sure the Flask server is running:")
        print("   cd backend && python app.py")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_smtp_connection():
    """Test SMTP connection directly"""
    print("\n" + "="*80)
    print("📧 Testing SMTP Connection")
    print("="*80 + "\n")
    
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        smtp_email = os.getenv('SMTP_EMAIL')
        smtp_password = os.getenv('SMTP_PASSWORD')
        
        if not smtp_email or not smtp_password:
            print("❌ SMTP credentials not configured")
            return False
        
        print(f"📧 Connecting to Gmail SMTP...")
        print(f"   Email: {smtp_email}")
        
        # Test connection
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(smtp_email, smtp_password)
            print("✅ SMTP connection successful!")
            print("✅ Gmail login successful!")
            
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("❌ SMTP Authentication Failed!")
        print()
        print("Possible reasons:")
        print("  1. Invalid App Password")
        print("  2. 2-Step Verification not enabled")
        print("  3. Wrong email/password in .env")
        print()
        print("Solution:")
        print("  1. Visit: https://myaccount.google.com/security")
        print("  2. Enable 2-Step Verification")
        print("  3. Visit: https://myaccount.google.com/apppasswords")
        print("  4. Create new App Password")
        print("  5. Update SMTP_PASSWORD in .env")
        return False
        
    except Exception as e:
        print(f"❌ SMTP connection error: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "🔐 Password Reset Email Test Suite" + "\n")
    
    # Test 1: SMTP Connection
    smtp_ok = test_smtp_connection()
    
    if not smtp_ok:
        print("\n⚠️  Fix SMTP connection issues before testing API")
        sys.exit(1)
    
    # Test 2: Forgot Password API
    api_ok = test_forgot_password()
    
    if api_ok:
        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED")
        print("="*80 + "\n")
    else:
        print("\n" + "="*80)
        print("❌ SOME TESTS FAILED")
        print("="*80 + "\n")
        sys.exit(1)
