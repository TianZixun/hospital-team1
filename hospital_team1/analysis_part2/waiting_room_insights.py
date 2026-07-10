from __future__ import annotations

from datetime import datetime

from hospital_team1.data_part1.csv_loader import load_patients_from_csv
from hospital_team1.simulation_part2.shift_simulation import (
    DEFAULT_WORKSTATION_COUNT,
    build_queue_snapshot,
)
from hospital_team1.structures_part1 import WaitingRoom

from .waiting_room_analytics import (
    detect_priority_inversions,
    estimate_wait_for_new_patient,
)


def _build_waiting_room(current_time: datetime) -> tuple[WaitingRoom, list[datetime]]:
    snapshot = build_queue_snapshot(
        load_patients_from_csv(),
        snapshot_time=current_time,
        workstation_count=DEFAULT_WORKSTATION_COUNT,
    )
    waiting_room = WaitingRoom()
    for patient in snapshot["waiting_patients"]:
        waiting_room.add_patient(patient)
    return waiting_room, snapshot["station_available_times"]


def detect_priority_anomalies(
    current_time: datetime | None = None,
) -> list[dict[str, object]]:
    if current_time is None:
        current_time = datetime(2026, 6, 30, 14, 0, 0)
    waiting_room, _ = _build_waiting_room(current_time)
    return detect_priority_inversions(waiting_room, current_time)


def estimate_wait_time_for_new_arrival(
    current_time: datetime | None = None,
) -> dict:
    if current_time is None:
        current_time = datetime(2026, 6, 30, 14, 0, 0)
    waiting_room, station_available_times = _build_waiting_room(current_time)
    return estimate_wait_for_new_patient(
        waiting_room,
        current_time,
        station_available_times=station_available_times,
        workstation_count=DEFAULT_WORKSTATION_COUNT,
    )
