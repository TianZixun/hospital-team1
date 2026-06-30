from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from hospital_team1.models import Patient, TriageLevel


@dataclass
class DatasetConfig:
    total_patients: int
    triage_distribution: dict[TriageLevel, float]
    shift_start_time: datetime


def generate_patients(config: DatasetConfig) -> list[Patient]:
    raise NotImplementedError("TODO: generate at least 20 patients for CSV export.")


def export_patients_to_csv(patients: list[Patient], output_path: Path) -> None:
    raise NotImplementedError("TODO: export generated patients to CSV.")
