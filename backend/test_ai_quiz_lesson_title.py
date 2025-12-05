"""
Quick test script to verify AI Quiz uses lesson title correctly
Run: python test_ai_quiz_lesson_title.py
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.routes.AIQuiz import _generate_quiz_prompt

def test_prompt_includes_lesson_title():
    """Test that the prompt includes lesson title"""
    print("=" * 80)
    print("TEST: AI Quiz Prompt Generation - Lesson Title Check")
    print("=" * 80)
    
    # Test cases with different lesson titles
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
            "lesson_title": "Advanced SQL Joins",
            "num_questions": 7,
            "difficulty": "hard"
        }
    ]
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test Case {i}:")
        print(f"   Lesson Title: '{test_case['lesson_title']}'")
        print(f"   Questions: {test_case['num_questions']}")
        print(f"   Difficulty: {test_case['difficulty']}")
        
        # Generate prompt
        prompt = _generate_quiz_prompt(
            test_case['lesson_title'],
            test_case['num_questions'],
            test_case['difficulty']
        )
        
        # Verify lesson title is in prompt
        if test_case['lesson_title'] in prompt:
            print(f"   ✅ PASS: Lesson title found in prompt")
        else:
            print(f"   ❌ FAIL: Lesson title NOT found in prompt")
            all_passed = False
        
        # Verify difficulty is in prompt
        if test_case['difficulty'] in prompt.lower():
            print(f"   ✅ PASS: Difficulty level found in prompt")
        else:
            print(f"   ❌ FAIL: Difficulty level NOT found in prompt")
            all_passed = False
        
        # Verify number of questions is in prompt
        if str(test_case['num_questions']) in prompt:
            print(f"   ✅ PASS: Number of questions found in prompt")
        else:
            print(f"   ❌ FAIL: Number of questions NOT found in prompt")
            all_passed = False
        
        # Print prompt preview
        print(f"\n   📝 Prompt Preview:")
        print(f"   {'-' * 76}")
        print(f"   {prompt[:250]}...")
        print(f"   {'-' * 76}")
    
    # Final result
    print("\n" + "=" * 80)
    if all_passed:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 80)
    
    return all_passed

if __name__ == "__main__":
    test_prompt_includes_lesson_title()
