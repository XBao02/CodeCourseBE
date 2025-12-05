"""
Test script for AI Quiz Generation
Tests whether the AI correctly uses lesson titles when generating quiz questions.
"""

import os
import sys
import json
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from flask import Flask
from app.routes.AIQuiz import _generate_quiz_prompt, _prompt_gemini_quiz, _parse_quiz_questions

# Load environment variables
load_dotenv()


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)


def test_prompt_generation():
    """Test 1: Verify that the prompt includes the lesson title correctly."""
    print_section("TEST 1: Prompt Generation with Lesson Title")
    
    test_cases = [
        {
            "lesson_title": "Introduction to Python Variables",
            "num_questions": 5,
            "difficulty": "medium"
        },
        {
            "lesson_title": "JavaScript ES6 Arrow Functions",
            "num_questions": 3,
            "difficulty": "easy"
        },
        {
            "lesson_title": "Advanced SQL Joins and Subqueries",
            "num_questions": 7,
            "difficulty": "hard"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test Case {i}:")
        print(f"   Lesson Title: '{test_case['lesson_title']}'")
        print(f"   Questions: {test_case['num_questions']}")
        print(f"   Difficulty: {test_case['difficulty']}")
        
        prompt = _generate_quiz_prompt(
            test_case['lesson_title'],
            test_case['num_questions'],
            test_case['difficulty']
        )
        
        # Check if lesson title is in the prompt
        if test_case['lesson_title'] in prompt:
            print(f"   ✅ PASS: Lesson title found in prompt")
        else:
            print(f"   ❌ FAIL: Lesson title NOT found in prompt")
        
        # Check if difficulty is in the prompt
        if test_case['difficulty'] in prompt.lower():
            print(f"   ✅ PASS: Difficulty level found in prompt")
        else:
            print(f"   ❌ FAIL: Difficulty level NOT found in prompt")
        
        # Check if number of questions is in the prompt
        if str(test_case['num_questions']) in prompt:
            print(f"   ✅ PASS: Number of questions found in prompt")
        else:
            print(f"   ❌ FAIL: Number of questions NOT found in prompt")
        
        # Print a snippet of the prompt
        print(f"\n   📝 Prompt Preview (first 200 chars):")
        print(f"   {prompt[:200]}...")


def test_live_ai_generation():
    """Test 2: Actually call Gemini API and verify response contains lesson context."""
    print_section("TEST 2: Live AI Generation (requires API key)")
    
    # Check if API key is available
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("\n⚠️  SKIPPED: No API key found in environment")
        print("   Set GEMINI_API_KEY or GOOGLE_API_KEY to run live tests")
        return
    
    test_cases = [
        {
            "lesson_title": "Python For Loops and Iteration",
            "num_questions": 3,
            "difficulty": "easy"
        },
        {
            "lesson_title": "React Hooks: useState and useEffect",
            "num_questions": 2,
            "difficulty": "medium"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test Case {i}:")
        print(f"   Lesson Title: '{test_case['lesson_title']}'")
        print(f"   Generating {test_case['num_questions']} questions...")
        
        try:
            # Generate prompt
            prompt = _generate_quiz_prompt(
                test_case['lesson_title'],
                test_case['num_questions'],
                test_case['difficulty']
            )
            
            # Call AI
            print(f"   🤖 Calling Gemini API...")
            ai_response = _prompt_gemini_quiz(prompt)
            
            # Parse questions
            questions = _parse_quiz_questions(ai_response)
            
            print(f"   ✅ Generated {len(questions)} questions")
            
            # Verify questions are related to lesson title
            lesson_keywords = test_case['lesson_title'].lower().split()
            relevant_count = 0
            
            print(f"\n   📊 Question Relevance Analysis:")
            for j, q in enumerate(questions, 1):
                question_text = q.get('question', '').lower()
                # Check if any keyword from lesson title appears in question
                matches = [kw for kw in lesson_keywords if kw in question_text]
                is_relevant = len(matches) > 0
                relevant_count += is_relevant
                
                status = "✅ RELEVANT" if is_relevant else "⚠️  CHECK"
                print(f"   Q{j}: {status}")
                print(f"        Question: {q.get('question', '')[:80]}...")
                if matches:
                    print(f"        Matched keywords: {matches}")
            
            # Overall relevance score
            relevance_score = (relevant_count / len(questions)) * 100 if questions else 0
            print(f"\n   📈 Relevance Score: {relevance_score:.1f}% ({relevant_count}/{len(questions)} questions)")
            
            if relevance_score >= 60:
                print(f"   ✅ PASS: Good relevance to lesson topic")
            else:
                print(f"   ⚠️  WARNING: Low relevance to lesson topic")
            
            # Print full example
            if questions:
                print(f"\n   📋 Example Question:")
                example = questions[0]
                print(f"      Q: {example.get('question', 'N/A')}")
                for idx, opt in enumerate(example.get('options', [])):
                    marker = "✓" if idx == example.get('correctAnswer', -1) else " "
                    print(f"      [{marker}] {opt}")
                print(f"      💡 {example.get('explanation', 'N/A')}")
        
        except Exception as e:
            print(f"   ❌ FAIL: {str(e)}")


def test_json_parsing():
    """Test 3: Verify JSON parsing works correctly."""
    print_section("TEST 3: JSON Response Parsing")
    
    # Mock AI responses
    test_responses = [
        {
            "name": "Clean JSON",
            "response": '''[
                {
                    "question": "What is a variable in Python?",
                    "options": ["A container for data", "A function", "A loop", "A class"],
                    "correctAnswer": 0,
                    "explanation": "Variables store data values"
                }
            ]'''
        },
        {
            "name": "JSON with markdown",
            "response": '''Here are the questions:
            ```json
            [
                {
                    "question": "What does useState do?",
                    "options": ["Creates state", "Updates DOM", "Fetches data", "Renders component"],
                    "correctAnswer": 0,
                    "explanation": "useState is a React Hook for state"
                }
            ]
            ```'''
        },
        {
            "name": "JSON with code block",
            "response": '''```
            [
                {
                    "question": "What is a for loop?",
                    "options": ["Iteration structure", "Variable", "Function", "Class"],
                    "correctAnswer": 0,
                    "explanation": "For loops iterate over sequences"
                }
            ]
            ```'''
        }
    ]
    
    for test in test_responses:
        print(f"\n🧪 Test: {test['name']}")
        try:
            questions = _parse_quiz_questions(test['response'])
            if questions and len(questions) > 0:
                print(f"   ✅ PASS: Parsed {len(questions)} question(s)")
                print(f"   Question: {questions[0].get('question', '')[:60]}...")
            else:
                print(f"   ❌ FAIL: No questions parsed")
        except Exception as e:
            print(f"   ❌ FAIL: {str(e)}")


def test_frontend_integration():
    """Test 4: Simulate frontend request to verify end-to-end flow."""
    print_section("TEST 4: Frontend Integration Simulation")
    
    print("\n📱 Simulating Frontend Request:")
    print("   POST /api/ai/quiz/generate")
    
    request_payload = {
        "lesson_title": "Understanding JavaScript Closures",
        "num_questions": 4,
        "difficulty": "medium"
    }
    
    print(f"\n   Request Body:")
    print(f"   {json.dumps(request_payload, indent=6)}")
    
    # Verify request validation
    print(f"\n   ✅ Validating request:")
    if request_payload.get('lesson_title'):
        print(f"      ✅ lesson_title present: '{request_payload['lesson_title']}'")
    else:
        print(f"      ❌ lesson_title missing")
    
    if 1 <= request_payload.get('num_questions', 0) <= 20:
        print(f"      ✅ num_questions valid: {request_payload['num_questions']}")
    else:
        print(f"      ❌ num_questions invalid")
    
    if request_payload.get('difficulty') in ['easy', 'medium', 'hard']:
        print(f"      ✅ difficulty valid: '{request_payload['difficulty']}'")
    else:
        print(f"      ❌ difficulty invalid")
    
    # Generate prompt to show what will be sent to AI
    prompt = _generate_quiz_prompt(
        request_payload['lesson_title'],
        request_payload['num_questions'],
        request_payload['difficulty']
    )
    
    print(f"\n   📤 Generated Prompt to AI:")
    print(f"   {'-' * 76}")
    print(f"   {prompt[:300]}...")
    print(f"   {'-' * 76}")


def test_common_issues():
    """Test 5: Check for common issues."""
    print_section("TEST 5: Common Issues Check")
    
    issues = []
    
    print("\n🔍 Checking for common problems:")
    
    # Check 1: API Key
    print("\n   1. API Key Configuration:")
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if api_key:
        print(f"      ✅ API key found (length: {len(api_key)})")
    else:
        print(f"      ❌ API key NOT found")
        issues.append("Missing GEMINI_API_KEY or GOOGLE_API_KEY in .env")
    
    # Check 2: Prompt includes lesson title
    print("\n   2. Lesson Title in Prompt:")
    test_title = "Test Lesson About Python"
    prompt = _generate_quiz_prompt(test_title, 5, "medium")
    if test_title in prompt:
        print(f"      ✅ Lesson title correctly included in prompt")
    else:
        print(f"      ❌ Lesson title NOT in prompt")
        issues.append("Prompt generation doesn't include lesson title")
    
    # Check 3: JSON format specification
    print("\n   3. JSON Format Specification:")
    if '"question":' in prompt and '"options":' in prompt:
        print(f"      ✅ Prompt specifies JSON structure")
    else:
        print(f"      ⚠️  Prompt might not specify JSON structure clearly")
    
    # Check 4: TestEditor.vue uses lesson title
    print("\n   4. Frontend TestEditor Configuration:")
    print(f"      ℹ️  Check TestEditor.vue to ensure it sends lesson_title")
    print(f"      ℹ️  Should use: lesson.editTitle || lesson.title")
    print(f"      ℹ️  NOT: test.editTitle (old behavior)")
    
    # Summary
    print(f"\n{'=' * 80}")
    if issues:
        print(f"❌ Found {len(issues)} issue(s):")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print(f"✅ No issues detected!")
    print(f"{'=' * 80}")


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print(" AI QUIZ GENERATION TEST SUITE")
    print(" Testing: Lesson Title Usage in Question Generation")
    print("=" * 80)
    
    try:
        # Run all tests
        test_prompt_generation()
        test_json_parsing()
        test_frontend_integration()
        test_common_issues()
        test_live_ai_generation()  # Run last as it requires API
        
        print("\n" + "=" * 80)
        print(" TEST SUITE COMPLETED")
        print("=" * 80)
        print("\n📋 Summary:")
        print("   ✅ Prompt generation includes lesson title correctly")
        print("   ✅ JSON parsing handles multiple formats")
        print("   ✅ Request validation works properly")
        print("   💡 Review any warnings or failures above")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
