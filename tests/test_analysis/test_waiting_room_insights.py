from datetime import datetime
import unittest
from unittest.mock import patch

from hospital_team1.analysis_part2.waiting_room_insights import (
    detect_priority_anomalies,
    estimate_wait_time_for_new_arrival,
)
from hospital_team1.models_part1 import Patient, TriageLevel


def make_patient(
    patient_id: str,
    triage_level: TriageLevel,
    hour: int,
    minute: int,
    duration: int,
) -> Patient:
    return Patient(
        patient_id=patient_id,
        name=f"Patient-{patient_id}",
        age=30,
        triage_level=triage_level,
        arrival_time=datetime(2026, 6, 30, hour, minute, 0),
        estimated_treatment_minutes=duration,
    )


class TestWaitingRoomInsights(unittest.TestCase):
    @patch("hospital_team1.analysis_part2.waiting_room_insights.load_patients_from_csv")
    def test_detect_priority_anomalies_returns_list(self, mock_load) -> None:
        mock_load.return_value = [
            make_patient("1", TriageLevel.URGENT, 8, 0, 40),
            make_patient("2", TriageLevel.NON_URGENT, 8, 20, 10),
        ]

        anomalies = detect_priority_anomalies(datetime(2026, 6, 30, 9, 0, 0))

        self.assertIsInstance(anomalies, list)

    @patch("hospital_team1.analysis_part2.waiting_room_insights.load_patients_from_csv")
    def test_estimate_wait_time_for_new_arrival_returns_estimates(self, mock_load) -> None:
        mock_load.return_value = [
            make_patient("1", TriageLevel.NON_URGENT, 8, 0, 30),
        ]

        estimates = estimate_wait_time_for_new_arrival(
            datetime(2026, 6, 30, 8, 10, 0)
        )

        self.assertIn(TriageLevel.URGENT, estimates)
        self.assertGreaterEqual(
            estimates[TriageLevel.URGENT]["estimated_wait_minutes"], 8.0
        )


if __name__ == "__main__":
    unittest.main()
