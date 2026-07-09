from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from hospital_team1.data.csv_loader import load_patients_from_csv


class TestCsvLoader(unittest.TestCase):
    def test_load_patients_from_csv_sorts_by_arrival_time(self) -> None:
        csv_content = """patient_id,name,age,triage_level,arrival_time,estimated_treatment_duration
2,Bob,40,4,2026-06-30 08:20:00,10
1,Alice,30,2,2026-06-30 08:10:00,25
"""
        with TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "patients.csv"
            csv_path.write_text(csv_content, encoding="utf-8")

            patients = load_patients_from_csv(csv_path)

        self.assertEqual([patient.patient_id for patient in patients], ["1", "2"])
        self.assertEqual(patients[0].arrival_time, datetime(2026, 6, 30, 8, 10, 0))


if __name__ == "__main__":
    unittest.main()
