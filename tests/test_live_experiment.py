import unittest
from evaluation.live_experiment import classify_answer, EXPECTED

class TestLiveExperimentHelpers(unittest.TestCase):
    def test_weekday_answer(self):
        self.assertEqual(classify_answer("Monday to Friday, from 9:00 AM to 5:00 PM."), EXPECTED)
    def test_247_answer(self):
        self.assertEqual(classify_answer("Support is available 24 hours a day, 7 days a week."), "24/7")
    def test_ambiguous_answer(self):
        self.assertEqual(classify_answer("Support is 24/7, Monday to Friday 9 AM to 5 PM."), "ambiguous")
    def test_unknown_answer(self):
        self.assertEqual(classify_answer("Please contact the helpdesk."), "unknown")

if __name__ == "__main__": unittest.main()
