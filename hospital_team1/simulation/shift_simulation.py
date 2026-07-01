from __future__ import annotations

from datetime import datetime, timedelta

from hospital_team1.models import Patient


def run_shift_simulation(
    patients: list[Patient], slot_interval: int = 20
) -> dict[str, object]:
    if not patients:
        return {
            "records": [],
            "untreated": [],
            "slot_interval": slot_interval,
            "shift_start": None,
            "shift_end": None,
        }

    queue: list[Patient] = []
    records: list[dict[str, object]] = []
    patients = sorted(patients, key=lambda patient: patient.arrival_time)

    shift_start = datetime(2026, 6, 30, 8, 0, 0)
    shift_end_limit = shift_start + timedelta(hours=8)
    current_time = max(shift_start, patients[0].arrival_time)
    patient_index = 0

    while current_time <= shift_end_limit and len(records) < len(patients):
        while (
            patient_index < len(patients)
            and patients[patient_index].arrival_time <= current_time
        ):
            queue.append(patients[patient_index])
            patient_index += 1

        queue.sort()
        if queue:
            treated = queue.pop(0)
            wait_minutes = max(treated.calculate_wait_minutes(current_time), 0.0)
            max_allowed = treated.get_max_allowed_wait()
            records.append(
                {
                    "patient": treated,
                    "treatment_time": current_time,
                    "wait_minutes": round(wait_minutes, 1),
                    "max_allowed": max_allowed,
                    "within_threshold": wait_minutes <= max_allowed,
                }
            )

        current_time += timedelta(minutes=slot_interval)

    untreated = queue + patients[patient_index:]
    return {
        "records": records,
        "untreated": untreated,
        "slot_interval": slot_interval,
        "shift_start": shift_start,
        "shift_end": current_time,
    }
