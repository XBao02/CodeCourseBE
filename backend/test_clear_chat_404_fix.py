"""
Quick test to verify the 404 clear chat fix.
Tests that clearing a non-existent session returns success.
"""

import requests
import json

BASE_URL = "http://localhost:5000/api"

def test_clear_nonexistent_session():
    print("=" * 80)
    print("Testing Clear Non-Existent Session (Should Return Success)")
    print("=" * 80)
    
    # Step 1: Login
    print("\n📝 Step 1: Login...")
    login_data = {
        "username": "hocsinh1",
        "password": "123"
    }
    
    login_res = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if login_res.status_code != 200:
        print(f"❌ Login failed: {login_res.status_code}")
        return
    
    token = login_res.json().get('token')
    print(f"✅ Login successful!")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Step 2: Try to clear a fake/non-existent session
    print("\n📝 Step 2: Clear a non-existent session...")
    fake_session_id = "fake-session-id-12345"
    clear_data = {"sessionId": fake_session_id}
    
    clear_res = requests.delete(
        f"{BASE_URL}/student/recommend/chat/clear",
        json=clear_data,
        headers=headers
    )
    
    print(f"📊 Status Code: {clear_res.status_code}")
    print(f"📋 Response: {json.dumps(clear_res.json(), indent=2)}")
    
    # Step 3: Verify it returns success
    if clear_res.status_code == 200:
        if clear_res.json().get('success'):
            print("\n✅ TEST PASSED: Non-existent session returns success!")
            print("✅ Backend correctly handles missing sessions")
            
            if clear_res.json().get('wasAlreadyCleared'):
                print("✅ Backend indicates session was already cleared")
        else:
            print("\n❌ TEST FAILED: Response says success=False")
    else:
        print(f"\n❌ TEST FAILED: Expected 200, got {clear_res.status_code}")
    
    # Step 4: Create a real session and clear it
    print("\n📝 Step 3: Create a real session...")
    init_res = requests.post(f"{BASE_URL}/student/recommend/chat/init", headers=headers)
    
    if init_res.status_code == 200:
        session_id = init_res.json().get('sessionId')
        print(f"✅ Session created: {session_id}")
        
        # Clear the real session
        print("\n📝 Step 4: Clear the real session...")
        clear_data2 = {"sessionId": session_id}
        clear_res2 = requests.delete(
            f"{BASE_URL}/student/recommend/chat/clear",
            json=clear_data2,
            headers=headers
        )
        
        print(f"📊 Status Code: {clear_res2.status_code}")
        print(f"📋 Response: {json.dumps(clear_res2.json(), indent=2)}")
        
        if clear_res2.status_code == 200 and clear_res2.json().get('success'):
            print("✅ Real session cleared successfully")
            
            # Try to clear it again
            print("\n📝 Step 5: Try to clear the same session again...")
            clear_res3 = requests.delete(
                f"{BASE_URL}/student/recommend/chat/clear",
                json=clear_data2,
                headers=headers
            )
            
            print(f"📊 Status Code: {clear_res3.status_code}")
            print(f"📋 Response: {json.dumps(clear_res3.json(), indent=2)}")
            
            if clear_res3.status_code == 200 and clear_res3.json().get('success'):
                print("✅ Clearing already-cleared session also returns success!")
                print("✅ IDEMPOTENT OPERATION WORKS CORRECTLY!")
            else:
                print("❌ Clearing already-cleared session failed")
    
    print("\n" + "=" * 80)
    print("✅ ALL TESTS COMPLETED!")
    print("=" * 80)

if __name__ == "__main__":
    try:
        test_clear_nonexistent_session()
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
