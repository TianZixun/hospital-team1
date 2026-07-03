from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from hospital_team1.data.csv_loader import load_patients_from_csv
from hospital_team1.data.dataset_generator import (
    DatasetConfig,
    export_patients_to_csv,
    generate_patients,
)
from hospital_team1.models import TriageLevel


class TestDatasetGenerator(unittest.TestCase):
    def test_generate_patients_creates_sorted_dataset(self) -> None:
        config = DatasetConfig(
            total_patients=20,
            triage_distribution={
                TriageLevel.CRITICAL: 0.1,
                TriageLevel.URGENT: 0.2,
                TriageLevel.SEMI_URGENT: 0.4,
                TriageLevel.NON_URGENT: 0.3,
            },
            shift_start_time=datetime(2026, 6, 30, 8, 0, 0),
            seed=7,
        )

        patients = generate_patients(config)

        self.assertEqual(len(patients), 20)
        self.assertEqual(patients[0].patient_id, "1")
        self.assertEqual(
            patients,
            sorted(patients, key=lambda patient: patient.arrival_time),
        )

    def test_generate_patients_rejects_invalid_distribution(self) -> None:
        config = DatasetConfig(
            total_patients=20,
            triage_distribution={
                TriageLevel.CRITICAL: 0.2,
                TriageLevel.URGENT: 0.2,
                TriageLevel.SEMI_URGENT: 0.2,
                TriageLevel.NON_URGENT: 0.2,
            },
            shift_start_time=datetime(2026, 6, 30, 8, 0, 0),
        )

        with self.assertRaises(ValueError):
            generate_patients(config)

    def test_export_patients_to_csv_round_trips_with_loader(self) -> None:
        config = DatasetConfig(
            total_patients=20,
            triage_distribution={
                TriageLevel.CRITICAL: 0.1,
                TriageLevel.URGENT: 0.2,
                TriageLevel.SEMI_URGENT: 0.4,
                TriageLevel.NON_URGENT: 0.3,
            },
            shift_start_time=datetime(2026, 6, 30, 8, 0, 0),
            seed=12,
        )
        patients = generate_patients(config)

        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "patients.csv"
            export_patients_to_csv(patients, output_path)
            loaded = load_patients_from_csv(output_path)

        self.assertEqual(len(loaded), len(patients))
        self.assertEqual(loaded[0].patient_id, patients[0].patient_id)


if __name__ == "__main__":
    unittest.main()
