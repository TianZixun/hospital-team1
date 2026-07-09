import unittest
from datetime import datetime

from hospital_team1.models import Patient, TriageLevel
from hospital_team1.simulation.compliance import is_wait_time_compliant


def _make_patient(triage_level: TriageLevel) -> Patient:
    """构造一个最小化的 Patient 用于合规测试。"""
    return Patient(
        patient_id="test",
        name="Test",
        age=30,
        triage_level=triage_level,
        arrival_time=datetime(2026, 6, 30, 8, 0, 0),
        estimated_treatment_minutes=10,
    )


class TestCompliance(unittest.TestCase):
    def test_critical_zero_wait_compliant(self) -> None:
        self.assertTrue(is_wait_time_compliant(_make_patient(TriageLevel.CRITICAL), 0))

    def test_critical_any_wait_noncompliant(self) -> None:
        self.assertFalse(is_wait_time_compliant(_make_patient(TriageLevel.CRITICAL), 1))

    def test_urgent_at_limit_compliant(self) -> None:
        self.assertTrue(is_wait_time_compliant(_make_patient(TriageLevel.URGENT), 20))

    def test_urgent_over_limit_noncompliant(self) -> None:
        self.assertFalse(is_wait_time_compliant(_make_patient(TriageLevel.URGENT), 21))

    def test_semi_urgent_at_limit_compliant(self) -> None:
        self.assertTrue(
            is_wait_time_compliant(_make_patient(TriageLevel.SEMI_URGENT), 35)
        )

    def test_semi_urgent_over_limit_noncompliant(self) -> None:
        self.assertFalse(
            is_wait_time_compliant(_make_patient(TriageLevel.SEMI_URGENT), 36)
        )

    def test_non_urgent_at_limit_compliant(self) -> None:
        self.assertTrue(
            is_wait_time_compliant(_make_patient(TriageLevel.NON_URGENT), 60)
        )

    def test_non_urgent_over_limit_noncompliant(self) -> None:
        self.assertFalse(
            is_wait_time_compliant(_make_patient(TriageLevel.NON_URGENT), 61)
        )

    def test_float_boundary_exactly_at_limit(self) -> None:
        self.assertTrue(
            is_wait_time_compliant(_make_patient(TriageLevel.URGENT), 20.0)
        )

    def test_float_boundary_barely_over(self) -> None:
        self.assertFalse(
            is_wait_time_compliant(_make_patient(TriageLevel.URGENT), 20.001)
        )


if __name__ == "__main__":
    unittest.main()
