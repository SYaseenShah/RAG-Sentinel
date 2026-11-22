import unittest
from evaluation.metrics import evaluate_benchmark, load_benchmark_dataset

class EvaluationTests(unittest.TestCase):
    def test_dataset_has_both_classes(self):
        rows = load_benchmark_dataset()
        labels = {row["label"] for row in rows}
        self.assertEqual(labels, {"clean", "poisoned"})

    def test_metrics_are_valid(self):
        result = evaluate_benchmark()
        self.assertEqual(result["sample_count"], 24)
        for key in ("accuracy", "precision", "recall", "f1"):
            self.assertGreaterEqual(result[key], 0.0)
            self.assertLessEqual(result[key], 1.0)
        cm = result["confusion_matrix"]
        self.assertEqual(cm["tn"] + cm["fp"] + cm["fn"] + cm["tp"], 24)

if __name__ == "__main__":
    unittest.main()
