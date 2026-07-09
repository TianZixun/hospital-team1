from __future__ import annotations

from datetime import datetime

from hospital_team1.data.csv_loader import load_patients_from_csv
from hospital_team1.models import Patient
from hospital_team1.simulation.shift_simulation import (
    DEFAULT_WORKSTATION_COUNT,
    build_queue_snapshot,
    project_waiting_starts,
)


class TimeoutPredictor:
    """Predict which waiting patients may exceed their max waiting time."""

    def __init__(self, workstation_count: int = DEFAULT_WORKSTATION_COUNT) -> None:
        self.workstation_count = workstation_count

    def predict_timeouts(
        self,
        current_time: datetime,
        queue: list[Patient],
        station_available_times: list[datetime] | None = None,
    ) -> set[str]:
        predicted: set[str] = set()
        projected_starts = project_waiting_starts(
            queue,
            current_time=current_time,
            station_available_times=station_available_times,
            workstation_count=self.workstation_count,
        )
        for patient in queue:
            patient_id = str(patient.patient_id)
            projected_start = projected_starts[patient_id]
            actual_wait = (
                projected_start - patient.arrival_time
            ).total_seconds() / 60
            if actual_wait > patient.get_max_allowed_wait():
                predicted.add(patient_id)
        return predicted


def summarize_timeout_risk(
    current_time: datetime | None = None,
    patients: list[Patient] | None = None,
) -> dict[str, object]:
    if patients is None:
        patients = load_patients_from_csv()
    if not patients:
        return {"risk_percent": 0, "at_risk_ids": [], "details": []}

    if current_time is None:
        current_time = datetime(2026, 6, 30, 14, 0, 0)

    snapshot = build_queue_snapshot(
        patients,
        snapshot_time=current_time,
        workstation_count=DEFAULT_WORKSTATION_COUNT,
    )
    waiting_patients = snapshot["waiting_patients"]
    predictor = TimeoutPredictor(workstation_count=DEFAULT_WORKSTATION_COUNT)
    at_risk_ids = sorted(
        predictor.predict_timeouts(
            current_time,
            waiting_patients,
            station_available_times=snapshot["station_available_times"],
        )
    )
    risk_percent = round((len(at_risk_ids) / max(len(waiting_patients), 1)) * 100)

    details = []
    for patient in waiting_patients:
        if str(patient.patient_id) in at_risk_ids:
            details.append(
                {
                    "patient_id": str(patient.patient_id),
                    "name": patient.name,
                    "triage": patient.triage_level.name.replace("_", " ").title(),
                }
            )

    return {
        "risk_percent": risk_percent,
        "at_risk_ids": at_risk_ids,
        "details": details[:5],
        "queue_size": len(waiting_patients),
    }
