import json
import os
from typing import Any, Dict, List, Optional

import requests

AI_TIMEOUT = 25


def _build_prompt(test_result: Any, skill_profile: Any) -> str:
    payload = {
        "total_score": float(test_result.total_score),
        "level": test_result.level,
        "skill_scores": {
            "logic": float(test_result.logic_score),
            "programming": float(test_result.programming_score),
            "oop": float(test_result.oop_score),
            "web": float(test_result.web_score),
        },
        "strengths": skill_profile.strengths or [],
        "weaknesses": skill_profile.weaknesses or [],
    }
    prompt = f"""
You are an AI learning architect. Given the following placement test summary and skill profile, craft a 6- to 12-week learning path.
Return only a JSON object with a single key "weeks" whose value is an array of objects.
Each week must contain: week_number (int), title (string), description (string), and topics (array of strings).
Do not wrap the JSON inside markdown.

Placement summary:
{json.dumps(payload, indent=2)}
"""
    return prompt.strip()


def _parse_ai_response(raw_text: Any) -> Dict[str, Any]:
    if isinstance(raw_text, dict):
        return raw_text
    try:
        return json.loads(raw_text)
    except Exception:
        try:
            cleaned = raw_text.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.strip("`").strip()
            return json.loads(cleaned)
        except Exception:
            return {}


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
            {"role": "system", "content": "You output valid JSON only."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 800,
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
        "temperature": 0.2,
        "maxOutputTokens": 800,
    }
    response = requests.post(url, headers=headers, params=params, json=body, timeout=AI_TIMEOUT)
    response.raise_for_status()
    payload = response.json()
    candidates = payload.get("candidates") or []
    if not candidates:
        return ""
    return candidates[0].get("output", "")


def _build_fallback(test_result: Any, skill_profile: Any) -> Dict[str, Any]:
    weeks: List[Dict[str, Any]] = []
    base_topics = skill_profile.recommended_topics or ["Core concepts review"]
    for week in range(1, 7):
        idx = (week - 1) % len(base_topics)
        weeks.append(
            {
                "week_number": week,
                "title": f"Week {week}: Focus on {skill_profile.level or 'fundamentals'}",
                "description": f"Build on strengths {skill_profile.strengths or []} and reinforce weaknesses {skill_profile.weaknesses or []}.",
                "topics": [base_topics[idx]],
            }
        )
    return {"weeks": weeks}


def _humanize_list(items: Optional[List[str]]) -> Optional[str]:
    if not items:
        return None
    cleaned = [str(item).strip() for item in items if item]
    if not cleaned:
        return None
    if len(cleaned) == 1:
        return cleaned[0]
    return f"{', '.join(cleaned[:-1])} và {cleaned[-1]}"


def _clean_text_output(raw_text: Any) -> str:
    if raw_text is None:
        return ""
    text = str(raw_text).strip()
    if text.startswith("```"):
        text = text.strip("`").strip()
    return text


def _call_description_ai(prompt: str) -> str:
    for invoker in (_invoke_openai, _invoke_gemini):
        try:
            raw = invoker(prompt)
        except Exception:
            continue
        description = _clean_text_output(raw)
        if description:
            return description
    return ""


def _build_week_description_prompt(
    level: str,
    strengths: List[str],
    weaknesses: List[str],
    courses_for_week: List[Dict[str, str]],
    week_index: int,
) -> str:
    strengths_text = _humanize_list(strengths) or "available strengths"
    weaknesses_text = _humanize_list(weaknesses) or "areas to improve"
    course_titles = ", ".join(
        [course.get("title") for course in courses_for_week if course.get("title")]
    ) or "recommended courses"
    prompt = f"""
You are a personalized learning advisor for a coding platform.
Based on:
- Week number: {week_index}
- Current level: {level}
- Strengths: {strengths_text}
- Weaknesses: {weaknesses_text}
- Courses scheduled for this week: {course_titles}
Write a single sentence (30-40 words) in Vietnamese that describes this week's goal, mention "tuần {week_index}", and highlight the progress from previous weeks.
Avoid code-style lists; keep the tone encouraging and clear.
"""
    return prompt.strip()


def generate_week_description_with_ai(
    level: str,
    strengths: List[str],
    weaknesses: List[str],
    courses_for_week: List[Dict[str, str]],
    week_index: int,
) -> str:
    prompt = _build_week_description_prompt(
        level or "beginner",
        strengths or [],
        weaknesses or [],
        courses_for_week or [],
        week_index,
    )
    ai_text = _call_description_ai(prompt)
    if ai_text:
        return ai_text
    strengths_text = _humanize_list(strengths) or "available strengths"
    weaknesses_text = _humanize_list(weaknesses) or "areas to improve"
    return f"Week {week_index} focuses on strengthening {strengths_text} and improving {weaknesses_text}."


def generate_week_description(
    level: str,
    strengths: List[str],
    weaknesses: List[str],
    week_index: int,
) -> str:
    strengths_str = ', '.join(strengths) if strengths else 'những thế mạnh hiện có'
    weaknesses_str = ', '.join(weaknesses) if weaknesses else 'các kỹ năng cần cải thiện'
    main_strength = strengths[0] if strengths else 'kỹ năng chính của bạn'

    if week_index == 1:
        return f'Tuần 1 tập trung ôn lại nền tảng {strengths_str} và làm quen với {weaknesses_str}.'
    if week_index == 2:
        return f'Tuần 2 đào sâu {main_strength} qua các bài tập thực hành, đồng thời tiếp tục củng cố {weaknesses_str}.'
    if week_index == 3:
        return f'Tuần 3 ưu tiên cải thiện {weaknesses_str}, giúp cân bằng với {strengths_str}.'
    if week_index == 4:
        return f'Tuần 4 áp dụng {strengths_str} vào bài tập tổng hợp và rèn luyện thêm {weaknesses_str} qua các lab thực tế.'
    return f'Tuần {week_index} tổng ôn các nội dung về {strengths_str} và {weaknesses_str}, chuẩn bị cho giai đoạn học tiếp theo.'
def generate_learning_path_with_ai(test_result: Any, skill_profile: Any) -> Dict[str, Any]:
    prompt = _build_prompt(test_result, skill_profile)
    raw_output = None
    try:
        raw_output = _invoke_openai(prompt)
    except Exception:
        pass
    if raw_output is None:
        try:
            raw_output = _invoke_gemini(prompt)
        except Exception:
            raw_output = None

    ai_payload = _parse_ai_response(raw_output) if raw_output else {}
    if not ai_payload.get("weeks"):
        ai_payload = _build_fallback(test_result, skill_profile)
    return {"raw_ai_response": ai_payload, "weeks": ai_payload.get("weeks", [])}
