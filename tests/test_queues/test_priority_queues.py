from datetime import datetime
import unittest

from hospital_team1.models_part1 import Patient, TriageLevel
from hospital_team1.queues_part1.heap_priority_queue import HeapPriorityQueue
from hospital_team1.queues_part1.ordered_linked_priority_queue import OrderedLinkedPriorityQueue


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
    """Shared test suite run against both PriorityQueue implementations."""

    queue_class = None

    def build_queue(self):
        assert self.queue_class is not None
        return self.queue_class()

    # ── empty queue ──────────────────────────────────────────────

    def test_empty_queue_is_empty(self) -> None:
        queue = self.build_queue()
        self.assertTrue(queue.is_empty())

    def test_empty_queue_dequeue_returns_none(self) -> None:
        queue = self.build_queue()
        self.assertIsNone(queue.dequeue())

    def test_empty_queue_peek_returns_none(self) -> None:
        queue = self.build_queue()
        self.assertIsNone(queue.peek())

    def test_empty_queue_get_all_sorted_patients_returns_empty_list(self) -> None:
        queue = self.build_queue()
        self.assertEqual(queue.get_all_sorted_patients(), [])

    def test_empty_queue_len_zero(self) -> None:
        queue = self.build_queue()
        self.assertEqual(len(queue), 0)

    def test_empty_queue_get_size_zero(self) -> None:
        queue = self.build_queue()
        self.assertEqual(queue.get_size(), 0)

    # ── single element ───────────────────────────────────────────

    def test_single_element_enqueue_then_dequeue(self) -> None:
        queue = self.build_queue()
        patient = make_patient("1", TriageLevel.URGENT, 10)
        queue.enqueue(patient)

        self.assertFalse(queue.is_empty())
        self.assertEqual(len(queue), 1)
        self.assertEqual(queue.get_size(), 1)
        self.assertEqual(queue.peek().patient_id, "1")

        dequeued = queue.dequeue()
        self.assertEqual(dequeued.patient_id, "1")
        self.assertTrue(queue.is_empty())
        self.assertEqual(len(queue), 0)
        self.assertIsNone(queue.dequeue())
        self.assertIsNone(queue.peek())

    def test_single_element_get_all_sorted_patients(self) -> None:
        queue = self.build_queue()
        patient = make_patient("1", TriageLevel.URGENT, 10)
        queue.enqueue(patient)

        ordered = queue.get_all_sorted_patients()
        self.assertEqual([p.patient_id for p in ordered], ["1"])
        self.assertEqual(queue.get_size(), 1)  # queue unchanged

    # ── same priority, different arrival times (tie-breaking) ────

    def test_same_priority_earlier_arrival_dequeues_first(self) -> None:
        queue = self.build_queue()
        # Both URGENT, "2" arrived earlier → should dequeue before "1"
        queue.enqueue(make_patient("1", TriageLevel.URGENT, 30))
        queue.enqueue(make_patient("2", TriageLevel.URGENT, 10))

        self.assertEqual(queue.peek().patient_id, "2")
        self.assertEqual(queue.dequeue().patient_id, "2")
        self.assertEqual(queue.dequeue().patient_id, "1")

    # ── same priority AND same arrival time ─────────────────────

    def test_same_priority_same_time_both_dequeue(self) -> None:
        queue = self.build_queue()
        p1 = make_patient("A", TriageLevel.SEMI_URGENT, 15)
        p2 = make_patient("B", TriageLevel.SEMI_URGENT, 15)
        queue.enqueue(p1)
        queue.enqueue(p2)

        self.assertEqual(queue.get_size(), 2)
        out1 = queue.dequeue()
        out2 = queue.dequeue()
        self.assertIsNotNone(out1)
        self.assertIsNotNone(out2)
        self.assertIsNone(queue.dequeue())
        # Both must be dequeued without error; order is not specified when
        # triage and arrival_time are identical, but neither should be lost.
        dequeued_ids = {out1.patient_id, out2.patient_id}
        self.assertEqual(dequeued_ids, {"A", "B"})

    # ── mixed priorities (original tests, preserved) ─────────────

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
            [queue.dequeue().patient_id,
             queue.dequeue().patient_id,
             queue.dequeue().patient_id],
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

        self.assertEqual([p.patient_id for p in ordered], ["1", "2", "3"])
        self.assertEqual(queue.get_size(), 3)

    # ── both implementations produce identical order ──────────────

    def test_both_implementations_produce_same_dequeue_order(self) -> None:
        """Explicit cross-check: Heap and OrderedLinked must agree."""
        patients = [
            make_patient("C", TriageLevel.NON_URGENT, 55),
            make_patient("A", TriageLevel.CRITICAL, 10),
            make_patient("B", TriageLevel.URGENT, 30),
            make_patient("E", TriageLevel.SEMI_URGENT, 50),
            make_patient("D", TriageLevel.SEMI_URGENT, 40),
        ]

        # Build results from HeapPriorityQueue (now using self-written heap)
        heap_q = HeapPriorityQueue()
        for p in patients:
            heap_q.enqueue(p)
        heap_order = []
        while not heap_q.is_empty():
            heap_order.append(heap_q.dequeue().patient_id)

        # Build results from OrderedLinkedPriorityQueue
        linked_q = OrderedLinkedPriorityQueue()
        for p in patients:
            linked_q.enqueue(p)
        linked_order = []
        while not linked_q.is_empty():
            linked_order.append(linked_q.dequeue().patient_id)

        self.assertEqual(
            heap_order, linked_order,
            f"Heap: {heap_order}, Linked: {linked_order}",
        )
        # Expected: A(CRITICAL), B(URGENT), D(SEMI_URGENT,40), E(SEMI_URGENT,50), C(NON_URGENT)
        self.assertEqual(heap_order, ["A", "B", "D", "E", "C"])


class TestHeapPriorityQueue(PriorityQueueMixin, unittest.TestCase):
    queue_class = HeapPriorityQueue


class TestOrderedLinkedPriorityQueue(PriorityQueueMixin, unittest.TestCase):
    queue_class = OrderedLinkedPriorityQueue


if __name__ == "__main__":
    unittest.main()
