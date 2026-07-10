from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
import csv
import random

from hospital_team1.models_part1 import Patient, TriageLevel


@dataclass
class DatasetConfig:
    total_patients: int
    triage_distribution: dict[TriageLevel, float]
    shift_start_time: datetime
    shift_duration_hours: float = 8.0
    seed: int = 42


FIRST_NAMES = [
    "Tom",
    "Jack",
    "Bill",
    "Emma",
    "Lucy",
    "Anna",
    "Mike",
    "Rose",
    "John",
    "Sara",
    "Mark",
    "Lily",
    "Paul",
    "Kate",
    "Nick",
    "Jane",
    "Eric",
    "Mia",
    "Ryan",
    "Ella",
    "Alex",
    "Zoe",
    "Adam",
    "Ruth",
    "Ben",
    "Tina",
    "Sam",
    "Leah",
    "Ivy",
    "Owen",
]

LAST_NAMES = [
    "Smith",
    "Brown",
    "Lee",
    "Clark",
    "White",
    "Hall",
    "King",
    "Green",
    "Baker",
    "Adams",
    "Hill",
    "Scott",
    "Young",
    "Moore",
    "Wood",
    "Ross",
    "Ward",
    "Bell",
    "Ford",
    "Cole",
]


def _random_name() -> str:
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"


def _random_age() -> int:
    pick = random.random()
    if pick < 0.05:
        return random.randint(0, 5)
    if pick < 0.12:
        return random.randint(6, 17)
    if pick < 0.45:
        return random.randint(18, 45)
    if pick < 0.75:
        return random.randint(46, 65)
    return random.randint(66, 90)


def _random_treatment_minutes(level: TriageLevel) -> int:
    ranges = {
        TriageLevel.CRITICAL: (60, 120),
        TriageLevel.URGENT: (30, 60),
        TriageLevel.SEMI_URGENT: (15, 30),
        TriageLevel.NON_URGENT: (5, 15),
    }
    low, high = ranges[level]
    return random.randint(low, high)


def generate_patients(config: DatasetConfig) -> list[Patient]:
    if config.total_patients < 20:
        raise ValueError("Assignment dataset should contain at least 20 patients.")

    random.seed(config.seed)
    if abs(sum(config.triage_distribution.values()) - 1.0) > 0.01:
        raise ValueError("Triage distribution must add up to 1.0.")

    counts: dict[TriageLevel, int] = {}
    assigned = 0
    levels = list(TriageLevel)
    for level in levels:
        count = int(config.total_patients * config.triage_distribution.get(level, 0.0))
        counts[level] = count
        assigned += count
    counts[TriageLevel.SEMI_URGENT] += config.total_patients - assigned

    temp_rows: list[dict[str, object]] = []
    for level in levels:
        for _ in range(counts[level]):
            arrival_offset = random.uniform(0, config.shift_duration_hours * 3600)
            temp_rows.append(
                {
                    "name": _random_name(),
                    "age": _random_age(),
                    "triage_level": level,
                    "arrival_time": config.shift_start_time
                    + timedelta(seconds=arrival_offset),
                    "estimated_treatment_minutes": _random_treatment_minutes(level),
                }
            )

    temp_rows.sort(key=lambda row: row["arrival_time"])
    patients: list[Patient] = []
    for index, row in enumerate(temp_rows, start=1):
        patients.append(
            Patient(
                patient_id=str(index),
                name=str(row["name"]),
                age=int(row["age"]),
                triage_level=row["triage_level"],  # type: ignore[arg-type]
                arrival_time=row["arrival_time"],  # type: ignore[arg-type]
                estimated_treatment_minutes=int(row["estimated_treatment_minutes"]),
            )
        )
    return patients


def export_patients_to_csv(patients: list[Patient], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "patient_id",
                "name",
                "age",
                "triage_level",
                "arrival_time",
                "estimated_treatment_duration",
            ],
        )
        writer.writeheader()
        for patient in patients:
            writer.writerow(
                {
                    "patient_id": patient.patient_id,
                    "name": patient.name,
                    "age": patient.age,
                    "triage_level": patient.triage_level.value,
                    "arrival_time": patient.arrival_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "estimated_treatment_duration": patient.estimated_treatment_minutes,
                }
            )
