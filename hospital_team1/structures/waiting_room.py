from __future__ import annotations

from typing import Iterator

from hospital_team1.models import Patient

from .linked_list import PatientNode


class WaitingRoom:
    """Linked-list-backed waiting-room container."""

    def __init__(self) -> None:
        self.head: PatientNode | None = None
        self.tail: PatientNode | None = None
        self._size = 0

    def add_patient(self, patient: Patient) -> None:
        node = PatientNode(patient=patient)
        if self.head is None:
            self.head = node
            self.tail = node
        else:
            assert self.tail is not None
            self.tail.next_node = node
            self.tail = node
        self._size += 1

    def remove_patient(self, patient_id: str) -> Patient | None:
        previous: PatientNode | None = None
        current = self.head
        while current is not None:
            if str(current.patient.patient_id) == str(patient_id):
                if previous is None:
                    self.head = current.next_node
                else:
                    previous.next_node = current.next_node
                if current is self.tail:
                    self.tail = previous
                self._size -= 1
                return current.patient
            previous = current
            current = current.next_node
        return None

    def find_patient(self, patient_id: str) -> Patient | None:
        for patient in self.iter_patients():
            if str(patient.patient_id) == str(patient_id):
                return patient
        return None

    def iter_patients(self) -> Iterator[Patient]:
        current = self.head
        while current is not None:
            yield current.patient
            current = current.next_node

    def to_list(self) -> list[Patient]:
        return list(self.iter_patients())

    def get_all_waiting_patients(self) -> list[Patient]:
        return self.to_list()

    def find_patient_by_id(self, patient_id: str | int) -> Patient | None:
        return self.find_patient(str(patient_id))

    def remove_patient_by_id(self, patient_id: str | int) -> Patient | None:
        return self.remove_patient(str(patient_id))

    def get_size(self) -> int:
        return self._size

    def is_empty(self) -> bool:
        return self._size == 0

    def __len__(self) -> int:
        return self._size
