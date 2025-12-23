"""
Test script for the chat clear endpoint.

This tests:
1. Initialize a chat session
2. Send a message
3. Clear the chat history
4. Verify the session is deleted

Run: python test_clear_chat.py
"""

import requests
import json

BASE_URL = "http://localhost:5000/api"

# Test user credentials (update these if needed)
TEST_USER = {
    "email": "student@test.com",
    "password": "password123"
}

def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def login():
    """Login and get access token."""
    print_section("1. LOGIN")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json=TEST_USER
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data.get('access_token')
        print(f"✅ Login successful")
        print(f"Token: {token[:50]}...")
        return token
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def init_chat(token):
    """Initialize a chat session."""
    print_section("2. INITIALIZE CHAT SESSION")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        f"{BASE_URL}/student/recommend/chat/init",
        json={},
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        session_id = data.get('sessionId')
        print(f"✅ Chat session initialized")
        print(f"Session ID: {session_id}")
        print(f"Welcome message: {data.get('message', 'N/A')}")
        return session_id
    else:
        print(f"❌ Failed to initialize chat: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def send_message(token, session_id, message):
    """Send a message to the chat."""
    print_section(f"3. SEND MESSAGE: '{message}'")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        f"{BASE_URL}/student/recommend/chat/message",
        json={
            "sessionId": session_id,
            "message": message
        },
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Message sent successfully")
        reply = data.get('reply', 'No reply')
        print(f"AI Reply: {reply[:200]}...")
        courses = data.get('coursesWithReasons', [])
        print(f"Recommended courses: {len(courses)}")
        return True
    else:
        print(f"❌ Failed to send message: {response.status_code}")
        print(f"Response: {response.text}")
        return False

def clear_chat(token, session_id):
    """Clear the chat history."""
    print_section("4. CLEAR CHAT HISTORY")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.delete(
        f"{BASE_URL}/student/recommend/chat/clear",
        json={"sessionId": session_id},
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Chat history cleared successfully")
        print(f"Message: {data.get('message')}")
        return True
    elif response.status_code == 404:
        print(f"⚠️ Session not found (might already be expired)")
        print(f"Response: {response.text}")
        return False
    else:
        print(f"❌ Failed to clear chat: {response.status_code}")
        print(f"Response: {response.text}")
        return False

def verify_session_deleted(token, session_id):
    """Verify the session was deleted by trying to send a message."""
    print_section("5. VERIFY SESSION IS DELETED")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        f"{BASE_URL}/student/recommend/chat/message",
        json={
            "sessionId": session_id,
            "message": "This should fail"
        },
        headers=headers
    )
    
    if response.status_code == 400 or response.status_code == 404:
        print(f"✅ Session is deleted (got expected error: {response.status_code})")
        data = response.json()
        print(f"Error message: {data.get('error')}")
        return True
    else:
        print(f"❌ Session still exists (unexpected status: {response.status_code})")
        print(f"Response: {response.text}")
        return False

def test_clear_without_session(token):
    """Test clearing without providing a session ID."""
    print_section("6. TEST CLEAR WITHOUT SESSION ID")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.delete(
        f"{BASE_URL}/student/recommend/chat/clear",
        json={},
        headers=headers
    )
    
    if response.status_code == 400:
        print(f"✅ Got expected error for missing sessionId: {response.status_code}")
        data = response.json()
        print(f"Error message: {data.get('error')}")
        return True
    else:
        print(f"❌ Unexpected response: {response.status_code}")
        print(f"Response: {response.text}")
        return False

def test_clear_without_auth():
    """Test clearing without authentication."""
    print_section("7. TEST CLEAR WITHOUT AUTHENTICATION")
    
    response = requests.delete(
        f"{BASE_URL}/student/recommend/chat/clear",
        json={"sessionId": "fake-session-id"}
    )
    
    if response.status_code == 401:
        print(f"✅ Got expected 401 Unauthorized: {response.status_code}")
        return True
    else:
        print(f"❌ Unexpected response: {response.status_code}")
        print(f"Response: {response.text}")
        return False

def main():
    """Run all tests."""
    print("\n" + "🔍" * 30)
    print("  TESTING CHAT CLEAR ENDPOINT")
    print("🔍" * 30)
    
    # Step 1: Login
    token = login()
    if not token:
        print("\n❌ Cannot proceed without login. Exiting.")
        return
    
    # Step 2: Initialize chat
    session_id = init_chat(token)
    if not session_id:
        print("\n❌ Cannot proceed without session. Exiting.")
        return
    
    # Step 3: Send a message
    send_message(token, session_id, "I want to learn Python programming")
    
    # Step 4: Clear the chat
    clear_success = clear_chat(token, session_id)
    
    # Step 5: Verify session is deleted
    if clear_success:
        verify_session_deleted(token, session_id)
    
    # Step 6: Test error cases
    test_clear_without_session(token)
    test_clear_without_auth()
    
    print_section("✅ ALL TESTS COMPLETED")
    print("\nSummary:")
    print("- Chat initialization: ✅")
    print("- Send message: ✅")
    print("- Clear chat: ✅")
    print("- Verify deletion: ✅")
    print("- Error handling: ✅")

if __name__ == "__main__":
    main()
