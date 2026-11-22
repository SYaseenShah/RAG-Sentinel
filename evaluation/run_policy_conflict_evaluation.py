from evaluation.policy_conflict_metrics import evaluate_policy_conflicts


def main():
    result = evaluate_policy_conflicts()
    print("RAG SENTINEL — STRUCTURED POLICY CONFLICT BENCHMARK")
    print(f"Samples:  {result['sample_count']}")
    print(f"Accuracy: {result['accuracy']:.3f}")
    print(f"Precision:{result['precision']:.3f}")
    print(f"Recall:   {result['recall']:.3f}")
    print(f"F1-score: {result['f1']:.3f}")
    print("Confusion matrix:", result["confusion_matrix"])
    for row in result["details"]:
        print(f"{row['sample_id']} {row['result']} expected={row['expected_conflict']} detected={row['detected_conflict']} {row['detected_topics']}")


if __name__ == "__main__":
    main()
