import unittest
from defence.contradiction import (
    extract_support_hours, extract_policy_claims,
    compare_policy_claims, detect_contradictions,
)


class ContradictionTests(unittest.TestCase):
    def test_legacy_support_hours(self):
        clean = "NORTHSTAR IT HELPDESK. Monday to Friday, from 9:00 AM to 5:00 PM."
        poisoned = "NORTHSTAR IT HELPDESK is available around the clock."
        self.assertEqual(extract_support_hours(clean), "weekdays_9_to_5")
        self.assertEqual(extract_support_hours(poisoned), "24/7")
        results = detect_contradictions([
            {"source": "northstar_official_policy.txt", "content": clean},
            {"source": "northstar_injected_policy.txt", "content": poisoned},
        ])
        self.assertEqual(len(results), 1)

    def test_refund_window_conflict(self):
        trusted = "Organization: Acme Store\nRefunds are available within 30 days."
        candidate = "Organization: Acme Store\nRefunds are available within 7 days."
        conflicts = compare_policy_claims(candidate, trusted)
        self.assertEqual(conflicts[0]["type"], "refund_window_days")
        self.assertEqual(conflicts[0]["candidate_claim"], 7)
        self.assertEqual(conflicts[0]["trusted_claim"], 30)

    def test_password_policy_conflict(self):
        trusted = "Organization: Blue Bank\nPassword must be at least 12 characters."
        candidate = "Organization: Blue Bank\nPassword must be at least 8 characters."
        self.assertEqual(compare_policy_claims(candidate, trusted)[0]["type"], "password_min_length")

    def test_retention_policy_conflict(self):
        trusted = "Organization: City Portal\nLogs are retained for 90 days."
        candidate = "Organization: City Portal\nLogs are retained for 30 days."
        self.assertEqual(compare_policy_claims(candidate, trusted)[0]["type"], "data_retention_days")

    def test_different_organizations_not_compared(self):
        trusted = "Organization: Acme Store\nRefunds are available within 30 days."
        candidate = "Organization: Other Store\nRefunds are available within 7 days."
        self.assertEqual(compare_policy_claims(candidate, trusted), [])

    def test_claim_extraction(self):
        claims = extract_policy_claims("Organization: Demo\nRefunds within 14 days. Password at least 10 characters. Logs retained for 60 days.")
        self.assertEqual(claims["refund_window_days"], 14)
        self.assertEqual(claims["password_min_length"], 10)
        self.assertEqual(claims["data_retention_days"], 60)


if __name__ == "__main__":
    unittest.main()
