from __future__ import annotations

from datetime import datetime

from hospital_team1.data.csv_loader import load_patients_from_csv
from hospital_team1.structures import WaitingRoom

from .waiting_room_analytics import (
    detect_priority_inversions,
    estimate_wait_for_new_patient,
)


def _build_waiting_room() -> WaitingRoom:
    waiting_room = WaitingRoom()
    for patient in load_patients_from_csv():
        waiting_room.add_patient(patient)
    return waiting_room


def detect_priority_anomalies(
    current_time: datetime | None = None,
) -> list[dict[str, object]]:
    if current_time is None:
        current_time = datetime(2026, 6, 30, 14, 0, 0)
    return detect_priority_inversions(_build_waiting_room(), current_time)


def estimate_wait_time_for_new_arrival(
    current_time: datetime | None = None,
) -> dict:
    if current_time is None:
        current_time = datetime(2026, 6, 30, 14, 0, 0)
    return estimate_wait_for_new_patient(_build_waiting_room(), current_time)
