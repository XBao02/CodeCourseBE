"""
Quick test for AI Quiz save functionality
"""
import requests
import json

BASE = "http://localhost:5000"

# Test 1: Create test
print("=" * 60)
print("TEST: Create Test via /api/lessons/{id}/tests")
print("=" * 60)

test_payload = {
    "title": "Test Vòng lặp for",
    "timeLimitMinutes": 15,
    "attemptsAllowed": 1,
    "isPlacement": False
}

print(f"\n📝 POST {BASE}/api/lessons/1/tests")
print(f"Payload: {json.dumps(test_payload, indent=2)}\n")

try:
    res = requests.post(
        f"{BASE}/api/lessons/1/tests",
        json=test_payload,
        timeout=10
    )
    print(f"✅ Status: {res.status_code}")
    print(f"Content-Type: {res.headers.get('content-type')}\n")
    
    data = res.json()
    print(f"Response: {json.dumps(data, indent=2)}\n")
    
    if res.status_code == 201:
        test_id = data.get('id')
        print(f"✅ SUCCESS! Test ID: {test_id}\n")
        
        # Test 2: Create question
        print("=" * 60)
        print("TEST: Create Question via /api/tests/{id}/questions")
        print("=" * 60)
        
        question_payload = {
            "type": "single_choice",
            "content": "Vòng lặp for dùng để làm gì?",
            "points": 1,
            "choices": [
                {"content": "Lặp lại mã", "is_correct": True, "sort_order": 0},
                {"content": "Khai báo biến", "is_correct": False, "sort_order": 1},
                {"content": "Nhập dữ liệu", "is_correct": False, "sort_order": 2},
            ]
        }
        
        print(f"\n📝 POST {BASE}/api/tests/{test_id}/questions")
        print(f"Payload: {json.dumps(question_payload, indent=2)}\n")
        
        qres = requests.post(
            f"{BASE}/api/tests/{test_id}/questions",
            json=question_payload,
            timeout=10
        )
        
        print(f"✅ Status: {qres.status_code}")
        print(f"Content-Type: {qres.headers.get('content-type')}\n")
        
        qdata = qres.json()
        print(f"Response: {json.dumps(qdata, indent=2)}\n")
        
        if qres.status_code == 201:
            print(f"✅ ALL TESTS PASSED!")
        else:
            print(f"❌ Question creation failed")
    else:
        print(f"❌ Test creation failed: {data.get('message')}")
        
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
