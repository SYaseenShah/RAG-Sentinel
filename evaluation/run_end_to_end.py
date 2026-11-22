from evaluation.end_to_end import evaluate_end_to_end

if __name__ == "__main__":
    result = evaluate_end_to_end()
    print("RAG SENTINEL — PHASE 4 END-TO-END BENCHMARK")
    print(f"Samples: {result['sample_count']} | Poisoned cases: {result['poisoned_count']}")
    print(f"Accuracy: {result['accuracy']:.3f}")
    print(f"Precision: {result['precision']:.3f}")
    print(f"Recall: {result['recall']:.3f}")
    print(f"F1-score: {result['f1']:.3f}")
    print(f"Confusion matrix: {result['confusion_matrix']}")
    print(f"Baseline attack success rate: {result['baseline_attack_success_rate']:.1%}")
    print(f"Defended attack success rate: {result['defended_attack_success_rate']:.1%}")
