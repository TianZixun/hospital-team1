from __future__ import annotations

from datetime import datetime, timedelta

from hospital_team1.models import Patient, TriageLevel
from hospital_team1.simulation.compliance import is_wait_time_compliant


DEFAULT_WORKSTATION_COUNT = 3
SHIFT_START = datetime(2026, 6, 30, 8, 0, 0)


def _queue_sort_key(patient: Patient) -> tuple[int, int, datetime]:
    emergency_rank = 0 if patient.triage_level == TriageLevel.CRITICAL else 1
    return (emergency_rank, patient.triage_level.value, patient.arrival_time)


def _build_record(patient: Patient, start_time: datetime) -> dict[str, object]:
    wait_minutes = max((start_time - patient.arrival_time).total_seconds() / 60, 0.0)
    return {
        "patient": patient,
        "treatment_time": start_time,
        "wait_minutes": round(wait_minutes, 1),
        "max_allowed": patient.get_max_allowed_wait(),
        "within_threshold": is_wait_time_compliant(patient, wait_minutes),
    }


def _record_end_time(record: dict[str, object]) -> datetime:
    patient = record["patient"]
    return record["treatment_time"] + timedelta(
        minutes=patient.estimated_treatment_minutes
    )


def _normalise_station_times(
    current_time: datetime,
    station_available_times: list[datetime] | None,
    workstation_count: int,
) -> list[datetime]:
    if station_available_times:
        return [max(current_time, time_point) for time_point in station_available_times]
    return [current_time] * max(workstation_count, 1)


def build_queue_snapshot(
    patients: list[Patient],
    snapshot_time: datetime,
    workstation_count: int = DEFAULT_WORKSTATION_COUNT,
) -> dict[str, object]:
    if not patients:
        return {
            "records": [],
            "waiting_patients": [],
            "in_service_patients": [],
            "station_available_times": [snapshot_time] * max(workstation_count, 1),
        }

    arrived_patients = sorted(
        [patient for patient in patients if patient.arrival_time <= snapshot_time],
        key=lambda patient: patient.arrival_time,
    )
    station_available_times = [SHIFT_START] * max(workstation_count, 1)
    waiting: list[Patient] = []
    records: list[dict[str, object]] = []
    patient_index = 0

    def load_arrivals(until_time: datetime) -> None:
        nonlocal patient_index
        while (
            patient_index < len(arrived_patients)
            and arrived_patients[patient_index].arrival_time <= until_time
        ):
            patient = arrived_patients[patient_index]
            patient_index += 1
            if patient.triage_level == TriageLevel.CRITICAL:
                records.append(_build_record(patient, patient.arrival_time))
            else:
                waiting.append(patient)

    while patient_index < len(arrived_patients) or waiting:
        next_arrival = (
            arrived_patients[patient_index].arrival_time
            if patient_index < len(arrived_patients)
            else None
        )

        if waiting:
            next_station_available = min(station_available_times)
            if next_arrival is None:
                event_time = next_station_available
            else:
                event_time = min(next_arrival, next_station_available)
        else:
            if next_arrival is None:
                break
            event_time = next_arrival

        if event_time > snapshot_time:
            break

        load_arrivals(event_time)

        free_stations = [
            index
            for index, available_time in enumerate(station_available_times)
            if available_time <= event_time
        ]
        waiting.sort(key=_queue_sort_key)
        while free_stations and waiting:
            station_index = min(
                free_stations, key=lambda index: station_available_times[index]
            )
            free_stations.remove(station_index)
            patient = waiting.pop(0)
            records.append(_build_record(patient, event_time))
            station_available_times[station_index] = event_time + timedelta(
                minutes=patient.estimated_treatment_minutes
            )

    load_arrivals(snapshot_time)
    waiting.sort(key=_queue_sort_key)
    in_service = [
        record["patient"]
        for record in records
        if record["treatment_time"] <= snapshot_time < _record_end_time(record)
    ]
    in_service.sort(key=_queue_sort_key)
    return {
        "records": records,
        "waiting_patients": waiting,
        "in_service_patients": in_service,
        "station_available_times": _normalise_station_times(
            snapshot_time, station_available_times, workstation_count
        ),
    }


def project_waiting_starts(
    waiting_patients: list[Patient],
    current_time: datetime,
    station_available_times: list[datetime] | None = None,
    workstation_count: int = DEFAULT_WORKSTATION_COUNT,
) -> dict[str, datetime]:
    projected_starts: dict[str, datetime] = {}
    available_times = _normalise_station_times(
        current_time, station_available_times, workstation_count
    )

    for patient in sorted(waiting_patients, key=_queue_sort_key):
        patient_id = str(patient.patient_id)
        if patient.triage_level == TriageLevel.CRITICAL:
            projected_starts[patient_id] = current_time
            continue

        station_index = min(
            range(len(available_times)), key=lambda index: available_times[index]
        )
        start_time = max(current_time, available_times[station_index])
        projected_starts[patient_id] = start_time
        available_times[station_index] = start_time + timedelta(
            minutes=patient.estimated_treatment_minutes
        )

    return projected_starts


def run_shift_simulation(
    patients: list[Patient],
    slot_interval: int = 20,
    workstation_count: int = DEFAULT_WORKSTATION_COUNT,
) -> dict[str, object]:
    if not patients:
        return {
            "records": [],
            "untreated": [],
            "slot_interval": slot_interval,
            "shift_start": None,
            "shift_end": None,
        }

    shift_end_limit = SHIFT_START + timedelta(hours=8)
    snapshot = build_queue_snapshot(
        patients,
        snapshot_time=shift_end_limit,
        workstation_count=workstation_count,
    )
    records = sorted(
        snapshot["records"],
        key=lambda item: (
            item["treatment_time"],
            item["patient"].triage_level.value,
            item["patient"].arrival_time,
        ),
    )
    shift_end = shift_end_limit
    if records:
        shift_end = max(item["treatment_time"] for item in records)

    return {
        "records": records,
        "untreated": snapshot["waiting_patients"],
        "slot_interval": slot_interval,
        "shift_start": SHIFT_START,
        "shift_end": shift_end,
    }
