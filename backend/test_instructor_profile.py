import requests
import json

# Base URL
BASE_URL = "http://localhost:5000"

# Get token (replace with your actual login credentials)
def get_token():
    """Login and get token"""
    login_data = {
        "username": "instructor2@codecourse.com",  # Replace with your instructor username
        "password": "123456"  # Replace with your instructor password
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Login successful!")
        print(f"User: {data.get('user', {}).get('username')}")
        print(f"Role: {data.get('user', {}).get('role')}")
        return data.get('token')
    else:
        print(f"✗ Login failed: {response.status_code}")
        print(response.text)
        return None

def test_instructor_profile(token):
    """Test instructor profile endpoint"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("\n" + "="*50)
    print("Testing /api/instructor/profile")
    print("="*50)
    
    response = requests.get(f"{BASE_URL}/api/instructor/profile", headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✓ Instructor Profile Retrieved Successfully!")
        print(f"  Name: {data.get('full_name')}")
        print(f"  Username: {data.get('username')}")
        print(f"  Email: {data.get('email')}")
        print(f"  Expertise: {data.get('expertise')}")
    else:
        print(f"\n✗ Failed to get instructor profile")

def test_session(token):
    """Test session endpoint"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("\n" + "="*50)
    print("Testing /api/auth/session")
    print("="*50)
    
    response = requests.get(f"{BASE_URL}/api/auth/session", headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✓ Session Retrieved Successfully!")
        print(f"  User: {data.get('user', {}).get('full_name')}")
        print(f"  Role: {data.get('user', {}).get('role')}")
    else:
        print(f"\n✗ Failed to get session")

if __name__ == "__main__":
    print("Testing Instructor Profile API")
    print("="*50)
    
    # Step 1: Get token
    token = get_token()
    if not token:
        print("Cannot proceed without token")
        exit(1)
    
    print(f"\nToken: {token[:50]}...")
    
    # Step 2: Test session endpoint
    test_session(token)
    
    # Step 3: Test instructor profile endpoint
    test_instructor_profile(token)
    
    print("\n" + "="*50)
    print("Test Complete!")
    print("="*50)
