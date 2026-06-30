from datetime import datetime
import unittest

from hospital_team1.models import Patient, TriageLevel
from hospital_team1.structures import WaitingRoom


def make_patient(patient_id: str) -> Patient:
    return Patient(
        patient_id=patient_id,
        name=f"Patient-{patient_id}",
        age=20,
        triage_level=TriageLevel.NON_URGENT,
        arrival_time=datetime(2026, 6, 30, 8, 0),
        estimated_treatment_minutes=15,
    )


class TestWaitingRoom(unittest.TestCase):
    def test_add_and_find_patient(self) -> None:
        waiting_room = WaitingRoom()
        patient = make_patient("P001")

        waiting_room.add_patient(patient)

        self.assertEqual(len(waiting_room), 1)
        self.assertEqual(waiting_room.find_patient("P001"), patient)

    def test_remove_patient(self) -> None:
        waiting_room = WaitingRoom()
        patient = make_patient("P001")
        waiting_room.add_patient(patient)

        removed = waiting_room.remove_patient("P001")

        self.assertEqual(removed, patient)
        self.assertEqual(len(waiting_room), 0)
        self.assertIsNone(waiting_room.find_patient("P001"))


if __name__ == "__main__":
    unittest.main()
