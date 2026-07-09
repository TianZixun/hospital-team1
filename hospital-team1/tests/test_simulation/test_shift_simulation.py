from datetime import datetime
import unittest
from unittest.mock import patch

from hospital_team1.models import Patient, TriageLevel
from hospital_team1.simulation.engine import SimulationConfig, SimulationEngine
from hospital_team1.simulation.shift_simulation import (
    build_queue_snapshot,
    project_waiting_starts,
    run_shift_simulation,
)


def make_patient(
    patient_id: str,
    triage_level: TriageLevel,
    minute: int,
    duration: int,
) -> Patient:
    return Patient(
        patient_id=patient_id,
        name=f"Patient-{patient_id}",
        age=30,
        triage_level=triage_level,
        arrival_time=datetime(2026, 6, 30, 8, minute, 0),
        estimated_treatment_minutes=duration,
    )


class TestShiftSimulation(unittest.TestCase):
    def test_build_queue_snapshot_keeps_critical_immediate_and_waits_others(self) -> None:
        patients = [
            make_patient("1", TriageLevel.NON_URGENT, 0, 30),
            make_patient("2", TriageLevel.URGENT, 5, 20),
            make_patient("3", TriageLevel.CRITICAL, 10, 40),
        ]

        snapshot = build_queue_snapshot(
            patients,
            snapshot_time=datetime(2026, 6, 30, 8, 15, 0),
            workstation_count=1,
        )

        self.assertEqual(
            [patient.patient_id for patient in snapshot["waiting_patients"]],
            ["2"],
        )
        self.assertEqual(
            [patient.patient_id for patient in snapshot["in_service_patients"]],
            ["3", "1"],
        )
        self.assertEqual(snapshot["records"][1]["patient"].patient_id, "3")
        self.assertEqual(snapshot["records"][1]["wait_minutes"], 0.0)

    def test_project_waiting_starts_uses_station_availability(self) -> None:
        waiting_patients = [
            make_patient("2", TriageLevel.URGENT, 5, 20),
            make_patient("4", TriageLevel.NON_URGENT, 8, 10),
        ]
        current_time = datetime(2026, 6, 30, 8, 15, 0)
        starts = project_waiting_starts(
            waiting_patients,
            current_time=current_time,
            station_available_times=[datetime(2026, 6, 30, 8, 30, 0)],
            workstation_count=1,
        )

        self.assertEqual(starts["2"], datetime(2026, 6, 30, 8, 30, 0))
        self.assertEqual(starts["4"], datetime(2026, 6, 30, 8, 50, 0))

    def test_run_shift_simulation_returns_records_and_threshold_flags(self) -> None:
        patients = [
            make_patient("1", TriageLevel.NON_URGENT, 0, 30),
            make_patient("2", TriageLevel.URGENT, 5, 20),
            make_patient("3", TriageLevel.CRITICAL, 10, 40),
        ]

        result = run_shift_simulation(patients, workstation_count=1)

        self.assertEqual(len(result["records"]), 3)
        self.assertEqual(result["records"][0]["patient"].patient_id, "1")
        self.assertEqual(result["records"][1]["patient"].patient_id, "3")
        self.assertFalse(result["records"][2]["within_threshold"])

    @patch("hospital_team1.simulation.engine.load_patients_from_csv")
    def test_simulation_engine_runs_with_loaded_patients(self, mock_load) -> None:
        mock_load.return_value = [
            make_patient("1", TriageLevel.URGENT, 0, 20),
            make_patient("2", TriageLevel.NON_URGENT, 15, 15),
        ]
        engine = SimulationEngine(
            SimulationConfig(
                workstation_open_interval_minutes=15,
                shift_start_time=datetime(2026, 6, 30, 8, 0, 0),
            )
        )

        result = engine.run()

        self.assertEqual(result["slot_interval"], 15)
        self.assertEqual(len(result["records"]), 2)


if __name__ == "__main__":
    unittest.main()
