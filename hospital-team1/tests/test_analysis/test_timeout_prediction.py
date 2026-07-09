from datetime import datetime
import unittest

from hospital_team1.analysis.timeout_prediction import summarize_timeout_risk
from hospital_team1.models import Patient, TriageLevel


class TestTimeoutPrediction(unittest.TestCase):
    def test_updated_wait_thresholds(self) -> None:
        patient_specs = [
            (TriageLevel.CRITICAL, 0),
            (TriageLevel.URGENT, 20),
            (TriageLevel.SEMI_URGENT, 35),
            (TriageLevel.NON_URGENT, 60),
        ]

        for level, expected_limit in patient_specs:
            patient = Patient(
                patient_id=level.name,
                name=level.name,
                age=30,
                triage_level=level,
                arrival_time=datetime(2026, 6, 30, 8, 0, 0),
                estimated_treatment_minutes=15,
            )
            self.assertEqual(patient.get_max_allowed_wait(), expected_limit)

    def test_timeout_risk_snapshot_is_not_full_queue(self) -> None:
        summary = summarize_timeout_risk(datetime(2026, 6, 30, 10, 0, 0))

        self.assertLess(summary["risk_percent"], 100)
        self.assertGreaterEqual(summary["queue_size"], len(summary["at_risk_ids"]))


if __name__ == "__main__":
    unittest.main()
