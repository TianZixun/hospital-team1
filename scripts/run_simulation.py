from datetime import datetime

from hospital_team1.simulation.engine import SimulationConfig, SimulationEngine
from hospital_team1.simulation.report import build_shift_report


def main() -> None:
    config = SimulationConfig(
        workstation_open_interval_minutes=20,
        shift_start_time=datetime(2026, 6, 30, 8, 0, 0),
    )
    engine = SimulationEngine(config)
    result = engine.run()
    summary = build_shift_report(result)
    print("Simulation summary:")
    for key, value in summary.items():
        print(f"- {key}: {value}")


if __name__ == "__main__":
    main()
