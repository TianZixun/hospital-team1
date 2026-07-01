from __future__ import annotations

from datetime import datetime, timedelta

from hospital_team1.data.csv_loader import load_patients_from_csv
from hospital_team1.models import Patient
from hospital_team1.queues import HeapPriorityQueue


class TimeoutPredictor:
    """Predict which patients may exceed their max waiting time."""

    def __init__(self, treatment_slots_per_hour: int = 3) -> None:
        self.slots_per_hour = treatment_slots_per_hour

    def predict_timeouts(
        self,
        current_time: datetime,
        queue: list[Patient],
        avg_treatment_time: float,
    ) -> set[str]:
        predicted: set[str] = set()
        for index, patient in enumerate(queue):
            wait_minutes = index * avg_treatment_time / self.slots_per_hour
            estimated_treatment_time = current_time + timedelta(minutes=wait_minutes)
            actual_wait = (
                estimated_treatment_time - patient.arrival_time
            ).total_seconds() / 60
            if actual_wait > patient.get_max_allowed_wait():
                predicted.add(str(patient.patient_id))
        return predicted

    def predict_timeouts_with_queue(
        self,
        current_time: datetime,
        heap_queue: HeapPriorityQueue,
        avg_treatment_time: float,
    ) -> set[str]:
        return self.predict_timeouts(
            current_time, heap_queue.get_all_sorted_patients(), avg_treatment_time
        )


def summarize_timeout_risk(
    current_time: datetime | None = None,
) -> dict[str, object]:
    patients = load_patients_from_csv()
    if not patients:
        return {"risk_percent": 0, "at_risk_ids": [], "details": []}

    if current_time is None:
        current_time = datetime(2026, 6, 30, 14, 0, 0)

    queue = HeapPriorityQueue()
    active_patients = [p for p in patients if p.arrival_time <= current_time]
    for patient in active_patients:
        queue.enqueue(patient)

    average_treatment = sum(
        patient.estimated_treatment_minutes for patient in active_patients
    ) / max(len(active_patients), 1)
    predictor = TimeoutPredictor(treatment_slots_per_hour=3)
    at_risk_ids = sorted(
        predictor.predict_timeouts_with_queue(current_time, queue, average_treatment)
    )
    risk_percent = round((len(at_risk_ids) / max(len(active_patients), 1)) * 100)

    details = []
    for patient in active_patients:
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
        "queue_size": len(active_patients),
    }
