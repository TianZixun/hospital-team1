from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

from hospital_team1.models import Patient, TriageLevel


def _default_csv_candidates() -> list[Path]:
    project_root = Path(__file__).resolve().parents[2]
    return [
        project_root / "datasets" / "patients_dataset.csv",
        Path(__file__).resolve().parent.parent / "datasets" / "patients_dataset.csv",
    ]


def load_patients_from_csv(csv_path: Path | None = None) -> list[Patient]:
    if csv_path is None:
        for candidate in _default_csv_candidates():
            if candidate.exists():
                csv_path = candidate
                break
    if csv_path is None:
        raise FileNotFoundError("Could not find patients_dataset.csv in known locations.")

    patients: list[Patient] = []
    with Path(csv_path).open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            patients.append(
                Patient(
                    patient_id=row["patient_id"],
                    name=row["name"],
                    age=int(row["age"]),
                    triage_level=TriageLevel.from_integer(int(row["triage_level"])),
                    arrival_time=datetime.strptime(
                        row["arrival_time"], "%Y-%m-%d %H:%M:%S"
                    ),
                    estimated_treatment_minutes=int(
                        row["estimated_treatment_duration"]
                    ),
                )
            )

    patients.sort(key=lambda patient: patient.arrival_time)
    return patients
