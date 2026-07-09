from datetime import datetime, timedelta
import unittest

from hospital_team1.analysis.waiting_room_analytics import (
    analyze_avg_wait_by_triage,
    detect_priority_inversions,
    estimate_wait_for_new_patient,
    run_waiting_room_analytics,
)
from hospital_team1.models import Patient, TriageLevel
from hospital_team1.structures import WaitingRoom


def make_patient(
    patient_id: str,
    triage_level: TriageLevel,
    arrival_time: datetime,
    duration: int = 20,
) -> Patient:
    return Patient(
        patient_id=patient_id,
        name=f"Patient-{patient_id}",
        age=30,
        triage_level=triage_level,
        arrival_time=arrival_time,
        estimated_treatment_minutes=duration,
    )


class TestWaitingRoomAnalytics(unittest.TestCase):
    def test_analyze_avg_wait_by_triage_tracks_counts_and_violations(self) -> None:
        current_time = datetime(2026, 6, 30, 9, 0, 0)
        waiting_room = WaitingRoom()
        waiting_room.add_patient(
            make_patient("1", TriageLevel.URGENT, current_time - timedelta(minutes=40))
        )
        waiting_room.add_patient(
            make_patient("2", TriageLevel.NON_URGENT, current_time - timedelta(minutes=10))
        )

        summary = analyze_avg_wait_by_triage(waiting_room, current_time)

        self.assertEqual(summary[TriageLevel.URGENT]["count"], 1)
        self.assertEqual(summary[TriageLevel.URGENT]["violations"], 1)
        self.assertEqual(summary[TriageLevel.NON_URGENT]["count"], 1)
        self.assertEqual(summary["total_patients"], 2)

    def test_detect_priority_inversions_returns_wait_gap(self) -> None:
        current_time = datetime(2026, 6, 30, 9, 0, 0)
        waiting_room = WaitingRoom()
        waiting_room.add_patient(
            make_patient("1", TriageLevel.URGENT, current_time - timedelta(minutes=45))
        )
        waiting_room.add_patient(
            make_patient("2", TriageLevel.NON_URGENT, current_time - timedelta(minutes=10))
        )

        inversions = detect_priority_inversions(waiting_room, current_time)

        self.assertEqual(len(inversions), 1)
        self.assertEqual(inversions[0]["higher_priority"].patient_id, "1")
        self.assertGreater(inversions[0]["wait_gap"], 0)

    def test_estimate_wait_for_new_patient_uses_non_zero_minimum_buffers(self) -> None:
        estimates = estimate_wait_for_new_patient(
            WaitingRoom(),
            datetime(2026, 6, 30, 10, 0, 0),
        )

        self.assertEqual(estimates[TriageLevel.CRITICAL]["estimated_wait_minutes"], 0.0)
        self.assertEqual(estimates[TriageLevel.URGENT]["estimated_wait_minutes"], 8.0)
        self.assertEqual(
            estimates[TriageLevel.SEMI_URGENT]["estimated_wait_minutes"], 15.0
        )
        self.assertEqual(
            estimates[TriageLevel.NON_URGENT]["estimated_wait_minutes"], 25.0
        )

    def test_run_waiting_room_analytics_returns_combined_sections(self) -> None:
        current_time = datetime(2026, 6, 30, 9, 0, 0)
        waiting_room = WaitingRoom()
        waiting_room.add_patient(
            make_patient("1", TriageLevel.URGENT, current_time - timedelta(minutes=15))
        )

        analytics = run_waiting_room_analytics(
            waiting_room,
            current_time,
            station_available_times=[current_time + timedelta(minutes=5)],
            workstation_count=1,
        )

        self.assertIn("avg_wait", analytics)
        self.assertIn("inversions", analytics)
        self.assertIn("estimates", analytics)


if __name__ == "__main__":
    unittest.main()
