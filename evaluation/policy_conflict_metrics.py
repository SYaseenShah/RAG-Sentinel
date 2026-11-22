"""Evaluate structured policy conflict matching on a labelled synthetic set."""
from __future__ import annotations
import csv
from pathlib import Path
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from defence.contradiction import compare_policy_claims

DATASET_PATH = Path(__file__).with_name("policy_conflict_benchmark.csv")


def evaluate_policy_conflicts(path=DATASET_PATH):
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError("Policy conflict benchmark is empty.")
    truth, predicted, details = [], [], []
    for row in rows:
        expected = int(row["expected_conflict"])
        conflicts = compare_policy_claims(row["candidate_text"], row["reference_text"], "candidate", "reference")
        prediction = int(bool(conflicts))
        truth.append(expected)
        predicted.append(prediction)
        details.append({
            "sample_id": row["sample_id"],
            "topic": row["topic"],
            "expected_conflict": expected,
            "detected_conflict": prediction,
            "result": "PASS" if expected == prediction else "FAIL",
            "detected_topics": ", ".join(item["type"] for item in conflicts),
            "notes": row["notes"],
        })
    tn, fp, fn, tp = [int(value) for value in confusion_matrix(truth, predicted, labels=[0, 1]).ravel()]
    return {
        "sample_count": len(rows),
        "accuracy": float(accuracy_score(truth, predicted)),
        "precision": float(precision_score(truth, predicted, zero_division=0)),
        "recall": float(recall_score(truth, predicted, zero_division=0)),
        "f1": float(f1_score(truth, predicted, zero_division=0)),
        "confusion_matrix": {"tn": tn, "fp": fp, "fn": fn, "tp": tp},
        "details": details,
    }
