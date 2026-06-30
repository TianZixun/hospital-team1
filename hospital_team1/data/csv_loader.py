from pathlib import Path

from hospital_team1.models import Patient


def load_patients_from_csv(csv_path: Path) -> list[Patient]:
    raise NotImplementedError("TODO: parse patients_dataset.csv into Patient objects.")
