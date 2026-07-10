from __future__ import annotations

from abc import ABC, abstractmethod

from hospital_team1.models_part1 import Patient


class PriorityQueue(ABC):
    @abstractmethod
    def enqueue(self, patient: Patient) -> None:
        """Insert a patient into the queue."""

    @abstractmethod
    def dequeue(self) -> Patient | None:
        """Remove and return the highest-priority patient, or None if empty."""

    @abstractmethod
    def peek(self) -> Patient | None:
        """Return the highest-priority patient without removing it, or None if empty."""

    @abstractmethod
    def is_empty(self) -> bool:
        """Return whether the queue is empty."""

    @abstractmethod
    def __len__(self) -> int:
        """Return the number of queued patients."""

    def get_size(self) -> int:
        """Return the number of queued patients (convenience alias for len)."""
        return len(self)

    @abstractmethod
    def get_all_sorted_patients(self) -> list[Patient]:
        """Return all patients in priority order without modifying the queue."""
