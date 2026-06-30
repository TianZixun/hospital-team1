from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class SimulationConfig:
    workstation_open_interval_minutes: int
    shift_start_time: datetime


class SimulationEngine:
    """Duty-shift simulation placeholder."""

    def __init__(self, config: SimulationConfig) -> None:
        self.config = config

    def run(self) -> dict:
        raise NotImplementedError("TODO: implement shift simulation workflow.")
