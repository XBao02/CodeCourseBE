"""
Quick test for AI Quiz Generation - Lesson Title Verification
Run this to quickly verify the lesson title is used correctly.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from app.routes.AIQuiz import _generate_quiz_prompt

load_dotenv()


def main():
    print("\n" + "="*70)
    print("🧪 QUICK TEST: AI Quiz Lesson Title Usage")
    print("="*70)
    
    # Test different lesson titles
    test_lessons = [
        "Introduction to Python Variables",
        "JavaScript Arrow Functions",
        "React useState Hook",
        "SQL JOIN Operations",
        "CSS Flexbox Layout"
    ]
    
    print("\n✅ Testing if lesson titles are included in AI prompts:\n")
    
    all_passed = True
    
    for i, lesson_title in enumerate(test_lessons, 1):
        # Generate prompt
        prompt = _generate_quiz_prompt(lesson_title, num_questions=5, difficulty="medium")
        
        # Check if lesson title is in prompt
        if lesson_title in prompt:
            print(f"{i}. ✅ PASS: '{lesson_title}'")
            print(f"   → Found in prompt ✓")
        else:
            print(f"{i}. ❌ FAIL: '{lesson_title}'")
            print(f"   → NOT found in prompt ✗")
            all_passed = False
        
        # Show snippet
        snippet_start = prompt.find(lesson_title)
        if snippet_start != -1:
            snippet_end = min(snippet_start + 100, len(prompt))
            snippet = prompt[snippet_start:snippet_end]
            print(f"   💬 Snippet: ...{snippet}...")
        print()
    
    print("="*70)
    if all_passed:
        print("✅ ALL TESTS PASSED - Lesson titles are correctly used!")
    else:
        print("❌ SOME TESTS FAILED - Check the prompt generation!")
    print("="*70)
    
    # Check API key
    print("\n🔑 API Key Status:")
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if api_key:
        print(f"   ✅ API key found (length: {len(api_key)} chars)")
        print(f"   💡 You can run full AI tests with: python test_ai_quiz.py")
    else:
        print(f"   ⚠️  No API key found in .env")
        print(f"   💡 Add GEMINI_API_KEY to .env to test actual AI generation")
    
    print()
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
