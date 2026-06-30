from __future__ import annotations

from abc import ABC, abstractmethod

from hospital_team1.models import Patient


class PriorityQueue(ABC):
    @abstractmethod
    def enqueue(self, patient: Patient) -> None:
        """Insert a patient into the queue."""

    @abstractmethod
    def dequeue(self) -> Patient:
        """Remove and return the highest-priority patient."""

    @abstractmethod
    def peek(self) -> Patient:
        """Return the highest-priority patient without removing it."""

    @abstractmethod
    def is_empty(self) -> bool:
        """Return whether the queue is empty."""

    @abstractmethod
    def __len__(self) -> int:
        """Return the number of queued patients."""
