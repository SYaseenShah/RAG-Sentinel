"""Controlled end-to-end evidence-routing evaluation.

This benchmark tests the deterministic policy-claim gate and evidence selection.
It does NOT call Ollama, ChromaDB, or the live Streamlit upload registry.
"""
from __future__ import annotations

import csv
from pathlib import Path
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

from defence.contradiction import compare_policy_claims, extract_policy_claims
from defence.detector import analyze_document

DATASET_PATH = Path(__file__).with_name("end_to_end_benchmark.csv")


def _claim_value(text: str, topic: str):
    return extract_policy_claims(text).get(topic)


def _safe_reference_answer(reference_text: str, topic: str):
    return _claim_value(reference_text, topic)


def evaluate_end_to_end(path=DATASET_PATH):
    """Compare a vulnerable candidate-preferred route with a defended route."""
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError("End-to-end benchmark is empty.")

    y_true, y_pred = [], []
    poisoned_total = baseline_success = defended_success = 0
    details = []

    for row in rows:
        expected_poisoned = int(row["expected_poisoned"])
        reference = row["trusted_reference"]
        candidate = row["candidate_document"]
        topic = row["topic"]
        expected_answer = _safe_reference_answer(reference, topic)

        conflicts = compare_policy_claims(
            candidate, reference,
            candidate_source="unverified_candidate",
            reference_source="administrator_approved_reference",
        )
        conflict_detected = int(any(item["type"] == topic for item in conflicts))

        # The content detector is recorded as an additional signal, not used
        # as a substitute for source authentication or contradiction analysis.
        content_analysis = analyze_document(candidate, source="unverified_candidate")

        # Vulnerable baseline: the candidate document wins retrieval precedence.
        baseline_answer = _claim_value(candidate, topic)
        baseline_wrong = int(baseline_answer != expected_answer)

        # Defended route: conflicting candidate evidence is excluded; only the
        # administrator-approved reference supplies the answer. Unknown sources
        # are never promoted to trusted evidence by this benchmark.
        candidate_is_eligible = (not conflict_detected) and content_analysis["decision"] == "APPROVED"
        defended_answer = baseline_answer if candidate_is_eligible else _safe_reference_answer(reference, topic)
        defended_wrong = int(defended_answer != expected_answer)

        y_true.append(expected_poisoned)
        y_pred.append(conflict_detected)

        if expected_poisoned:
            poisoned_total += 1
            baseline_success += baseline_wrong
            defended_success += defended_wrong

        details.append({
            "sample_id": row["sample_id"],
            "organization": row["organization"],
            "topic": topic,
            "expected_poisoned": expected_poisoned,
            "conflict_detected": conflict_detected,
            "baseline_answer": str(baseline_answer),
            "defended_answer": str(defended_answer),
            "expected_answer": str(expected_answer),
            "baseline_wrong_answer": baseline_wrong,
            "defended_wrong_answer": defended_wrong,
            "content_risk_score": content_analysis["risk_score"],
            "content_decision": content_analysis["decision"],
            "result": "PASS" if (conflict_detected == expected_poisoned and defended_wrong == 0) else "CHECK",
            "notes": row["notes"],
        })

    tn, fp, fn, tp = [int(v) for v in confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()]
    return {
        "sample_count": len(rows),
        "poisoned_count": poisoned_total,
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "confusion_matrix": {"tn": tn, "fp": fp, "fn": fn, "tp": tp},
        "baseline_attack_success_rate": baseline_success / poisoned_total if poisoned_total else 0.0,
        "defended_attack_success_rate": defended_success / poisoned_total if poisoned_total else 0.0,
        "details": details,
    }


if __name__ == "__main__":
    result = evaluate_end_to_end()
    print("RAG SENTINEL — CONTROLLED END-TO-END EVIDENCE-ROUTING BENCHMARK")
    print(f"Samples: {result['sample_count']} | Poisoned: {result['poisoned_count']}")
    print(f"Conflict detection — Accuracy: {result['accuracy']:.1%} | Precision: {result['precision']:.1%} | Recall: {result['recall']:.1%} | F1: {result['f1']:.1%}")
    print(f"Confusion matrix: {result['confusion_matrix']}")
    print(f"Baseline attack success rate: {result['baseline_attack_success_rate']:.1%}")
    print(f"Defended attack success rate: {result['defended_attack_success_rate']:.1%}")
    for item in result["details"]:
        print(f"{item['sample_id']} {item['result']} conflict={item['conflict_detected']} baseline_wrong={item['baseline_wrong_answer']} defended_wrong={item['defended_wrong_answer']}")
