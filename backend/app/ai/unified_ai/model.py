"""
Unified AI model for placement test.

Design:
- Single lightweight model (logistic regression on bag-of-words) for level estimation.
- Question bank lives in dataset.json; generation samples by skill/difficulty.
- No external services; CPU only.
"""

from __future__ import annotations

import os
import pickle
import random
from dataclasses import dataclass, field
import sys
from typing import Dict, List, Tuple

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


@dataclass
class UnifiedAIState:
    question_bank: List[Dict[str, str]]
    pipeline: Pipeline
    labels: List[str] = field(default_factory=list)


# Backward-compat alias so pickled objects referring to 'model' can be loaded
sys.modules.setdefault("model", sys.modules[__name__])


class UnifiedAIModel:
    def __init__(self, model_dir: str) -> None:
        self.model_dir = model_dir
        self.model_path = os.path.join(model_dir, "model.pkl")
        self.question_bank_path = os.path.join(model_dir, "dataset.json")
        self._state: UnifiedAIState | None = None

        # Lightweight promptless template pools to synthesize new questions offline.
        self.language_topics: Dict[str, Dict[str, List[str]]] = {
            "python": {
                "syntax": ["functions", "list comprehensions", "with statement"],
                "concept": ["OOP", "generators", "context managers"],
                "tooling": ["virtualenv", "pip", "pytest"],
            },
            "javascript": {
                "syntax": ["let/const", "arrow functions", "template literals"],
                "concept": ["closures", "prototype chain", "event loop"],
                "tooling": ["npm", "ES modules", "fetch API"],
            },
            "go": {
                "syntax": ["goroutines", "channels", "defer"],
                "concept": ["interfaces", "struct embedding", "error handling"],
                "tooling": ["go mod", "testing", "pprof"],
            },
            "java": {
                "syntax": ["classes", "generics", "streams"],
                "concept": ["JVM memory", "concurrency", "exceptions"],
                "tooling": ["Maven/Gradle", "JUnit", "JDK tooling"],
            },
        }
        self.templates_by_difficulty: Dict[str, List[str]] = {
            "beginner": [
                "In {lang}, what does {topic} typically refer to?",
                "Which option best describes {lang} {topic}?",
                "For a newcomer to {lang}, how is {topic} commonly written?",
            ],
            "intermediate": [
                "When working with {lang} {topic}, which choice is most correct?",
                "What is a common pitfall when using {lang} {topic}?",
                "How do you idiomatically handle {topic} in {lang}?",
            ],
            "advanced": [
                "What is a performance consideration for {lang} {topic}?",
                "How does {lang} handle {topic} under the hood?",
                "Which approach is recommended for production-grade {lang} {topic}?",
            ],
        }

    def load(self) -> None:
        with open(self.model_path, "rb") as f:
            self._state = pickle.load(f)
        # Refresh question bank from dataset file to ensure latest tags
        try:
            with open(self.question_bank_path, "r", encoding="utf-8") as jf:
                bank = json.load(jf)
                if isinstance(self._state, UnifiedAIState):
                    self._state.question_bank = bank
        except Exception:
            pass

    def save(self, state: UnifiedAIState) -> None:
        os.makedirs(self.model_dir, exist_ok=True)
        with open(self.model_path, "wb") as f:
            pickle.dump(state, f)
        self._state = state

    @property
    def ready(self) -> bool:
        return self._state is not None

    def generate_questions(self, language: str, goal: str, limit: int = 8) -> List[Dict[str, str]]:
        """
        Pick deterministic-but-randomized questions filtered by difficulty/skill if possible.
        If bank is insufficient, synthesize new questions from templates/topic pools (offline).
        """
        assert self._state, "Model not loaded"
        bank = self._state.question_bank
        lang_key = language.lower()
        lang_key = self._normalize_language_alias(lang_key)
        # simple filter by goal -> difficulty
        target_difficulty = "beginner" if goal == "beginner" else "intermediate"
        # priority: same language + difficulty
        pool = [
            q
            for q in bank
            if q.get("difficulty") == target_difficulty and self._match_language(q.get("skill_tag", ""), lang_key)
        ]
        # next: same language any difficulty
        if len(pool) < limit:
            more = [
                q
                for q in bank
                if self._match_language(q.get("skill_tag", ""), lang_key) and q not in pool
            ]
            pool.extend(more)

        random.shuffle(pool)
        selected = list(pool[:limit])

        # Synthesize more if not enough
        if len(selected) < limit:
            needed = limit - len(selected)
            synthesized = self._synthesize_questions(language, target_difficulty, needed)
            selected.extend(synthesized)

        return [
            {
                "id": idx + 1,
                "question": q["question"],
                "options": q["options"],
                "correct_answer": q["correct_answer"],
                "difficulty": q["difficulty"],
                "skill_tag": q.get("skill_tag", "general"),
                "language": language,
            }
            for idx, q in enumerate(selected[:limit])
        ]

    def _synthesize_questions(self, language: str, difficulty: str, count: int) -> List[Dict[str, str]]:
        """
        Create questions on the fly using small templates and topic hints.
        Keeps everything deterministic-ish but varied enough.
        """
        lang_key = self._normalize_language_alias(language.lower())
        topics = self.language_topics.get(lang_key) or self.language_topics.get("python", {})
        templates = self.templates_by_difficulty.get(difficulty, self.templates_by_difficulty["beginner"])

        flat_topics = []
        for bucket in topics.values():
            flat_topics.extend(bucket)
        if not flat_topics:
            flat_topics = ["syntax", "tooling", "concepts"]

        questions: List[Dict[str, str]] = []
        for i in range(count):
            topic = random.choice(flat_topics)
            template = random.choice(templates)
            text = template.format(lang=language.title(), topic=topic)
            options = [
                f"It is about {topic}",
                f"It is unrelated to {topic}",
                f"It partially covers {topic}",
                f"It optimizes {topic}",
            ]
            correct = options[0]
            questions.append(
                {
                    "question": text,
                    "options": options,
                    "correct_answer": correct,
                    "difficulty": difficulty,
                    "skill_tag": topic,
                }
            )
        return questions

    @staticmethod
    def _normalize_language_alias(language: str) -> str:
        aliases = {
            "js": "javascript",
            "nodejs": "node",
            "c#": "csharp",
            "c++": "cpp",
            "golang": "go",
            "py": "python",
            "ts": "typescript",
        }
        return aliases.get(language, language)

    def _match_language(self, skill_tag: str, language: str) -> bool:
        if not language or language == "general":
            return True
        st = (skill_tag or "").lower()
        lang = self._normalize_language_alias(language)
        return st.startswith(lang)

    def evaluate(self, questions: List[Dict[str, str]], answers: List[Dict[str, str]]) -> Tuple[float, List[str]]:
        """
        Compare chosen answers to correct answers. Return score and weak skills.
        """
        score = 0.0
        weak: Dict[str, int] = {}
        ans_map = {a.get("question_id") or a.get("question"): a for a in answers}
        for q in questions:
            qid = q.get("id") or q.get("question")
            chosen = ans_map.get(qid, {}).get("answer") or ans_map.get(qid, {}).get("chosen_option")
            correct = str(q.get("correct_answer"))
            skill = q.get("skill_tag", "general")
            if chosen is not None and str(chosen).strip().lower() == correct.strip().lower():
                score += 10
            else:
                weak[skill] = weak.get(skill, 0) + 1
        weak_skills = sorted(weak, key=weak.get, reverse=True)[:2]
        return score, weak_skills

    def predict_level(self, score: float) -> Tuple[str, Dict[str, float]]:
        """
        Predict level from numeric score using trained classifier; fallback to thresholds.
        """
        assert self._state, "Model not loaded"
        pipe = self._state.pipeline
        try:
            probs = pipe.predict_proba([[score]])[0]
            labels = pipe.classes_
            prob_map = {str(lbl): float(p) for lbl, p in zip(labels, probs)}
            level = str(labels[int(probs.argmax())])
            return level, prob_map
        except Exception:
            if score >= 70:
                return "Advanced", {"Advanced": 1.0}
            if score >= 40:
                return "Intermediate", {"Intermediate": 1.0}
            return "Beginner", {"Beginner": 1.0}
