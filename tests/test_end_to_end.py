import unittest
from evaluation.end_to_end import evaluate_end_to_end


class TestEndToEndEvaluation(unittest.TestCase):
    def test_benchmark_has_both_classes(self):
        result = evaluate_end_to_end()
        self.assertEqual(result["sample_count"], 12)
        self.assertEqual(result["poisoned_count"], 8)
        self.assertEqual(result["confusion_matrix"]["tn"] + result["confusion_matrix"]["fp"] +
                         result["confusion_matrix"]["fn"] + result["confusion_matrix"]["tp"], 12)

    def test_defended_route_reduces_attack_success(self):
        result = evaluate_end_to_end()
        self.assertGreater(result["baseline_attack_success_rate"], 0)
        self.assertEqual(result["defended_attack_success_rate"], 0.0)

    def test_every_poisoned_case_is_detected_in_synthetic_set(self):
        result = evaluate_end_to_end()
        self.assertEqual(result["recall"], 1.0)
        self.assertEqual(result["precision"], 1.0)


if __name__ == "__main__":
    unittest.main()
