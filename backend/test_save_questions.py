"""
Debug script to test AI Quiz save functionality
Run: python test_save_questions.py
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_create_test():
    """Test creating a test"""
    print("\n" + "="*60)
    print("TEST 1: Create Test")
    print("="*60)
    
    payload = {
        "title": "Debug Test - Vòng lặp for",
        "timeLimitMinutes": 15,
        "attemptsAllowed": 1,
        "isPlacement": False
    }
    
    print(f"\n📝 URL: POST {BASE_URL}/api/lessons/1/tests")
    print(f"📝 Payload: {json.dumps(payload, indent=2)}")
    
    try:
        res = requests.post(
            f"{BASE_URL}/api/lessons/1/tests",
            json=payload,
            timeout=10
        )
        
        print(f"\n✅ Status: {res.status_code}")
        print(f"📋 Headers: {dict(res.headers)}")
        
        try:
            data = res.json()
            print(f"\n📊 Response:")
            print(json.dumps(data, indent=2))
            
            if res.status_code == 201:
                print(f"\n✅ SUCCESS! Test ID: {data.get('id')}")
                return data.get('id')
            else:
                print(f"\n❌ FAILED: {data.get('message')}")
                return None
        except json.JSONDecodeError as e:
            text = res.text
            print(f"\n❌ Invalid JSON response:")
            print(f"Content-Type: {res.headers.get('content-type')}")
            print(f"Body: {text[:500]}")
            return None
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return None


def test_create_question(test_id):
    """Test creating a question"""
    if not test_id:
        print("\n⚠️  Skipping - no test_id")
        return
    
    print("\n" + "="*60)
    print("TEST 2: Create Question")
    print("="*60)
    
    payload = {
        "type": "single_choice",
        "content": "Vòng lặp for được sử dụng để làm gì?",
        "points": 1,
        "choices": [
            {
                "content": "Lặp lại một khối mã nhiều lần",
                "is_correct": True,
                "sort_order": 0
            },
            {
                "content": "Khai báo một biến",
                "is_correct": False,
                "sort_order": 1
            },
            {
                "content": "Nhập dữ liệu từ người dùng",
                "is_correct": False,
                "sort_order": 2
            },
            {
                "content": "Tính toán một giá trị",
                "is_correct": False,
                "sort_order": 3
            }
        ]
    }
    
    print(f"\n📝 URL: POST {BASE_URL}/api/tests/{test_id}/questions")
    print(f"📝 Payload: {json.dumps(payload, indent=2)}")
    
    try:
        res = requests.post(
            f"{BASE_URL}/api/tests/{test_id}/questions",
            json=payload,
            timeout=10
        )
        
        print(f"\n✅ Status: {res.status_code}")
        
        try:
            data = res.json()
            print(f"\n📊 Response:")
            print(json.dumps(data, indent=2))
            
            if res.status_code == 201:
                print(f"\n✅ SUCCESS! Question ID: {data.get('id')}")
                return True
            else:
                print(f"\n❌ FAILED: {data.get('message')}")
                return False
        except json.JSONDecodeError as e:
            text = res.text
            print(f"\n❌ Invalid JSON response:")
            print(f"Content-Type: {res.headers.get('content-type')}")
            print(f"Body: {text[:500]}")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False


if __name__ == "__main__":
    print("\n🧪 AI QUIZ SAVE QUESTIONS TEST\n")
    print("Make sure:")
    print("  1. Backend is running: python app.py")
    print("  2. Lesson with ID=1 exists in database")
    print("  3. Internet connection available\n")
    
    # Test 1: Create test
    test_id = test_create_test()
    
    # Test 2: Create question
    if test_id:
        success = test_create_question(test_id)
        
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print("✅ Create Test: PASS")
        print(f"✅ Create Question: {'PASS' if success else 'FAIL'}")
    else:
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print("❌ Create Test: FAIL")
        print("⏭️  Skipped: Create Question")
    
    print("="*60)
