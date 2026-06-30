from datetime import datetime
import unittest

from hospital_team1.models import Patient, TriageLevel


class TestPatient(unittest.TestCase):
    def test_repr_contains_core_fields(self) -> None:
        patient = Patient(
            patient_id="P001",
            name="Alice",
            age=30,
            triage_level=TriageLevel.URGENT,
            arrival_time=datetime(2026, 6, 30, 8, 0),
            estimated_treatment_minutes=25,
        )

        rendered = repr(patient)

        self.assertIn("P001", rendered)
        self.assertIn("Alice", rendered)
        self.assertIn("URGENT", rendered)

    def test_lt_uses_priority_before_arrival_time(self) -> None:
        urgent = Patient(
            patient_id="P001",
            name="Alice",
            age=30,
            triage_level=TriageLevel.URGENT,
            arrival_time=datetime(2026, 6, 30, 8, 10),
            estimated_treatment_minutes=25,
        )
        semi_urgent = Patient(
            patient_id="P002",
            name="Bob",
            age=28,
            triage_level=TriageLevel.SEMI_URGENT,
            arrival_time=datetime(2026, 6, 30, 8, 0),
            estimated_treatment_minutes=25,
        )

        self.assertLess(urgent, semi_urgent)

    def test_lt_breaks_ties_by_arrival_time(self) -> None:
        earlier = Patient(
            patient_id="P001",
            name="Alice",
            age=30,
            triage_level=TriageLevel.URGENT,
            arrival_time=datetime(2026, 6, 30, 8, 0),
            estimated_treatment_minutes=25,
        )
        later = Patient(
            patient_id="P002",
            name="Bob",
            age=28,
            triage_level=TriageLevel.URGENT,
            arrival_time=datetime(2026, 6, 30, 8, 5),
            estimated_treatment_minutes=25,
        )

        self.assertLess(earlier, later)


if __name__ == "__main__":
    unittest.main()
