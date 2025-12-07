import json
import os
from typing import Any, Dict, List

import requests
from sqlalchemy import func

from app.models.placement_question_bank import PlacementQuestionBank

AI_TIMEOUT = 25

QUESTION_PLAN = [
    {"key": "syntax", "count": 4, "difficulty": "beginner", "focus": "core syntax, operators and literals"},
    {"key": "concept", "count": 4, "difficulty": "intermediate", "focus": "OOP or idiomatic patterns"},
    {"key": "advanced", "count": 2, "difficulty": "advanced", "focus": "async, tooling, performance"},
]

LANGUAGE_TOPICS = {
    "python": {
        "label": "Python",
        "mapping": {
            "syntax": ["syntax", "comprehension"],
            "concept": ["oop", "library"],
            "advanced": ["async", "typing"],
        },
    },
    "javascript": {
        "label": "JavaScript",
        "mapping": {
            "syntax": ["syntax", "es6"],
            "concept": ["closure", "event loop"],
            "advanced": ["async", "performance"],
        },
    },
    "cpp": {
        "label": "C++",
        "mapping": {
            "syntax": ["syntax", "expression"],
            "concept": ["pointer", "reference"],
            "advanced": ["stl", "templates"],
        },
    },
    "java": {
        "label": "Java",
        "mapping": {
            "syntax": ["syntax", "jvm"],
            "concept": ["oop", "thread"],
            "advanced": ["concurrency", "performance"],
        },
    },
}

FALLBACK_LANGUAGES = {
    "web_frontend": "Web Frontend",
    "react": "React",
    "vue": "Vue.js",
    "angular": "Angular",
    "svelte": "Svelte",
    "nodejs": "Node.js",
    "django": "Django",
    "flask": "Flask",
    "laravel": "Laravel",
    "android": "Android",
    "ios": "iOS",
    "flutter": "Flutter",
    "sql": "SQL",
    "machine_learning": "Machine Learning",
    "deep_learning": "Deep Learning",
    "data_analysis": "Data Analysis",
    "devops": "DevOps",
    "cloud": "Cloud",
    "typescript": "TypeScript",
    "design_pattern": "Design Pattern",
}

def _normalize_language(language: str) -> str:
    return (language or "general").strip().lower()


def _language_label(language: str) -> str:
    base = LANGUAGE_TOPICS.get(language, {}).get("label")
    if base:
        return base
    return FALLBACK_LANGUAGES.get(language, language.replace("_", " ").title() if language else "General")


