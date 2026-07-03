import unittest

from hospital_team1.models import TriageLevel
from hospital_team1.simulation.compliance import is_wait_time_compliant


class TestCompliance(unittest.TestCase):
    def test_updated_thresholds_are_used(self) -> None:
        self.assertTrue(is_wait_time_compliant(TriageLevel.CRITICAL, 0))
        self.assertFalse(is_wait_time_compliant(TriageLevel.CRITICAL, 1))
        self.assertTrue(is_wait_time_compliant(TriageLevel.URGENT, 20))
        self.assertFalse(is_wait_time_compliant(TriageLevel.URGENT, 21))
        self.assertTrue(is_wait_time_compliant(TriageLevel.SEMI_URGENT, 35))
        self.assertFalse(is_wait_time_compliant(TriageLevel.SEMI_URGENT, 36))
        self.assertTrue(is_wait_time_compliant(TriageLevel.NON_URGENT, 60))
        self.assertFalse(is_wait_time_compliant(TriageLevel.NON_URGENT, 61))


if __name__ == "__main__":
    unittest.main()
