"""AI assistant endpoints backed by Google Generative AI (Gemini)."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from flask import Blueprint, current_app, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename

try:
    import google.generativeai as genai
except Exception:  # pragma: no cover - optional dependency
    genai = None


ai_bp = Blueprint("ai", __name__, url_prefix="/api/ai")

UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads" / "ai"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "pdf", "txt", "md"}

COURSE_LIBRARY = [
    {
        "id": 1,
        "title": "HTML & CSS Essentials",
        "description": "Build your first responsive pages starting from pure HTML and CSS.",
        "duration": 20,
        "enrolled": 1250,
        "rating": 4.8,
        "level": "beginner",
        "icon": "fab fa-html5",
        "gradient": "linear-gradient(135deg, #6a11cb 0%, #2575fc 100%)",
        "tags": ["html", "css", "web", "frontend"],
    },
    {
        "id": 2,
        "title": "Modern JavaScript",
        "description": "Master ES6+, async patterns, and real-world architecture.",
        "duration": 30,
        "enrolled": 890,
        "rating": 4.9,
        "level": "advanced",
        "icon": "fab fa-js-square",
        "gradient": "linear-gradient(135deg, #2575fc 0%, #6a11cb 100%)",
        "tags": ["javascript", "frontend", "advanced"],
    },
    {
        "id": 3,
        "title": "Python for Data Science",
        "description": "Use Python to explore, visualise, and build first ML models.",
        "duration": 40,
        "enrolled": 2100,
        "rating": 4.7,
        "level": "intermediate",
        "icon": "fab fa-python",
        "gradient": "linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%)",
        "tags": ["python", "data", "ml", "analytics"],
    },
    {
        "id": 4,
        "title": "React from Zero to Hero",
        "description": "Ship production-ready UIs with hooks, state machines, and testing.",
        "duration": 35,
        "enrolled": 1750,
        "rating": 4.8,
        "level": "intermediate",
        "icon": "fab fa-react",
        "gradient": "linear-gradient(135deg, #00b894 0%, #00cec9 100%)",
        "tags": ["react", "web", "frontend"],
    },
    {
        "id": 5,
        "title": "Node.js Backend Fundamentals",
        "description": "Design APIs with Express, authentication, and database integrations.",
        "duration": 25,
        "enrolled": 980,
        "rating": 4.6,
        "level": "intermediate",
        "icon": "fab fa-node-js",
        "gradient": "linear-gradient(135deg, #fd79a8 0%, #e84393 100%)",
        "tags": ["node", "backend", "api"],
    },
    {
        "id": 6,
        "title": "UI / UX Design Fundamentals",
        "description": "Foundations of interface design, research, and prototyping.",
        "duration": 18,
        "enrolled": 650,
        "rating": 4.5,
        "level": "beginner",
        "icon": "fas fa-palette",
        "gradient": "linear-gradient(135deg, #a29bfe 0%, #6c5ce7 100%)",
        "tags": ["design", "ui", "ux"],
    },
]


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


def list_text_models() -> list[str]:
    """Return Gemini model IDs that support text generation."""
    try:
        _configure_client()
        models = genai.list_models()
    except Exception as exc:  # pragma: no cover - network call
        current_app.logger.warning("Gemini list_models failed: %s", exc)
        return []

    names = []
    for model in models:
        methods = getattr(model, "supported_generation_methods", None) or []
        if "generateContent" in methods:
            names.append(model.name)
    return names


def _prompt_gemini(prompt: str, model_name: str | None = None) -> str:
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


def _local_reply(prompt: str) -> tuple[str, list[str], list[int]]:
    lower = (prompt or "").lower()
    if any(k in lower for k in ("web", "frontend", "html", "css", "javascript", "react")):
        text = (
            "Great choice focusing on web development. Start with solid HTML/CSS foundations, "
            "then layer JavaScript and React to ship full experiences."
        )
        suggestions = [
            "Show me beginner web courses",
            "How do I move from HTML/CSS to React?",
            "What does the frontend track look like?",
        ]
        recs = [1, 2, 4]
    elif any(k in lower for k in ("python", "data", "analysis", "ml", "machine learning")):
        text = (
            "Python plus data is a powerful combo. Begin with data wrangling and visualisation, "
            "then add machine learning once you feel comfortable."
        )
        suggestions = [
            "Recommend Python + data courses",
            "How to start machine learning?",
            "Any analytics projects I can try?",
        ]
        recs = [3]
    elif any(k in lower for k in ("backend", "api", "node")):
        text = (
            "Backend engineering thrives on clean APIs and solid database design. "
            "Node.js with Express is a fast way to build production-ready services."
        )
        suggestions = [
            "Show me backend roadmap",
            "How do I secure my APIs?",
            "What database should I pair with Node?",
        ]
        recs = [5]
    elif any(k in lower for k in ("design", "ui", "ux", "interface")):
        text = (
            "Strong product design blends research with visual craft. "
            "Start with UI/UX fundamentals, then layer tools like Figma or Framer."
        )
        suggestions = [
            "Beginner tips for UI/UX",
            "How do I build a case study?",
            "Best tools for interface design?",
        ]
        recs = [6]
    elif any(k in lower for k in ("new", "beginner", "start", "where do i begin")):
        text = (
            "Welcome aboard! Begin with foundational courses so you gain confidence quickly, "
            "then follow one of the curated tracks depending on your interest."
        )
        suggestions = [
            "Suggest a complete beginner path",
            "How long to become job-ready?",
            "What should I learn after the basics?",
        ]
        recs = [1, 6]
    else:
        text = (
            "Thanks for sharing! I can recommend a curated mix of courses based on your goals. "
            "Feel free to mention the stack, role, or timeline you're targeting."
        )
        suggestions = [
            "What is the most popular track?",
            "Help me choose between frontend and backend",
            "Show courses that fit my schedule",
        ]
        recs = []
    return text, suggestions, recs


@ai_bp.get("/models")
def get_models():
    models = list_text_models()
    return jsonify({"models": models, "count": len(models)})


@ai_bp.post("/chat")
def chat():
    payload = request.get_json(silent=True) or {}
    prompt = (payload.get("prompt") or "").strip()
    model = (payload.get("model") or "").strip() or None

    if not prompt:
        return jsonify({"error": "prompt is required"}), 400

    fallback_text, suggestions, course_ids = _local_reply(prompt)
    reply = fallback_text
    model_used = model or "gemini-2.5-flash"

    try:
        ai_answer = _prompt_gemini(prompt, model)
        if ai_answer:
            reply = ai_answer
    except Exception as exc:  # pragma: no cover - external API
        current_app.logger.error("Gemini chat failed: %s", exc)
        # keep fallback reply but still surface error info to client via metadata
        return jsonify(
            {
                "reply": reply,
                "suggestions": suggestions,
                "recommendations": course_ids,
                "model": model_used,
                "warning": str(exc),
            }
        ), 200

    return jsonify(
        {
            "reply": reply or "No response generated.",
            "suggestions": suggestions,
            "recommendations": course_ids,
            "model": model_used,
        }
    )


@ai_bp.get("/courses")
def list_courses():
    return jsonify({"courses": COURSE_LIBRARY})


def _ensure_upload_dir() -> Path:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    return UPLOAD_DIR


def _allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@ai_bp.post("/upload")
def upload_attachment():
    if "file" not in request.files:
        return jsonify({"error": "file is required"}), 400

    file = request.files["file"]
    if not file or not file.filename:
        return jsonify({"error": "missing filename"}), 400

    if not _allowed_file(file.filename):
        return jsonify({"error": "Unsupported file type"}), 400

    safe_name = secure_filename(file.filename)
    upload_dir = _ensure_upload_dir()

    final_name = safe_name
    counter = 1
    while (upload_dir / final_name).exists():
        stem = Path(safe_name).stem
        suffix = Path(safe_name).suffix
        final_name = f"{stem}_{counter}{suffix}"
        counter += 1

    file.save(upload_dir / final_name)
    url = f"/api/ai/uploads/{final_name}"
    return jsonify(
        {
            "file_name": final_name,
            "url": url,
            "mime": file.mimetype,
            "size": (upload_dir / final_name).stat().st_size,
        }
    )


@ai_bp.get("/uploads/<path:filename>")
def serve_upload(filename: str):
    upload_dir = _ensure_upload_dir()
    return send_from_directory(upload_dir, filename, as_attachment=False)


__all__ = [
    "ai_bp",
    "list_text_models",
    "_prompt_gemini",
]
