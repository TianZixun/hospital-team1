from __future__ import annotations

from hospital_team1.models_part1 import Patient
from hospital_team1.structures_part1.my_heap import heappush, heappop

from .base import PriorityQueue


class HeapPriorityQueue(PriorityQueue):
    """Array-backed heap queue using the project's self-written heap."""

    def __init__(self) -> None:
        self._heap: list[tuple[int, float, Patient]] = []

    def enqueue(self, patient: Patient) -> None:
        heappush(
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
        _, _, patient = heappop(self._heap)
        return patient

    def peek(self) -> Patient | None:
        if self.is_empty():
            return None
        return self._heap[0][2]

    def get_all_sorted_patients(self) -> list[Patient]:
        """返回按优先级排序的所有患者列表，不修改原队列。

        直接对底层堆数组调用 sorted()，利用 Python 内置的 Timsort
        （C 实现）一次性完成排序，避免了旧实现中的两处额外开销：
        1. 不再需要 self._heap.copy()  —— 消除了 O(n) 显式拷贝
        2. 不再需要 n 次 Python 级 heappop —— 消除了 n 次 _sift_down 调用

        时间复杂度：O(n log n)，但常数因子远小于旧的 copy + n×heappop 方案。
        """
        return [patient for _, _, patient in sorted(self._heap)]

    def get_size(self) -> int:
        return len(self)

    def is_empty(self) -> bool:
        return len(self._heap) == 0

    def __len__(self) -> int:
        return len(self._heap)
