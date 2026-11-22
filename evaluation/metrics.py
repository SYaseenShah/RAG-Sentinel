"""Reproducible benchmark for the current rule-based content detector.

This evaluates the configured detector against a small, labelled, synthetic
benchmark. It is not a claim of general-purpose poisoning detection.
"""
from __future__ import annotations
import csv
from pathlib import Path
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)
from defence.detector import analyze_document, TRUSTED_SOURCES

ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = Path(__file__).with_name("benchmark_dataset.csv")

def load_benchmark_dataset(path: Path = DATASET_PATH):
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError("Benchmark dataset is empty.")
    for row in rows:
        if row.get("label") not in {"clean", "poisoned"}:
            raise ValueError(f"Invalid label in sample {row.get('sample_id')}")
    return rows

def evaluate_benchmark(path: Path = DATASET_PATH):
    rows = load_benchmark_dataset(path)
    y_true, y_pred, details = [], [], []
    # Use a registered source label to isolate content-pattern detection from
    # the separate provenance warning. This is an offline detector benchmark.
    benchmark_source = next(iter(TRUSTED_SOURCES))
    for row in rows:
        analysis = analyze_document(row["content"], source=benchmark_source)
        truth = 1 if row["label"] == "poisoned" else 0
        prediction = 1 if analysis["decision"] == "REJECTED" else 0
        y_true.append(truth); y_pred.append(prediction)
        details.append({
            "sample_id": row["sample_id"], "actual": row["label"],
            "predicted": "poisoned" if prediction else "clean",
            "risk_score": analysis["risk_score"],
            "decision": analysis["decision"],
            "matched_categories": ", ".join(analysis["matched_categories"]),
        })
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    tn, fp, fn, tp = [int(x) for x in cm.ravel()]
    return {
        "sample_count": len(rows),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "confusion_matrix": {"tn": tn, "fp": fp, "fn": fn, "tp": tp},
        "details": details,
        "report": classification_report(y_true, y_pred, labels=[0, 1], target_names=["clean", "poisoned"], zero_division=0, output_dict=True),
    }
