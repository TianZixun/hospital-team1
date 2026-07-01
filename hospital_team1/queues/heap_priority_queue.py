from __future__ import annotations

import heapq

from hospital_team1.models import Patient

from .base import PriorityQueue


class HeapPriorityQueue(PriorityQueue):
    """Array-backed heap queue for assignment part 1 task 2A."""

    def __init__(self) -> None:
        self._heap: list[tuple[int, float, Patient]] = []

    def enqueue(self, patient: Patient) -> None:
        heapq.heappush(
            self._heap,
            (
                patient.triage_level.value,
                patient.arrival_time.timestamp(),
                patient,
            ),
        )

    def dequeue(self) -> Patient | None:
        if self.is_empty():
            return None
        _, _, patient = heapq.heappop(self._heap)
        return patient

    def peek(self) -> Patient | None:
        if self.is_empty():
            return None
        return self._heap[0][2]

    def get_all_sorted_patients(self) -> list[Patient]:
        temp_heap = self._heap.copy()
        sorted_patients: list[Patient] = []
        while temp_heap:
            _, _, patient = heapq.heappop(temp_heap)
            sorted_patients.append(patient)
        return sorted_patients

    def get_size(self) -> int:
        return len(self)

    def is_empty(self) -> bool:
        return len(self._heap) == 0

    def __len__(self) -> int:
        return len(self._heap)
