from __future__ import annotations

from pathlib import Path

from .performance_analysis import (
    load_results_from_csv,
    plot_results,
    run_performance_analysis,
    save_results_to_csv,
)


def benchmark_priority_queues() -> dict:
    project_root = Path(__file__).resolve().parents[2]
    csv_path = project_root / "performance_results.csv"
    png_path = project_root / "performance_comparison.png"

    if csv_path.exists():
        return {
            "rows": load_results_from_csv(csv_path),
            "csv_path": str(csv_path),
            "image_path": str(png_path),
        }

    results = run_performance_analysis()
    save_results_to_csv(results, csv_path)
    plot_results(results, png_path)
    return {
        "raw": results,
        "rows": load_results_from_csv(csv_path),
        "csv_path": str(csv_path),
        "image_path": str(png_path),
    }
