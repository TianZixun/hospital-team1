from __future__ import annotations

from dataclasses import dataclass

from hospital_team1.models_part1 import Patient

from .base import PriorityQueue


@dataclass
class _QueueNode:
    patient: Patient
    next_node: "_QueueNode | None" = None


class OrderedLinkedPriorityQueue(PriorityQueue):
    """Ordered linked-list queue used as the second implementation."""

    def __init__(self) -> None:
        self.head: _QueueNode | None = None
        self._size = 0

    def enqueue(self, patient: Patient) -> None:
        new_node = _QueueNode(patient)
        self._size += 1

        if self.head is None or patient < self.head.patient:
            new_node.next_node = self.head
            self.head = new_node
            return

        current = self.head
        while current.next_node is not None and not (
            patient < current.next_node.patient
        ):
            current = current.next_node
        new_node.next_node = current.next_node
        current.next_node = new_node

    def dequeue(self) -> Patient | None:
        if self.head is None:
            return None
        patient = self.head.patient
        self.head = self.head.next_node
        self._size -= 1
        return patient

    def peek(self) -> Patient | None:
        if self.head is None:
            return None
        return self.head.patient

    def get_all_sorted_patients(self) -> list[Patient]:
        patients: list[Patient] = []
        current = self.head
        while current is not None:
            patients.append(current.patient)
            current = current.next_node
        return patients

    def get_size(self) -> int:
        return len(self)

    def is_empty(self) -> bool:
        return self._size == 0

    def __len__(self) -> int:
        return self._size
