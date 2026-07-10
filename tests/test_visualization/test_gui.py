from datetime import datetime, timedelta
import unittest
from unittest.mock import patch

from hospital_team1.models_part1 import Patient, TriageLevel
from hospital_team1.visualization_part2 import create_app
from hospital_team1.visualization_part2.dashboard_data import (
    add_runtime_patient,
    complete_runtime_patient,
    get_dashboard_context,
    reset_runtime_state,
)


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
        reset_runtime_state()
        self.app = create_app()
        self.client = self.app.test_client()

    def tearDown(self) -> None:
        reset_runtime_state()

    def test_dashboard_route_renders(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        body = response.get_data(as_text=True)
        self.assertIn("Hospital Triage Scheduler", body)
        self.assertIn("Quick Actions", body)
        self.assertIn("Performance Analysis", body)
        self.assertIn("Completed Patients", body)
        self.assertNotIn("Project Structure", body)
        self.assertNotIn("Content Slots", body)

    def test_dashboard_route_accepts_snapshot_offset(self) -> None:
        response = self.client.get("/?snapshot_offset=20")

        self.assertEqual(response.status_code, 200)
        query = response.request.path + "?" + response.request.query_string.decode()
        self.assertIn("snapshot_offset", query)

    def test_dashboard_route_accepts_queue_mode(self) -> None:
        response = self.client.get("/?snapshot_offset=20&queue_mode=ordered_list")

        self.assertEqual(response.status_code, 200)
        body = response.get_data(as_text=True)
        self.assertIn('data-current-queue-mode="ordered_list"', body)
        self.assertIn("Ordered Linked Queue", body)

    def test_dashboard_context_uses_live_active_queue(self) -> None:
        context = get_dashboard_context(0)

        self.assertEqual(context["summary_cards"][0]["value"], "1")
        self.assertEqual(context["system_overview"]["snapshot_clock"], "10:00:00")
        self.assertTrue(context["system_overview"]["real_clock"])
        self.assertEqual(len(context["waiting_room_patients"]), 10)
        self.assertEqual(context["waiting_room_patients"][0]["patient_id"], "P0006")
        self.assertEqual(
            context["waiting_room_patients"][0]["status"],
            "In Service (就诊中)",
        )
        self.assertIn(
            "Scheduled (即将到达)",
            {patient["status"] for patient in context["waiting_room_patients"]},
        )
        self.assertEqual(context["overtime_card"]["details"][0][1], "1")

    @patch("hospital_team1.visualization_part2.dashboard_data.run_shift_simulation")
    @patch("hospital_team1.visualization_part2.dashboard_data.build_queue_snapshot")
    @patch("hospital_team1.visualization_part2.dashboard_data.load_patients_from_csv")
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
        self.assertEqual(
            context["waiting_room_patients"][0]["status"],
            "Waiting (候诊中)",
        )
        self.assertEqual(context["waiting_room_patients"][-1]["patient_id"], "P0010")

    @patch("hospital_team1.visualization_part2.dashboard_data.run_shift_simulation")
    @patch("hospital_team1.visualization_part2.dashboard_data.build_queue_snapshot")
    @patch("hospital_team1.visualization_part2.dashboard_data.load_patients_from_csv")
    def test_heap_and_predicted_waits_follow_priority_order(
        self,
        mock_load_patients,
        mock_build_queue_snapshot,
        mock_run_shift_simulation,
    ) -> None:
        patients = [
            Patient(
                patient_id="1",
                name="Non",
                age=20,
                triage_level=TriageLevel.NON_URGENT,
                arrival_time=datetime(2026, 6, 30, 9, 0, 0),
                estimated_treatment_minutes=10,
            ),
            Patient(
                patient_id="2",
                name="Semi",
                age=20,
                triage_level=TriageLevel.SEMI_URGENT,
                arrival_time=datetime(2026, 6, 30, 9, 1, 0),
                estimated_treatment_minutes=10,
            ),
            Patient(
                patient_id="3",
                name="Urgent",
                age=20,
                triage_level=TriageLevel.URGENT,
                arrival_time=datetime(2026, 6, 30, 9, 2, 0),
                estimated_treatment_minutes=10,
            ),
            Patient(
                patient_id="4",
                name="Critical",
                age=20,
                triage_level=TriageLevel.CRITICAL,
                arrival_time=datetime(2026, 6, 30, 9, 3, 0),
                estimated_treatment_minutes=10,
            ),
        ]
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
        heap_items = [item for level in context["heap_levels"] for item in level]
        predicted_waits = [
            float(row["wait"].replace(" min", ""))
            for row in context["predicted_rows"]
        ]

        self.assertEqual(
            [item["priority"].split(" ")[0] for item in heap_items[:4]],
            [
                "Critical",
                "Urgent",
                "Semi-Urgent",
                "Non-Urgent",
            ],
        )
        self.assertEqual(predicted_waits, sorted(predicted_waits))
        self.assertLess(predicted_waits[-1], 60.0)

    def test_run_simulation_action_returns_json(self) -> None:
        response = self.client.get("/api/actions/run-simulation?snapshot_offset=20")

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertIsInstance(payload, dict)
        self.assertIn("message", payload)
        self.assertIn("summary", payload)
        self.assertIn("treated_patients", payload["summary"])

    def test_add_patient_action_returns_json_and_patient_waits(self) -> None:
        response = self.client.post("/api/actions/add-patient?snapshot_offset=0")

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertIn("message", payload)
        self.assertIn("patient", payload)
        self.assertTrue(payload["patient"]["name"].startswith("Walk-in"))

        context = get_dashboard_context(0)
        added_patient = next(
            patient
            for patient in context["waiting_room_patients"]
            if patient["patient_id"] == payload["patient"]["patient_id"]
        )
        self.assertEqual(added_patient["status"], "Waiting (候诊中)")

    def test_complete_patient_action_rejects_active_patient(self) -> None:
        patient = add_runtime_patient(0)
        raw_id = str(int(patient["patient_id"].replace("P", "")))

        response = self.client.post(
            f"/api/actions/complete-patient/{raw_id}?snapshot_offset=0"
        )

        self.assertEqual(response.status_code, 404)
        payload = response.get_json()
        self.assertFalse(payload["ok"])

    @patch("hospital_team1.visualization_part2.dashboard_data.build_queue_snapshot")
    @patch("hospital_team1.visualization_part2.dashboard_data.load_patients_from_csv")
    def test_complete_patient_action_removes_completed_patient(
        self,
        mock_load_patients,
        mock_build_queue_snapshot,
    ) -> None:
        patient = Patient(
            patient_id="99",
            name="Finished Patient",
            age=40,
            triage_level=TriageLevel.URGENT,
            arrival_time=datetime(2026, 6, 30, 8, 30, 0),
            estimated_treatment_minutes=15,
        )
        mock_load_patients.return_value = [patient]
        def fake_snapshot(patients, snapshot_time, workstation_count):
            if not patients:
                return {
                    "records": [],
                    "waiting_patients": [],
                    "in_service_patients": [],
                    "station_available_times": [datetime(2026, 6, 30, 10, 0, 0)],
                }
            return {
                "records": [
                    {
                        "patient": patient,
                        "treatment_time": datetime(2026, 6, 30, 9, 0, 0),
                        "wait_minutes": 30.0,
                        "max_allowed": 20,
                        "within_threshold": False,
                    }
                ],
                "waiting_patients": [],
                "in_service_patients": [],
                "station_available_times": [datetime(2026, 6, 30, 10, 0, 0)],
            }

        mock_build_queue_snapshot.side_effect = fake_snapshot

        response = self.client.post("/api/actions/complete-patient/99?snapshot_offset=0")

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload["ok"])
        second_try = complete_runtime_patient("99", 0)
        self.assertFalse(second_try["ok"])

    def test_favicon_route_returns_asset(self) -> None:
        response = self.client.get("/favicon.ico")

        self.assertEqual(response.status_code, 200)
        self.assertIn("image/svg+xml", response.content_type)
        response.close()


if __name__ == "__main__":
    unittest.main()
