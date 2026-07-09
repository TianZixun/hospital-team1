from datetime import datetime
from pathlib import Path

from _bootstrap import PROJECT_ROOT  # noqa: F401
from hospital_team1.data.dataset_generator import (
    DatasetConfig,
    export_patients_to_csv,
    generate_patients,
)
from hospital_team1.models import TriageLevel


def main() -> None:
    config = DatasetConfig(
        total_patients=20,
        triage_distribution={
            TriageLevel.CRITICAL: 0.10,
            TriageLevel.URGENT: 0.25,
            TriageLevel.SEMI_URGENT: 0.40,
            TriageLevel.NON_URGENT: 0.25,
        },
        shift_start_time=datetime(2026, 6, 30, 8, 0, 0),
    )
    patients = generate_patients(config)
    output_path = Path(__file__).resolve().parents[1] / "datasets" / "patients_dataset.csv"
    export_patients_to_csv(patients, output_path)
    print(f"Generated {len(patients)} patients at {output_path}")


if __name__ == "__main__":
    main()
