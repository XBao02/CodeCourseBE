"""
Script để test JWT token
"""
import requests
import json

BASE_URL = "http://localhost:5000/api"

# 1. Login để lấy token
print("📝 Test 1: Login và lấy token")
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "email": "dinhminhcong678@gmail.com",  # Thay bằng email student của bạn
        "password": "123456"  # Thay bằng password
    }
)

if login_response.status_code == 200:
    data = login_response.json()
    token = data.get("access_token")
    user = data.get("user", {})
    
    print(f"✅ Login thành công!")
    print(f"   - Token: {token[:50]}..." if token else "   - Token: None")
    print(f"   - User: {user.get('email')} (Role: {user.get('role')})")
    print(f"   - Student ID: {user.get('studentId')}")
    
    # 2. Test gọi API với token
    if token:
        print("\n📝 Test 2: Gọi /api/student/register với token")
        headers = {"Authorization": f"Bearer {token}"}
        register_response = requests.post(
            f"{BASE_URL}/student/register",
            json={"courseId": 1},  # Thay bằng course ID thực tế
            headers=headers
        )
        
        print(f"   - Status: {register_response.status_code}")
        print(f"   - Response: {register_response.json()}")
else:
    print(f"❌ Login thất bại: {login_response.status_code}")
    print(f"   - Error: {login_response.json()}")
