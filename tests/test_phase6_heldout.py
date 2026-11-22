import unittest
from evaluation.phase6_heldout import CASES, evaluate_phase6

class Phase6HeldoutTests(unittest.TestCase):
    def test_dataset_has_40_cases(self):
        self.assertEqual(len(CASES),40)
    def test_case_ids_are_unique(self):
        ids=[c.case_id for c in CASES]
        self.assertEqual(len(ids),len(set(ids)))
    def test_benchmark_metrics_are_bounded(self):
        result=evaluate_phase6()
        for key in ("accuracy","precision","recall","f1"):
            self.assertGreaterEqual(result[key],0)
            self.assertLessEqual(result[key],1)
    def test_guard_cases_exist(self):
        categories={c.category for c in CASES}
        self.assertIn("organization_guard",categories)
        self.assertIn("unsupported_claim",categories)

if __name__ == "__main__": unittest.main()
