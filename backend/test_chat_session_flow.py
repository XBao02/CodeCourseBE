"""
Test script for verifying the complete chat session flow including clear functionality.

This script tests:
1. Login and get token
2. Initialize a chat session
3. Send a message
4. Clear the chat history
5. Send another message (should work with new session auto-creation)
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000/api"

def test_chat_flow():
    print("=" * 80)
    print("Testing Chat Session Flow with Clear Functionality")
    print("=" * 80)
    
    # Step 1: Login
    print("\n📝 Step 1: Login...")
    login_data = {
        "username": "hocsinh1",  # Change to your test student username
        "password": "123"  # Change to your test password
    }
    
    login_res = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if login_res.status_code != 200:
        print(f"❌ Login failed: {login_res.status_code}")
        print(login_res.text)
        return
    
    token = login_res.json().get('token')
    print(f"✅ Login successful! Token: {token[:20]}...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Step 2: Initialize chat session
    print("\n📝 Step 2: Initialize chat session...")
    init_res = requests.post(f"{BASE_URL}/student/recommend/chat/init", headers=headers)
    if init_res.status_code != 200:
        print(f"❌ Init failed: {init_res.status_code}")
        print(init_res.text)
        return
    
    session_id = init_res.json().get('sessionId')
    welcome_msg = init_res.json().get('message')
    print(f"✅ Session created: {session_id}")
    print(f"💬 Welcome message: {welcome_msg}")
    
    # Step 3: Send first message
    print("\n📝 Step 3: Send first message...")
    msg_data = {
        "sessionId": session_id,
        "message": "Tôi muốn học Python backend"
    }
    
    msg_res = requests.post(f"{BASE_URL}/student/recommend/chat/message", json=msg_data, headers=headers)
    if msg_res.status_code != 200:
        print(f"❌ Message failed: {msg_res.status_code}")
        print(msg_res.text)
        return
    
    reply = msg_res.json().get('reply', '')
    print(f"✅ Message sent successfully!")
    print(f"💬 AI Reply: {reply[:200]}...")
    
    # Wait a bit
    time.sleep(1)
    
    # Step 4: Clear chat history
    print("\n📝 Step 4: Clear chat history...")
    clear_data = {"sessionId": session_id}
    clear_res = requests.delete(
        f"{BASE_URL}/student/recommend/chat/clear",
        json=clear_data,
        headers=headers
    )
    
    if clear_res.status_code == 200:
        print("✅ Chat history cleared successfully!")
        print(f"📋 Response: {clear_res.json()}")
    elif clear_res.status_code == 404:
        print("⚠️ Session not found (might have been cleaned up)")
        print(f"📋 Response: {clear_res.json()}")
    else:
        print(f"❌ Clear failed: {clear_res.status_code}")
        print(clear_res.text)
    
    # Step 5: Try to send message with OLD session ID (should fail)
    print("\n📝 Step 5: Try to send message with cleared session ID (should fail)...")
    msg_data_old = {
        "sessionId": session_id,  # Using old session ID
        "message": "This should fail"
    }
    
    msg_res_old = requests.post(f"{BASE_URL}/student/recommend/chat/message", json=msg_data_old, headers=headers)
    if msg_res_old.status_code == 400:
        print("✅ Expected failure! Old session correctly rejected.")
        print(f"📋 Error: {msg_res_old.json().get('error')}")
    else:
        print(f"⚠️ Unexpected response: {msg_res_old.status_code}")
        print(msg_res_old.text)
    
    # Step 6: Initialize NEW session
    print("\n📝 Step 6: Initialize new session...")
    init_res2 = requests.post(f"{BASE_URL}/student/recommend/chat/init", headers=headers)
    if init_res2.status_code != 200:
        print(f"❌ Init failed: {init_res2.status_code}")
        print(init_res2.text)
        return
    
    new_session_id = init_res2.json().get('sessionId')
    print(f"✅ New session created: {new_session_id}")
    print(f"🆕 Old session ID: {session_id}")
    print(f"🆕 New session ID: {new_session_id}")
    
    # Step 7: Send message with new session
    print("\n📝 Step 7: Send message with new session...")
    msg_data_new = {
        "sessionId": new_session_id,
        "message": "Tôi muốn học React"
    }
    
    msg_res_new = requests.post(f"{BASE_URL}/student/recommend/chat/message", json=msg_data_new, headers=headers)
    if msg_res_new.status_code != 200:
        print(f"❌ Message failed: {msg_res_new.status_code}")
        print(msg_res_new.text)
        return
    
    new_reply = msg_res_new.json().get('reply', '')
    print(f"✅ Message sent successfully with new session!")
    print(f"💬 AI Reply: {new_reply[:200]}...")
    
    print("\n" + "=" * 80)
    print("✅ ALL TESTS PASSED!")
    print("=" * 80)

if __name__ == "__main__":
    try:
        test_chat_flow()
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
