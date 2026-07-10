from datetime import datetime
import unittest

from hospital_team1.models_part1 import Patient, TriageLevel
from hospital_team1.visualization_part2.cli_views import render_waiting_room_table


class TestCliViews(unittest.TestCase):
    def test_render_waiting_room_table_outputs_patient_rows(self) -> None:
        patient = Patient(
            patient_id="P001",
            name="Alice",
            age=30,
            triage_level=TriageLevel.URGENT,
            arrival_time=datetime(2026, 6, 30, 8, 0, 0),
            estimated_treatment_minutes=25,
        )

        rendered = render_waiting_room_table([patient])

        self.assertIn("patient_id | name | triage | arrival_time | est_minutes", rendered)
        self.assertIn("P001 | Alice | URGENT | 08:00 | 25", rendered)


if __name__ == "__main__":
    unittest.main()
