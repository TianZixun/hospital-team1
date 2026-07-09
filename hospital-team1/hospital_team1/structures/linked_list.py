from __future__ import annotations

from dataclasses import dataclass

from hospital_team1.models import Patient


@dataclass
class PatientNode:
    patient: Patient
    next_node: "PatientNode | None" = None
