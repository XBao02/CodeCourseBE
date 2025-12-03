"""Simple script to exercise AI recommendation chat endpoints.
Run:
    python backend/tests/test_ai_recommendation.py
Server must be running on http://localhost:5000
"""
import re
import json
import time
import requests

BASE = "http://localhost:5000/api/student/recommend/chat"

TEST_MESSAGES = [
    "Tôi muốn chuyển sang data science",
    "I want a roadmap to learn backend with Rust",
    "Cho mình vài khóa nâng cao về machine learning",
]

SEMANTIC_QUERY = "/semantic python web"  # will trigger semantic endpoint path inside FE logic


def extract_json_block(text: str):
    """Extract <JSON>...</JSON> block from Gemini reply, return dict or None."""
    m = re.search(r"<JSON>(.*?)</JSON>", text, re.DOTALL)
    if not m:
        return None
    raw = m.group(1).strip()
    try:
        return json.loads(raw)
    except Exception:
        return None


def run_chat_flow():
    print("== INIT SESSION ==")
    r = requests.post(f"{BASE}/init", json={})
    try:
        data = r.json()
    except Exception:
        print("Init response not JSON", r.text)
        return
    if not data.get("success"):
        print("Failed to init session", data)
        return
    session_id = data.get("sessionId")
    print("Session ID:", session_id)
    print("Intro message:", data.get("message"))

    results = []

    for msg in TEST_MESSAGES:
        print("\n== USER MESSAGE ==", msg)
        r2 = requests.post(f"{BASE}/message", json={"sessionId": session_id, "message": msg})
        try:
            resp = r2.json()
        except Exception:
            print("Reply not JSON", r2.text)
            continue
        if not resp.get("success"):
            print("Chat error:", resp)
            continue
        reply_text = resp.get("reply", "")
        print("Assistant reply (truncated):", reply_text[:300].replace("\n", " "))
        json_block = extract_json_block(reply_text)
        if json_block:
            print("Parsed JSON block:", json_block)
        courses = resp.get("coursesWithReasons", [])
        if courses:
            print("Recommended courses:")
            for item in courses:
                c = item.get("course", {})
                reason = item.get("reason")
                print(f" - #{c.get('id')} {c.get('title')} | level={c.get('level')} | reason={reason}")
        else:
            print("(No courses returned this turn)")
        follow_up = resp.get("followUp")
        if follow_up:
            print("Follow-up suggestion:", follow_up)
        # store
        results.append({
            "user_message": msg,
            "reply": reply_text,
            "json_block": json_block,
            "courses": courses,
            "follow_up": follow_up,
        })
        time.sleep(1)  # slight pause

    # Optional semantic test
    print("\n== SEMANTIC SEARCH COMMAND ==", SEMANTIC_QUERY)
    # This command is handled client-side normally; we directly call semantic endpoint here.
    semantic_payload = {"query": SEMANTIC_QUERY.replace("/semantic", "").strip(), "limit": 5}
    rs = requests.post("http://localhost:5000/api/student/recommend/semantic", json=semantic_payload)
    try:
        semantic_json = rs.json()
    except Exception:
        semantic_json = {"error": "Non-JSON response", "raw": rs.text}
    print("Semantic response:", json.dumps(semantic_json, ensure_ascii=False, indent=2)[:600])

    # Final summary
    print("\n================ SUMMARY ================")
    for r in results:
        print(f"User: {r['user_message']}")
        block = r['json_block'] or {}
        if block.get("courses"):
            print("  JSON courses IDs:", [c.get("id") for c in block.get("courses", [])])
        if r['courses']:
            print("  Mapped courses:")
            for item in r['courses']:
                c = item.get("course", {})
                print(f"    -> {c.get('id')} | {c.get('title')} | {c.get('level')} ")
        else:
            print("  No mapped courses")
        print()


if __name__ == "__main__":
    run_chat_flow()
