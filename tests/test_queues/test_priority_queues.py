from datetime import datetime
import unittest

from hospital_team1.models import Patient, TriageLevel
from hospital_team1.queues.heap_priority_queue import HeapPriorityQueue
from hospital_team1.queues.ordered_linked_priority_queue import OrderedLinkedPriorityQueue


def make_patient(
    patient_id: str,
    triage_level: TriageLevel,
    minute: int,
) -> Patient:
    return Patient(
        patient_id=patient_id,
        name=f"Patient-{patient_id}",
        age=30,
        triage_level=triage_level,
        arrival_time=datetime(2026, 6, 30, 8, minute, 0),
        estimated_treatment_minutes=20,
    )


class PriorityQueueMixin:
    queue_class = None

    def build_queue(self):
        assert self.queue_class is not None
        return self.queue_class()

    def test_enqueue_peek_and_dequeue_order(self) -> None:
        queue = self.build_queue()
        patients = [
            make_patient("3", TriageLevel.NON_URGENT, 30),
            make_patient("1", TriageLevel.URGENT, 10),
            make_patient("2", TriageLevel.URGENT, 20),
        ]
        for patient in patients:
            queue.enqueue(patient)

        self.assertEqual(queue.peek().patient_id, "1")
        self.assertEqual(queue.get_size(), 3)
        self.assertFalse(queue.is_empty())
        self.assertEqual(
            [queue.dequeue().patient_id, queue.dequeue().patient_id, queue.dequeue().patient_id],
            ["1", "2", "3"],
        )
        self.assertTrue(queue.is_empty())

    def test_get_all_sorted_patients_preserves_priority_order(self) -> None:
        queue = self.build_queue()
        patients = [
            make_patient("2", TriageLevel.SEMI_URGENT, 25),
            make_patient("1", TriageLevel.CRITICAL, 15),
            make_patient("3", TriageLevel.NON_URGENT, 35),
        ]
        for patient in patients:
            queue.enqueue(patient)

        ordered = queue.get_all_sorted_patients()

        self.assertEqual([patient.patient_id for patient in ordered], ["1", "2", "3"])
        self.assertEqual(queue.get_size(), 3)


class TestHeapPriorityQueue(PriorityQueueMixin, unittest.TestCase):
    queue_class = HeapPriorityQueue


class TestOrderedLinkedPriorityQueue(PriorityQueueMixin, unittest.TestCase):
    queue_class = OrderedLinkedPriorityQueue


if __name__ == "__main__":
    unittest.main()
