from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from hospital_team1.data_part1.csv_loader import load_patients_from_csv

from .shift_simulation import run_shift_simulation


@dataclass
class SimulationConfig:
    workstation_open_interval_minutes: int
    shift_start_time: datetime


class SimulationEngine:
    """Duty-shift simulation wrapper around the queue-based model."""

    def __init__(self, config: SimulationConfig) -> None:
        self.config = config

    def run(self) -> dict:
        patients = load_patients_from_csv()
        return run_shift_simulation(
            patients, slot_interval=self.config.workstation_open_interval_minutes
        )