def _parse_response(raw_text: Any) -> List[Dict[str, Any]]:
    if not raw_text:
        return []
    if isinstance(raw_text, list):
        return raw_text
    try:
        return json.loads(raw_text)
    except Exception:
        cleaned = str(raw_text).strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`").strip()
        try:
            return json.loads(cleaned)
        except Exception:
            return []


def _invoke_openai(prompt: str) -> Any:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    data = {
        "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        "messages": [
            {"role": "system", "content": "Output JSON array of multiple choice questions."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
        "max_tokens": 1200,
    }
    response = requests.post(url, json=data, headers=headers, timeout=AI_TIMEOUT)
    response.raise_for_status()
    payload = response.json()
    return payload["choices"][0]["message"]["content"]


def _invoke_gemini(prompt: str) -> Any:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    model = os.getenv("GEMINI_MODEL", "models/gemini-1.5-pro")
    url = f"https://generativelanguage.googleapis.com/v1beta/{model}:generateText"
    headers = {"Content-Type": "application/json"}
    params = {"key": api_key}
    body = {
        "prompt": {"text": prompt},
        "temperature": 0.3,
        "maxOutputTokens": 1200,
    }
    response = requests.post(url, headers=headers, params=params, json=body, timeout=AI_TIMEOUT)
    response.raise_for_status()
    payload = response.json()
    candidates = payload.get("candidates") or []
    if not candidates:
        return ""
    return candidates[0].get("output", "")


def _language_plan(language: str) -> Dict[str, Any]:
    normalized = _normalize_language(language)
    return LANGUAGE_TOPICS.get(normalized, {})


def _build_prompt(user_id: int, learning_goal: str | None, language: str) -> str:
    language_label = _language_label(language)
    goal_desc = learning_goal or "Improve technical skills"
    plan = _language_plan(language)
    lines = []
    for entry in QUESTION_PLAN:
        topic_variants = plan.get("mapping", {}).get(entry["key"], [entry["key"]])
        topic_list = ", ".join(topic_variants)
        lines.append(
            f"- {entry['count']} questions exploring {entry['key']} ({topic_list}) focused on {entry['focus']} (difficulty {entry['difficulty']})."
        )
    overview = "\n".join(lines)
    return f"""
You are crafting a placement test for {language_label} with user goal: "{goal_desc}".
Generate 8 to 12 multiple-choice questions covering the following breakdown:
{overview}
Each question must be tied to {language_label} idioms, syntax or tooling, and mention the topic in the response.
Return a JSON array of questions formatted as:
{{"question": "...", "options": ["A", "B", "C", "D"], "correct_answer": "A", "topic": "syntax", "difficulty": "beginner", "language": "{language_label.lower()}"}}
Questions must include exactly 4 unique options and clearly indicate one correct answer.
"""


def _bank_questions(language: str, limit: int = 10) -> List[Dict[str, Any]]:
    normalized = _normalize_language(language)
    bank_items = (
        PlacementQuestionBank.query.filter(func.lower(PlacementQuestionBank.language) == normalized)
        .order_by(func.rand())
        .limit(limit)
        .all()
    )
    return [
        {
            "question": item.question,
            "options": item.options,
            "correct_answer": item.correct_answer,
            "topic": item.topic,
            "difficulty": item.difficulty or "intermediate",
        }
        for item in bank_items
    ]


def _fallback_questions(language: str) -> List[Dict[str, Any]]:
    label = _language_label(language)
    plan = _language_plan(language)
    questions = []
    for entry in QUESTION_PLAN:
        topic_variants = plan.get("mapping", {}).get(entry["key"], [entry["key"]])
        for idx in range(entry["count"]):
            topic = topic_variants[idx % len(topic_variants)]
            text = (
                f"In {label}, {topic} question #{idx+1}: "
                f"Describe how {label} handles {entry['focus']} in a short scenario."
            )
            questions.append(
                {
                    "question": text,
                    "options": ["A", "B", "C", "D"],
                    "correct_answer": "A",
                    "topic": topic,
                    "difficulty": entry["difficulty"],
                }
            )
    return questions


def _normalize_question(raw: Dict[str, Any], language: str) -> Dict[str, Any]:
    question_text = (raw.get("question") or "").strip()
    options = raw.get("options") or []
    if isinstance(options, dict):
        options = list(options.values())
    if not isinstance(options, list):
        options = []
    normalized_options = options[:4]
    while len(normalized_options) < 4:
        normalized_options.append(f"Option {chr(65 + len(normalized_options))}")
    correct_answer = raw.get("correct_answer") or raw.get("answer") or normalized_options[0]
    topic = (raw.get("topic") or raw.get("subject") or "syntax").strip().lower()
    difficulty = (raw.get("difficulty") or raw.get("level") or "intermediate").strip().lower()
    return {
        "question": question_text or f"{language.title()} question",
        "options": normalized_options,
        "correct_answer": correct_answer,
        "topic": topic,
        "difficulty": difficulty,
        "language": language,
    }


def generate_questions_with_ai(user_id: int, learning_goal: str | None = None, language: str = "general") -> List[Dict[str, Any]]:
    normalized_language = _normalize_language(language)
    prompt = _build_prompt(user_id, learning_goal, normalized_language)
    raw_output = None
    try:
        raw_output = _invoke_openai(prompt)
    except Exception:
        raw_output = None
    if raw_output is None:
        try:
            raw_output = _invoke_gemini(prompt)
        except Exception:
            raw_output = None

    questions = _parse_response(raw_output)
    if not questions:
        questions = _bank_questions(normalized_language)
    if not questions:
        questions = _fallback_questions(normalized_language)

    normalized = []
    for raw in questions[:15]:
        normalized.append(_normalize_question(raw, normalized_language))
    return normalized
