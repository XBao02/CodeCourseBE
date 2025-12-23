"""
Test script for AI Course Recommendation Chat
Tests the /api/student/recommend/chat endpoints
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_recommendation_chat():
    print("=" * 60)
    print("Testing AI Course Recommendation Chat")
    print("=" * 60)
    
    # Step 1: Initialize chat session
    print("\n1. Initializing chat session...")
    init_response = requests.post(f"{BASE_URL}/api/student/recommend/chat/init")
    
    if init_response.status_code != 200:
        print(f"❌ Init failed: {init_response.status_code}")
        print(init_response.text)
        return
    
    init_data = init_response.json()
    if not init_data.get('success'):
        print(f"❌ Init failed: {init_data}")
        return
    
    session_id = init_data.get('sessionId')
    intro_message = init_data.get('message')
    print(f"✅ Session created: {session_id}")
    print(f"📝 Intro: {intro_message}")
    
    # Step 2: Send a test message
    print("\n2. Sending test message...")
    test_messages = [
        "Tôi muốn học lập trình backend với Python",
        "I want to learn data science and machine learning",
        "Tôi muốn cải thiện kỹ năng thuật toán để phỏng vấn"
    ]
    
    for i, user_message in enumerate(test_messages[:1], 1):  # Test with first message only
        print(f"\n   Test {i}: '{user_message}'")
        
        message_response = requests.post(
            f"{BASE_URL}/api/student/recommend/chat/message",
            json={
                "sessionId": session_id,
                "message": user_message
            }
        )
        
        if message_response.status_code != 200:
            print(f"   ❌ Message failed: {message_response.status_code}")
            print(f"   Response: {message_response.text}")
            continue
        
        message_data = message_response.json()
        if not message_data.get('success'):
            print(f"   ❌ Message failed: {message_data}")
            continue
        
        print(f"   ✅ Response received")
        print(f"   📝 AI Reply: {message_data.get('reply', '')[:200]}...")
        
        courses = message_data.get('coursesWithReasons', [])
        print(f"   📚 Recommended Courses: {len(courses)}")
        for j, item in enumerate(courses[:3], 1):
            course = item.get('course', {})
            reason = item.get('reason', 'No reason provided')
            print(f"      {j}. {course.get('title', 'N/A')} ({course.get('level', 'N/A')})")
            print(f"         Reason: {reason[:100]}...")
        
        follow_up = message_data.get('followUp')
        if follow_up:
            print(f"   💬 Follow-up: {follow_up}")
    
    print("\n" + "=" * 60)
    print("✅ Test completed successfully!")
    print("=" * 60)

def test_error_cases():
    print("\n" + "=" * 60)
    print("Testing Error Cases")
    print("=" * 60)
    
    # Test 1: Invalid session
    print("\n1. Testing invalid session...")
    response = requests.post(
        f"{BASE_URL}/api/student/recommend/chat/message",
        json={
            "sessionId": "invalid-session-id",
            "message": "Hello"
        }
    )
    if response.status_code == 400:
        print("   ✅ Correctly rejected invalid session (400)")
    else:
        print(f"   ❌ Expected 400, got {response.status_code}")
    
    # Test 2: Empty message
    print("\n2. Testing empty message...")
    init_response = requests.post(f"{BASE_URL}/api/student/recommend/chat/init")
    session_id = init_response.json().get('sessionId')
    
    response = requests.post(
        f"{BASE_URL}/api/student/recommend/chat/message",
        json={
            "sessionId": session_id,
            "message": ""
        }
    )
    if response.status_code == 400:
        print("   ✅ Correctly rejected empty message (400)")
    else:
        print(f"   ❌ Expected 400, got {response.status_code}")
    
    print("\n" + "=" * 60)
    print("✅ Error case tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        print("\n🚀 Starting AI Recommendation Chat Tests\n")
        test_recommendation_chat()
        test_error_cases()
        print("\n🎉 All tests completed!\n")
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to server at", BASE_URL)
        print("Make sure the backend server is running (python backend/app.py)\n")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n")
        import traceback
        traceback.print_exc()
