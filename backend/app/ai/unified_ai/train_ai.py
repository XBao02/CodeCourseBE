"""
Minimal training script for unified placement AI.
Usage:
    python train_ai.py

This trains a tiny logistic regression classifier on synthetic scores
to map numeric score -> level, and saves question bank alongside.
"""

from __future__ import annotations

import json
import os
import pickle

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from model import UnifiedAIModel, UnifiedAIState


def build_classifier():
    # Synthetic training data: score -> level
    X = np.array([[10], [20], [30], [40], [50], [60], [70], [80], [90]])
    y = np.array(
        ["Beginner", "Beginner", "Beginner", "Intermediate", "Intermediate", "Intermediate", "Advanced", "Advanced", "Advanced"]
    )
    pipe = Pipeline(
        [
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(multi_class="auto", max_iter=200)),
        ]
    )
    pipe.fit(X, y)
    return pipe


def load_question_bank(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    base_dir = os.path.dirname(__file__)
    model_dir = base_dir
    dataset_path = os.path.join(base_dir, "dataset.json")
    question_bank = load_question_bank(dataset_path)
    pipe = build_classifier()

    state = UnifiedAIState(
        question_bank=question_bank,
        pipeline=pipe,
        labels=list(pipe.classes_),
    )
    model = UnifiedAIModel(model_dir=model_dir)
    model.save(state)
    print(f"Saved unified AI model to {model.model_path}")


if __name__ == "__main__":
    main()
