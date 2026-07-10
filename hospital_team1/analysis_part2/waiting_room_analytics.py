from __future__ import annotations

from datetime import datetime

from hospital_team1.models_part1 import Patient, TriageLevel
from hospital_team1.simulation_part2.shift_simulation import (
    DEFAULT_WORKSTATION_COUNT,
    project_waiting_starts,
)
from hospital_team1.structures_part1 import WaitingRoom


TRIAGE_ORDER = [
    TriageLevel.CRITICAL,
    TriageLevel.URGENT,
    TriageLevel.SEMI_URGENT,
    TriageLevel.NON_URGENT,
]

MINIMUM_TRIAGE_WAIT_ESTIMATES = {
    TriageLevel.CRITICAL: 0.0,
    TriageLevel.URGENT: 8.0,
    TriageLevel.SEMI_URGENT: 15.0,
    TriageLevel.NON_URGENT: 25.0,
}


def analyze_avg_wait_by_triage(
    waiting_room: WaitingRoom, current_time: datetime
) -> dict:
    groups: dict[TriageLevel | str, dict | datetime | int] = {}
    for level in TRIAGE_ORDER:
        groups[level] = {
            "count": 0,
            "total_wait": 0.0,
            "avg_wait": 0.0,
            "max_wait": 0.0,
            "threshold": level.value,
            "violations": 0,
        }

    total_patients = 0
    for patient in waiting_room.get_all_waiting_patients():
        if patient.arrival_time > current_time:
            continue
        total_patients += 1
        wait_minutes = max(patient.calculate_wait_minutes(current_time), 0.0)
        group = groups[patient.triage_level]
        group["count"] += 1
        group["total_wait"] += wait_minutes
        group["max_wait"] = max(group["max_wait"], wait_minutes)
        group["threshold"] = patient.get_max_allowed_wait()
        if wait_minutes > patient.get_max_allowed_wait():
            group["violations"] += 1

    for level in TRIAGE_ORDER:
        group = groups[level]
        if group["count"]:
            group["avg_wait"] = group["total_wait"] / group["count"]

    groups["current_time"] = current_time
    groups["total_patients"] = total_patients
    return groups


def detect_priority_inversions(
    waiting_room: WaitingRoom, current_time: datetime
) -> list[dict[str, object]]:
    active_patients = [
        patient
        for patient in waiting_room.get_all_waiting_patients()
        if patient.arrival_time <= current_time
    ]
    inversions: list[dict[str, object]] = []

    for index, patient_a in enumerate(active_patients):
        wait_a = max(patient_a.calculate_wait_minutes(current_time), 0.0)
        for patient_b in active_patients[index + 1 :]:
            if patient_a.triage_level == patient_b.triage_level:
                continue
            wait_b = max(patient_b.calculate_wait_minutes(current_time), 0.0)
            if patient_a.triage_level.value < patient_b.triage_level.value:
                higher, lower = patient_a, patient_b
                higher_wait, lower_wait = wait_a, wait_b
            else:
                higher, lower = patient_b, patient_a
                higher_wait, lower_wait = wait_b, wait_a

            if higher.arrival_time < lower.arrival_time and higher_wait > lower_wait:
                inversions.append(
                    {
                        "higher_priority": higher,
                        "lower_priority": lower,
                        "higher_wait": round(higher_wait, 1),
                        "lower_wait": round(lower_wait, 1),
                        "wait_gap": round(higher_wait - lower_wait, 1),
                    }
                )

    inversions.sort(key=lambda item: item["wait_gap"], reverse=True)
    return inversions


def estimate_wait_for_new_patient(
    waiting_room: WaitingRoom,
    current_time: datetime,
    slot_interval: int = 20,
    station_available_times: list[datetime] | None = None,
    workstation_count: int = DEFAULT_WORKSTATION_COUNT,
) -> dict:
    active_patients = [
        patient
        for patient in waiting_room.get_all_waiting_patients()
        if patient.arrival_time <= current_time
    ]

    estimates: dict[TriageLevel | str, dict | datetime | int] = {}
    for level in TRIAGE_ORDER:
        if level == TriageLevel.CRITICAL:
            estimates[level] = {
                "patients_ahead": 0,
                "estimated_wait_minutes": 0.0,
            }
            continue

        preview_patient = Patient(
            patient_id=f"preview-{level.name.lower()}",
            name="Preview",
            age=0,
            triage_level=level,
            arrival_time=current_time,
            estimated_treatment_minutes=slot_interval,
        )
        projected_queue = list(active_patients) + [preview_patient]
        projected_queue.sort()
        patients_ahead = 0
        for patient in projected_queue:
            if patient is preview_patient:
                break
            patients_ahead += 1

        projected_starts = project_waiting_starts(
            projected_queue,
            current_time=current_time,
            station_available_times=station_available_times,
            workstation_count=workstation_count,
        )
        start_time = projected_starts[str(preview_patient.patient_id)]
        projected_wait = max(
            (start_time - current_time).total_seconds() / 60, 0.0
        )
        estimates[level] = {
            "patients_ahead": patients_ahead,
            "estimated_wait_minutes": max(
                projected_wait,
                MINIMUM_TRIAGE_WAIT_ESTIMATES[level],
            ),
        }

    estimates["total_in_queue"] = len(active_patients)
    estimates["slot_interval"] = slot_interval
    estimates["current_time"] = current_time
    return estimates


def run_waiting_room_analytics(
    waiting_room: WaitingRoom,
    current_time: datetime,
    slot_interval: int = 20,
    station_available_times: list[datetime] | None = None,
    workstation_count: int = DEFAULT_WORKSTATION_COUNT,
) -> dict[str, object]:
    return {
        "avg_wait": analyze_avg_wait_by_triage(waiting_room, current_time),
        "inversions": detect_priority_inversions(waiting_room, current_time),
        "estimates": estimate_wait_for_new_patient(
            waiting_room,
            current_time,
            slot_interval,
            station_available_times=station_available_times,
            workstation_count=workstation_count,
        ),
    }
