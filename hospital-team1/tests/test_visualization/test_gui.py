from datetime import datetime, timedelta
import unittest
from unittest.mock import patch

from hospital_team1.models import Patient, TriageLevel
from hospital_team1.visualization import create_app
from hospital_team1.visualization.dashboard_data import get_dashboard_context


def make_patient(index: int) -> Patient:
    return Patient(
        patient_id=str(index),
        name=f"Patient-{index}",
        age=30,
        triage_level=TriageLevel.NON_URGENT,
        arrival_time=datetime(2026, 6, 30, 9, 0, 0) + timedelta(minutes=index),
        estimated_treatment_minutes=20,
    )


class TestDashboardApp(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app()
        self.client = self.app.test_client()

    def test_dashboard_route_renders(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        body = response.get_data(as_text=True)
        self.assertIn("Hospital Triage Scheduler", body)
        self.assertIn("Quick Actions", body)
        self.assertIn("Performance Analysis", body)

    def test_dashboard_route_accepts_snapshot_offset(self) -> None:
        response = self.client.get("/?snapshot_offset=20")

        self.assertEqual(response.status_code, 200)
        self.assertIn("snapshot_offset", response.request.path + "?" + response.request.query_string.decode())

    def test_dashboard_context_uses_live_active_queue(self) -> None:
        context = get_dashboard_context(0)

        self.assertEqual(context["summary_cards"][0]["value"], "1")
        self.assertEqual(len(context["waiting_room_patients"]), 10)
        self.assertEqual(context["waiting_room_patients"][0]["patient_id"], "P0006")
        self.assertEqual(context["waiting_room_patients"][0]["status"], "In Service (正在接诊)")
        self.assertIn(
            "Scheduled (即将到达)",
            {patient["status"] for patient in context["waiting_room_patients"]},
        )
        self.assertEqual(context["overtime_card"]["details"][0][1], "1")

    @patch("hospital_team1.visualization.dashboard_data.run_shift_simulation")
    @patch("hospital_team1.visualization.dashboard_data.build_queue_snapshot")
    @patch("hospital_team1.visualization.dashboard_data.load_patients_from_csv")
    def test_dashboard_context_shows_up_to_ten_queue_patients(
        self,
        mock_load_patients,
        mock_build_queue_snapshot,
        mock_run_shift_simulation,
    ) -> None:
        patients = [make_patient(index) for index in range(1, 13)]
        mock_load_patients.return_value = patients
        mock_build_queue_snapshot.return_value = {
            "records": [],
            "waiting_patients": patients,
            "in_service_patients": [],
            "station_available_times": [datetime(2026, 6, 30, 10, 0, 0)],
        }
        mock_run_shift_simulation.return_value = {
            "records": [],
            "untreated": [],
            "slot_interval": 20,
            "shift_start": datetime(2026, 6, 30, 8, 0, 0),
            "shift_end": datetime(2026, 6, 30, 10, 0, 0),
        }

        context = get_dashboard_context(0)

        self.assertEqual(len(context["waiting_room_patients"]), 10)
        self.assertEqual(context["waiting_room_patients"][0]["patient_id"], "P0001")
        self.assertEqual(context["waiting_room_patients"][0]["status"], "Waiting (等待中)")
        self.assertEqual(context["waiting_room_patients"][-1]["patient_id"], "P0010")

    def test_run_simulation_action_returns_json(self) -> None:
        response = self.client.get("/api/actions/run-simulation?snapshot_offset=20")

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertIsInstance(payload, dict)
        self.assertIn("message", payload)
        self.assertIn("summary", payload)
        self.assertIn("treated_patients", payload["summary"])

    def test_favicon_route_returns_asset(self) -> None:
        response = self.client.get("/favicon.ico")

        self.assertEqual(response.status_code, 200)
        self.assertIn("image/svg+xml", response.content_type)
        response.close()


if __name__ == "__main__":
    unittest.main()
