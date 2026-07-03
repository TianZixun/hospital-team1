from pathlib import Path

from _bootstrap import PROJECT_ROOT  # noqa: F401
from hospital_team1.analysis.performance_analysis import (
    plot_results,
    run_performance_analysis,
    save_results_to_csv,
)


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    results = run_performance_analysis()
    save_results_to_csv(results, project_root / "performance_results.csv")
    plot_results(results, project_root / "performance_comparison.png")
    print("Saved performance_results.csv and performance_comparison.png")


if __name__ == "__main__":
    main()
