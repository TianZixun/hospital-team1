from hospital_team1.models import Patient

from .base import PriorityQueue


class OrderedLinkedPriorityQueue(PriorityQueue):
    """Second queue implementation placeholder.

    Recommended direction for this repo: maintain an ordered linked list so the
    contrast with the heap structure stays clear.
    """

    def __init__(self) -> None:
        self._size = 0

    def enqueue(self, patient: Patient) -> None:
        raise NotImplementedError(
            "TODO: implement ordered linked-list queue insertion."
        )

    def dequeue(self) -> Patient:
        raise NotImplementedError(
            "TODO: implement ordered linked-list queue removal."
        )

    def peek(self) -> Patient:
        raise NotImplementedError(
            "TODO: implement ordered linked-list queue front lookup."
        )

    def is_empty(self) -> bool:
        return self._size == 0

    def __len__(self) -> int:
        return self._size
