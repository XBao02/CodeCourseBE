"""AI Quiz generation endpoints backed by Google Generative AI (Gemini)."""

from __future__ import annotations

import json
import os
from functools import lru_cache

from dotenv import load_dotenv
from flask import Blueprint, current_app, jsonify, request

try:
    import google.generativeai as genai
except Exception:  # pragma: no cover - optional dependency
    genai = None


ai_quiz_bp = Blueprint("ai_quiz", __name__, url_prefix="/api/ai/quiz")


def _missing_dependency() -> RuntimeError:
    return RuntimeError(
        "google-generativeai is not installed. "
        "Run `pip install google-generativeai` inside the backend environment."
    )


@lru_cache(maxsize=1)
def _configure_client() -> None:
    """Configure the Generative AI client once."""
    load_dotenv()
    if genai is None:
        raise _missing_dependency()

    api_key = (
        os.getenv("GEMINI_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
        or os.getenv("GOOGLE_GEMINI_KEY")
    )
    if not api_key:
        raise RuntimeError("Missing GEMINI_API_KEY / GOOGLE_API_KEY in environment.")

    genai.configure(api_key=api_key)


def _prompt_gemini_quiz(prompt: str, model_name: str | None = None) -> str:
    """Call Gemini API to generate quiz questions."""
    _configure_client()
    name = model_name or "gemini-2.5-flash"
    model = genai.GenerativeModel(name)
    response = model.generate_content(prompt)
    text = getattr(response, "text", None)
    if text:
        return text.strip()
    # Fallback to concatenating individual parts if .text is empty
    return " ".join(
        part.text.strip()
        for part in getattr(response, "candidates", [])  # type: ignore[attr-defined]
        for part in getattr(getattr(part, "content", None), "parts", []) or []  # type: ignore[arg-type]
        if hasattr(part, "text") and part.text
    ).strip()


def _parse_quiz_questions(ai_response: str) -> list[dict]:
    """
    Parse AI response to extract quiz questions.
    Expected format: JSON array with question objects
    """
    try:
        # Try to extract JSON from markdown code blocks if present
        if "```json" in ai_response:
            start = ai_response.find("```json") + 7
            end = ai_response.find("```", start)
            json_str = ai_response[start:end].strip()
        elif "```" in ai_response:
            start = ai_response.find("```") + 3
            end = ai_response.find("```", start)
            json_str = ai_response[start:end].strip()
        else:
            json_str = ai_response
        
        questions = json.loads(json_str)
        return questions if isinstance(questions, list) else [questions]
    except json.JSONDecodeError:
        current_app.logger.error("Failed to parse quiz JSON: %s", ai_response)
        return []


def _generate_quiz_prompt(lesson_title: str, num_questions: int = 5, difficulty: str = "medium") -> str:
    """Generate a prompt for Gemini to create quiz questions."""
    prompt = f"""Create {num_questions} multiple-choice quiz questions about the lesson: "{lesson_title}"

Difficulty level: {difficulty}

Return the response as a JSON array of objects with this exact structure:
[
  {{
    "question": "The question text here",
    "options": [
      "Option A (correct answer)",
      "Option B (incorrect)",
      "Option C (incorrect)",
      "Option D (incorrect)"
    ],
    "correctAnswer": 0,
    "explanation": "Why this is the correct answer"
  }}
]

Make sure:
1. The correct answer is randomly placed in the options array (0-3)
2. Shuffle the options so the correct answer isn't always first
3. Each question tests understanding of the lesson content
4. Options are plausible but clearly distinguishable
5. explanations are clear and educational
6. Return ONLY valid JSON, no additional text
"""
    return prompt


@ai_quiz_bp.post("/generate")
def generate_quiz():
    """
    Generate quiz questions based on lesson title.
    
    Request body:
    {
        "lesson_title": "string",
        "num_questions": int (optional, default 5),
        "difficulty": "easy|medium|hard" (optional, default "medium"),
        "model": "string" (optional, Gemini model name)
    }
    """
    payload = request.get_json(silent=True) or {}
    lesson_title = (payload.get("lesson_title") or "").strip()
    num_questions = payload.get("num_questions", 5)
    difficulty = (payload.get("difficulty") or "medium").strip().lower()
    model = (payload.get("model") or "").strip() or None

    # Validate inputs
    if not lesson_title:
        return jsonify({"error": "lesson_title is required"}), 400
    
    if not isinstance(num_questions, int) or num_questions < 1 or num_questions > 20:
        return jsonify({"error": "num_questions must be between 1 and 20"}), 400
    
    if difficulty not in ("easy", "medium", "hard"):
        return jsonify({"error": "difficulty must be 'easy', 'medium', or 'hard'"}), 400

    questions = []
    error_msg = None

    try:
        # Generate prompt and call Gemini
        prompt = _generate_quiz_prompt(lesson_title, num_questions, difficulty)
        ai_response = _prompt_gemini_quiz(prompt, model)
        
        # Parse response
        questions = _parse_quiz_questions(ai_response)
        
        if not questions:
            error_msg = "Failed to parse AI response as valid quiz questions"
            current_app.logger.error("No questions parsed from: %s", ai_response)
        
    except Exception as exc:  # pragma: no cover - external API
        current_app.logger.error("Quiz generation failed: %s", exc)
        error_msg = str(exc)
    
    return jsonify(
        {
            "lesson_title": lesson_title,
            "questions": questions,
            "count": len(questions),
            "requested_count": num_questions,
            "difficulty": difficulty,
            "model": model or "gemini-2.5-flash",
            "error": error_msg,
        }
    ), 200 if not error_msg or questions else 206


@ai_quiz_bp.post("/generate-batch")
def generate_batch_quiz():
    """
    Generate quiz questions for multiple lessons.
    
    Request body:
    {
        "lessons": [
            {
                "id": "lesson_id",
                "title": "lesson_title"
            }
        ],
        "num_questions": int (optional, default 5),
        "difficulty": "easy|medium|hard" (optional, default "medium"),
        "model": "string" (optional, Gemini model name)
    }
    """
    payload = request.get_json(silent=True) or {}
    lessons = payload.get("lessons", [])
    num_questions = payload.get("num_questions", 5)
    difficulty = (payload.get("difficulty") or "medium").strip().lower()
    model = (payload.get("model") or "").strip() or None

    # Validate inputs
    if not lessons or not isinstance(lessons, list):
        return jsonify({"error": "lessons array is required"}), 400
    
    if not isinstance(num_questions, int) or num_questions < 1 or num_questions > 20:
        return jsonify({"error": "num_questions must be between 1 and 20"}), 400
    
    if difficulty not in ("easy", "medium", "hard"):
        return jsonify({"error": "difficulty must be 'easy', 'medium', or 'hard'"}), 400

    results = []

    for lesson in lessons:
        lesson_id = lesson.get("id")
        lesson_title = (lesson.get("title") or "").strip()
        
        if not lesson_title:
            results.append({
                "lesson_id": lesson_id,
                "lesson_title": lesson_title,
                "questions": [],
                "error": "lesson_title is required"
            })
            continue
        
        questions = []
        error_msg = None

        try:
            prompt = _generate_quiz_prompt(lesson_title, num_questions, difficulty)
            ai_response = _prompt_gemini_quiz(prompt, model)
            questions = _parse_quiz_questions(ai_response)
            
            if not questions:
                error_msg = "Failed to parse AI response"
        except Exception as exc:
            current_app.logger.error("Quiz generation failed for lesson %s: %s", lesson_id, exc)
            error_msg = str(exc)
        
        results.append({
            "lesson_id": lesson_id,
            "lesson_title": lesson_title,
            "questions": questions,
            "count": len(questions),
            "error": error_msg
        })

    return jsonify(
        {
            "results": results,
            "total_lessons": len(lessons),
            "successful": sum(1 for r in results if not r.get("error")),
            "model": model or "gemini-2.5-flash"
        }
    ), 200


@ai_quiz_bp.post("/validate")
def validate_answer():
    """
    Validate a user's quiz answer.
    
    Request body:
    {
        "question": "question text",
        "user_answer": int (option index),
        "correct_answer": int (option index),
        "explanation": "string (optional)"
    }
    """
    payload = request.get_json(silent=True) or {}
    user_answer = payload.get("user_answer")
    correct_answer = payload.get("correct_answer")

    if user_answer is None or correct_answer is None:
        return jsonify({"error": "user_answer and correct_answer are required"}), 400

    is_correct = user_answer == correct_answer
    explanation = payload.get("explanation", "")

    return jsonify(
        {
            "is_correct": is_correct,
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "explanation": explanation,
        }
    )


@ai_quiz_bp.post("/enhance")
def enhance_question():
    """
    Enhance or modify an existing quiz question using AI.
    
    Request body:
    {
        "question": "question text",
        "options": ["option1", "option2", "option3", "option4"],
        "action": "simplify|enhance|rephrase",
        "model": "string (optional)"
    }
    """
    payload = request.get_json(silent=True) or {}
    question = (payload.get("question") or "").strip()
    options = payload.get("options", [])
    action = (payload.get("action") or "rephrase").strip().lower()
    model = (payload.get("model") or "").strip() or None

    if not question or not options:
        return jsonify({"error": "question and options are required"}), 400
    
    if action not in ("simplify", "enhance", "rephrase"):
        return jsonify({"error": "action must be 'simplify', 'enhance', or 'rephrase'"}), 400

    action_prompts = {
        "simplify": "Make this question simpler and clearer without changing its meaning",
        "enhance": "Make this question more challenging and test deeper understanding",
        "rephrase": "Rephrase this question while keeping the same difficulty level"
    }

    prompt = f"""{action_prompts[action]}:

Question: {question}
Options:
{chr(10).join(f"  {i+1}. {opt}" for i, opt in enumerate(options))}

Return the enhanced question and options in this JSON format:
{{
  "question": "new question",
  "options": ["option 1", "option 2", "option 3", "option 4"]
}}

Return ONLY valid JSON, no additional text.
"""

    enhanced = {}
    error_msg = None

    try:
        ai_response = _prompt_gemini_quiz(prompt, model)
        parsed = _parse_quiz_questions(ai_response)
        if parsed and isinstance(parsed, list) and len(parsed) > 0:
            enhanced = parsed[0] if isinstance(parsed[0], dict) else {}
        elif parsed and isinstance(parsed, dict):
            enhanced = parsed
        else:
            # Try to parse as direct JSON
            try:
                enhanced = json.loads(ai_response)
            except json.JSONDecodeError:
                error_msg = "Failed to parse enhanced question"
                current_app.logger.error("Failed to parse: %s", ai_response)
    except Exception as exc:
        current_app.logger.error("Question enhancement failed: %s", exc)
        error_msg = str(exc)

    return jsonify(
        {
            "original_question": question,
            "enhanced": enhanced,
            "action": action,
            "error": error_msg,
            "model": model or "gemini-2.5-flash"
        }
    ), 200 if not error_msg else 206


__all__ = [
    "ai_quiz_bp",
    "_prompt_gemini_quiz",
    "_generate_quiz_prompt",
    "_parse_quiz_questions",
]
