from datetime import datetime, timedelta
import unittest
from unittest.mock import patch

from hospital_team1.models import Patient, TriageLevel
from hospital_team1.simulation.engine import SimulationConfig, SimulationEngine
from hospital_team1.simulation.shift_simulation import (
    SHIFT_START,
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
        arrival_time=datetime(2026, 6, 30, 8, 0, 0) + timedelta(minutes=minute),
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


    # ── 新增：边界与场景覆盖 ──────────────────────────────

    def test_empty_patient_list(self) -> None:
        """空病人列表 → 返回空 records 和空 untreated。"""
        result = run_shift_simulation([], workstation_count=1)
        self.assertEqual(len(result["records"]), 0)
        self.assertEqual(len(result["untreated"]), 0)

    def test_single_critical_patient(self) -> None:
        """单个危重病人 → 立即治疗，等待时间为 0，合规。"""
        patients = [make_patient("1", TriageLevel.CRITICAL, 0, 30)]
        result = run_shift_simulation(patients, workstation_count=1)
        self.assertEqual(len(result["records"]), 1)
        self.assertEqual(result["records"][0]["wait_minutes"], 0.0)
        self.assertTrue(result["records"][0]["within_threshold"])

    def test_single_non_urgent_patient(self) -> None:
        """单个非紧急病人 → 工作站空闲，等待为 0。"""
        patients = [make_patient("1", TriageLevel.NON_URGENT, 0, 30)]
        result = run_shift_simulation(patients, workstation_count=1)
        self.assertEqual(len(result["records"]), 1)
        self.assertEqual(result["records"][0]["wait_minutes"], 0.0)

    def test_same_priority_fifo_order(self) -> None:
        """同优先级不同到达时间 → 先到先治。"""
        patients = [
            make_patient("A", TriageLevel.URGENT, 0, 20),
            make_patient("B", TriageLevel.URGENT, 10, 20),
        ]
        result = run_shift_simulation(patients, workstation_count=1)
        ids = [r["patient"].patient_id for r in result["records"]]
        self.assertEqual(ids[0], "A")
        self.assertEqual(ids[1], "B")

    def test_different_priority_same_arrival(self) -> None:
        """不同优先级同时到达 → 高优先级先治（URGENT 在 NON_URGENT 之前）。"""
        patients = [
            make_patient("low", TriageLevel.NON_URGENT, 0, 20),
            make_patient("high", TriageLevel.URGENT, 0, 20),
        ]
        result = run_shift_simulation(patients, workstation_count=1)
        first_treated_triage = result["records"][0]["patient"].triage_level
        self.assertEqual(first_treated_triage, TriageLevel.URGENT)

    def test_workstation_all_full(self) -> None:
        """病人数 > 工作站数 → 多出的病人进入 waiting。"""
        patients = [
            make_patient(str(i), TriageLevel.NON_URGENT, 0, 30)
            for i in range(1, 5)  # 4 patients, 3 workstations
        ]
        snapshot = build_queue_snapshot(
            patients,
            snapshot_time=datetime(2026, 6, 30, 8, 5, 0),
            workstation_count=3,
        )
        self.assertEqual(len(snapshot["in_service_patients"]), 3)
        self.assertEqual(len(snapshot["waiting_patients"]), 1)

    def test_critical_jumps_queue(self) -> None:
        """CRITICAL 到达时无论队列多长都立即治疗，wait=0。"""
        patients = [
            make_patient("1", TriageLevel.NON_URGENT, 0, 60),
            make_patient("2", TriageLevel.CRITICAL, 5, 30),
        ]
        result = run_shift_simulation(patients, workstation_count=1)
        critical = [r for r in result["records"]
                    if r["patient"].patient_id == "2"][0]
        self.assertEqual(critical["wait_minutes"], 0.0)
        self.assertTrue(critical["within_threshold"])

    def test_compliance_boundary_exact_60min(self) -> None:
        """NON_URGENT 刚好等 60 分钟 → 合规。"""
        patients = [
            make_patient("blocker", TriageLevel.NON_URGENT, 0, 60),
            make_patient("waiter", TriageLevel.NON_URGENT, 0, 10),
        ]
        result = run_shift_simulation(patients, workstation_count=1)
        waiter = [r for r in result["records"]
                  if r["patient"].patient_id == "waiter"][0]
        self.assertEqual(waiter["wait_minutes"], 60.0)
        self.assertTrue(waiter["within_threshold"])

    def test_noncompliance_61min(self) -> None:
        """NON_URGENT 等 61 分钟 → 不合规。"""
        patients = [
            make_patient("blocker", TriageLevel.NON_URGENT, 0, 61),
            make_patient("waiter", TriageLevel.NON_URGENT, 0, 10),
        ]
        result = run_shift_simulation(patients, workstation_count=1)
        waiter = [r for r in result["records"]
                  if r["patient"].patient_id == "waiter"][0]
        self.assertEqual(waiter["wait_minutes"], 61.0)
        self.assertFalse(waiter["within_threshold"])

    def test_untreated_after_shift_end(self) -> None:
        """病人到达后班次结束前排不到 → 进入 untreated。"""
        patients = [
            make_patient("long", TriageLevel.NON_URGENT, 0, 500),
            make_patient("late", TriageLevel.NON_URGENT, 240, 10),
        ]
        result = run_shift_simulation(patients, workstation_count=1)
        self.assertGreater(len(result["untreated"]), 0)
        untreated_ids = [p.patient_id for p in result["untreated"]]
        self.assertIn("late", untreated_ids)

    def test_project_waiting_starts_empty_queue(self) -> None:
        """空等待队列 → 返回空字典。"""
        result = project_waiting_starts(
            [],
            current_time=datetime(2026, 6, 30, 8, 0, 0),
            workstation_count=1,
        )
        self.assertEqual(result, {})

    def test_run_shift_simulation_eight_hour_shift(self) -> None:
        """班次起点固定为 SHIFT_START（8:00），snapshot 截止 8 小时后。"""
        patients = [make_patient("1", TriageLevel.URGENT, 0, 20)]
        result = run_shift_simulation(patients)
        self.assertEqual(result["shift_start"], SHIFT_START)
        shift_end_limit = SHIFT_START + timedelta(hours=8)
        for record in result["records"]:
            self.assertLessEqual(record["treatment_time"], shift_end_limit)


if __name__ == "__main__":
    unittest.main()
