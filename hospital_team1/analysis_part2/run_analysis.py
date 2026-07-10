from __future__ import annotations

from datetime import datetime
from pathlib import Path

from hospital_team1.analysis_part2.performance_analysis import (
    plot_results,
    run_performance_analysis,
    save_results_to_csv,
)
from hospital_team1.analysis_part2.timeout_prediction import summarize_timeout_risk
from hospital_team1.analysis_part2.waiting_room_analytics import run_waiting_room_analytics
from hospital_team1.data_part1.csv_loader import load_patients_from_csv
from hospital_team1.structures_part1 import WaitingRoom


def main() -> None:
    project_root = Path(__file__).resolve().parents[2]
    dataset_path = project_root / "datasets" / "patients_dataset.csv"
    patients = load_patients_from_csv(dataset_path)

    waiting_room = WaitingRoom()
    for patient in patients:
        waiting_room.add_patient(patient)

    current_time = datetime(2026, 6, 30, 14, 0, 0)
    waiting_results = run_waiting_room_analytics(waiting_room, current_time)
    timeout_summary = summarize_timeout_risk(current_time)
    performance_results = run_performance_analysis()

    save_results_to_csv(performance_results, project_root / "results" / "performance_results.csv")
    plot_results(performance_results, project_root / "results" / "performance_comparison.png")

    print("Waiting-room analytics:", waiting_results["avg_wait"]["total_patients"])
    print("Timeout summary:", timeout_summary["risk_percent"], "%")


if __name__ == "__main__":
    main()
