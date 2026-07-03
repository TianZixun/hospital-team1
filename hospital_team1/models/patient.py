from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .triage import TriageLevel


@dataclass(order=False)
class Patient:
    patient_id: str | int
    name: str
    age: int
    triage_level: TriageLevel
    arrival_time: datetime
    estimated_treatment_minutes: int

    def __repr__(self) -> str:
        return (
            "Patient("
            f"patient_id={self.patient_id!r}, "
            f"name={self.name!r}, "
            f"age={self.age!r}, "
            f"triage_level={self.triage_level.name}, "
            f"arrival_time={self.arrival_time.isoformat()}, "
            f"estimated_treatment_minutes={self.estimated_treatment_minutes!r}"
            ")"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Patient):
            return NotImplemented
        return (
            self.patient_id,
            self.name,
            self.age,
            self.triage_level,
            self.arrival_time,
            self.estimated_treatment_minutes,
        ) == (
            other.patient_id,
            other.name,
            other.age,
            other.triage_level,
            other.arrival_time,
            other.estimated_treatment_minutes,
        )

    def __lt__(self, other: "Patient") -> bool:
        if not isinstance(other, Patient):
            return NotImplemented
        return (self.triage_level.value, self.arrival_time) < (
            other.triage_level.value,
            other.arrival_time,
        )

    @property
    def estimated_treatment_duration(self) -> int:
        return self.estimated_treatment_minutes

    def calculate_wait_minutes(self, current_time: datetime) -> float:
        delta = current_time - self.arrival_time
        return delta.total_seconds() / 60

    def get_max_allowed_wait(self) -> int:
        limits = {
            TriageLevel.CRITICAL: 0,
            TriageLevel.URGENT: 20,
            TriageLevel.SEMI_URGENT: 35,
            TriageLevel.NON_URGENT: 60,
        }
        return limits[self.triage_level]
