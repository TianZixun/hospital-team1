from hospital_team1.models import Patient

from .base import PriorityQueue


class HeapPriorityQueue(PriorityQueue):
    """Array-backed heap queue for assignment part 1 task 2A."""

    def __init__(self) -> None:
        self._heap: list[Patient] = []

    def enqueue(self, patient: Patient) -> None:
        raise NotImplementedError("TODO: implement manual heap insert logic.")

    def dequeue(self) -> Patient:
        raise NotImplementedError("TODO: implement manual heap pop logic.")

    def peek(self) -> Patient:
        raise NotImplementedError("TODO: implement heap front lookup.")

    def is_empty(self) -> bool:
        return len(self._heap) == 0

    def __len__(self) -> int:
        return len(self._heap)
