import unittest
from evaluation.policy_conflict_metrics import evaluate_policy_conflicts


class PolicyConflictBenchmarkTests(unittest.TestCase):
    def test_benchmark_runs_and_counts_all_rows(self):
        result = evaluate_policy_conflicts()
        self.assertEqual(result["sample_count"], 12)
        self.assertEqual(sum(result["confusion_matrix"].values()), 12)

    def test_benchmark_predictions_match_labels(self):
        result = evaluate_policy_conflicts()
        self.assertTrue(all(row["result"] == "PASS" for row in result["details"]))


if __name__ == "__main__":
    unittest.main()
