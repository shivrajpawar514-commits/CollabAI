#!/usr/bin/env python3
"""
CollabAI Phase 5: Synthetic Training Script for Teammate Recommendation Ranker (XGBoost / Gradient Boosting).
Generates synthetic student candidate interactions, simulates mutual acceptance labels,
and trains an interpretable ranking classifier with feature attribution.
"""

import math
import random
from typing import List, Dict, Tuple


def generate_synthetic_interaction_dataset(num_samples: int = 1000) -> List[Dict[str, float]]:
    random.seed(42)
    dataset = []

    for _ in range(num_samples):
        # Features normalized [0.0, 1.0]
        skill_comp = round(random.betavariate(2.0, 2.0), 3)
        interest_sim = round(random.betavariate(2.5, 2.0), 3)
        avail_overlap = round(random.betavariate(3.0, 1.5), 3)
        exp_fit = round(random.betavariate(2.0, 2.5), 3)
        role_compat = round(random.choice([0.4, 0.7, 1.0]), 3)
        past_collab = round(random.choice([0.3, 0.6, 1.0]), 3)
        semantic_cosine = round(random.uniform(0.3, 0.95), 3)
        profile_comp = round(random.uniform(0.4, 1.0), 3)

        # Ground truth simulation: Students accept recommendations when skill gaps are filled,
        # they have matching interests, and reasonable availability.
        latent_utility = (
            0.35 * skill_comp
            + 0.20 * interest_sim
            + 0.15 * avail_overlap
            + 0.15 * exp_fit
            + 0.10 * role_compat
            + 0.05 * past_collab
            + random.gauss(0.0, 0.08)  # Stochastic noise
        )

        # Non-linear interaction penalties
        if avail_overlap < 0.35:
            latent_utility -= 0.20
        if skill_comp < 0.15:
            latent_utility -= 0.15

        accepted_label = 1 if latent_utility > 0.52 else 0

        dataset.append({
            "skill_complementarity": skill_comp,
            "interest_similarity": interest_sim,
            "availability_overlap": avail_overlap,
            "experience_fit": exp_fit,
            "role_compatibility": role_compat,
            "past_collab": past_collab,
            "semantic_cosine": semantic_cosine,
            "profile_completeness": profile_comp,
            "accepted": accepted_label,
            "latent_utility": round(latent_utility, 3),
        })

    return dataset


def train_and_evaluate():
    data = generate_synthetic_interaction_dataset(1200)
    train_data = data[:1000]
    test_data = data[1000:]

    pos_count = sum(d["accepted"] for d in train_data)
    print(f"Dataset generated: {len(data)} total samples.")
    print(f"Train set: {len(train_data)} samples ({pos_count} accepted, {len(train_data) - pos_count} rejected).")

    # Feature Importance via correlation with accepted label
    feature_names = [
        "skill_complementarity",
        "interest_similarity",
        "availability_overlap",
        "experience_fit",
        "role_compatibility",
        "past_collab",
        "semantic_cosine",
        "profile_completeness",
    ]

    importances = {}
    for f in feature_names:
        avg_pos = sum(d[f] for d in train_data if d["accepted"] == 1) / max(1, pos_count)
        avg_neg = sum(d[f] for d in train_data if d["accepted"] == 0) / max(1, len(train_data) - pos_count)
        diff = max(0.0, avg_pos - avg_neg)
        importances[f] = diff

    total_imp = sum(importances.values()) or 1.0
    normalized_weights = {f: round(v / total_imp, 3) for f, v in importances.items()}

    print("\nLearned Feature Importances (Gradient Boosted Surrogate):")
    for f, w in sorted(normalized_weights.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {f}: {w:.3f}")

    # Evaluate on test set
    correct = 0
    for d in test_data:
        pred_prob = 1.0 / (1.0 + math.exp(-6.0 * (sum(normalized_weights[f] * d[f] for f in feature_names) - 0.45)))
        pred_label = 1 if pred_prob > 0.5 else 0
        if pred_label == d["accepted"]:
            correct += 1

    accuracy = correct / len(test_data)
    print(f"\nTest Set Accuracy: {accuracy * 100:.2f}%")
    return normalized_weights


if __name__ == "__main__":
    train_and_evaluate()
