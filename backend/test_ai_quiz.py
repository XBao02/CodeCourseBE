"""
Simple test script to verify AI Quiz API is working
Run this from backend folder: python test_ai_quiz.py
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_generate_quiz():
    """Test quiz generation endpoint"""
    print("=" * 60)
    print("Testing AI Quiz Generate Endpoint")
    print("=" * 60)
    
    payload = {
        "lesson_title": "Vòng lặp for trong Python",
        "num_questions": 3,
        "difficulty": "medium"
    }
    
    print(f"\n📝 Request URL: {BASE_URL}/api/ai/quiz/generate")
    print(f"📝 Request Body: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/ai/quiz/generate",
            json=payload,
            timeout=30
        )
        
        print(f"\n✅ Response Status: {response.status_code}")
        
        data = response.json()
        print(f"\n📊 Response:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        if response.status_code == 200 and data.get("questions"):
            print(f"\n✅ SUCCESS! Generated {len(data['questions'])} questions")
            return True
        else:
            error = data.get("error", "Unknown error")
            print(f"\n❌ FAILED: {error}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("\n❌ CONNECTION ERROR")
        print("   Make sure backend is running: python app.py")
        return False
    except requests.exceptions.Timeout:
        print("\n❌ TIMEOUT ERROR")
        print("   API took too long to respond (check Gemini API)")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False

def test_validate_answer():
    """Test answer validation endpoint"""
    print("\n" + "=" * 60)
    print("Testing Answer Validation Endpoint")
    print("=" * 60)
    
    payload = {
        "user_answer": 2,
        "correct_answer": 1
    }
    
    print(f"\n📝 Request URL: {BASE_URL}/api/ai/quiz/validate")
    print(f"📝 Request Body: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/ai/quiz/validate",
            json=payload,
            timeout=10
        )
        
        print(f"\n✅ Response Status: {response.status_code}")
        data = response.json()
        print(f"\n📊 Response:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        if response.status_code == 200:
            print(f"\n✅ SUCCESS!")
            return True
        else:
            print(f"\n❌ FAILED")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    print("\n🧪 AI QUIZ API TEST SCRIPT\n")
    
    print("⏳ Make sure:")
    print("   1. Backend is running: python app.py")
    print("   2. .env file has GEMINI_API_KEY set")
    print("   3. Internet connection is available\n")
    
    quiz_ok = test_generate_quiz()
    validate_ok = test_validate_answer()
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Quiz Generation: {'✅ PASS' if quiz_ok else '❌ FAIL'}")
    print(f"Answer Validation: {'✅ PASS' if validate_ok else '❌ FAIL'}")
    print("=" * 60)
    
    if quiz_ok and validate_ok:
        print("\n🎉 All tests passed! API is ready to use.")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
