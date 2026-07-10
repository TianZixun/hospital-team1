from __future__ import annotations

import csv
import random
import time
from datetime import datetime, timedelta
from pathlib import Path

from hospital_team1.models_part1 import Patient, TriageLevel
from hospital_team1.queues_part1 import HeapPriorityQueue, OrderedLinkedPriorityQueue


def generate_patients(n: int, seed: int = 42) -> list[Patient]:
    random.seed(seed)
    triage_counts = {
        TriageLevel.CRITICAL: int(n * 0.10),
        TriageLevel.URGENT: int(n * 0.25),
        TriageLevel.SEMI_URGENT: int(n * 0.40),
    }
    triage_counts[TriageLevel.NON_URGENT] = (
        n
        - triage_counts[TriageLevel.CRITICAL]
        - triage_counts[TriageLevel.URGENT]
        - triage_counts[TriageLevel.SEMI_URGENT]
    )

    names = [
        "Tom",
        "Bill",
        "Mike",
        "John",
        "David",
        "Chris",
        "Steve",
        "Mark",
        "Paul",
        "James",
        "Ruth",
        "Mary",
        "Lisa",
        "Anna",
        "Emma",
        "Jane",
    ]
    arrival_start = datetime(2026, 6, 30, 8, 0, 0)

    temp_rows: list[tuple[TriageLevel, datetime]] = []
    for level, count in triage_counts.items():
        for _ in range(count):
            arrival = arrival_start + timedelta(minutes=random.uniform(0, 480))
            temp_rows.append((level, arrival))

    temp_rows.sort(key=lambda row: row[1])
    patients: list[Patient] = []
    for index, (level, arrival) in enumerate(temp_rows, start=1):
        patients.append(
            Patient(
                patient_id=str(index),
                name=random.choice(names),
                age=random.randint(1, 90),
                triage_level=level,
                arrival_time=arrival,
                estimated_treatment_minutes=random.randint(5, 120),
            )
        )
    return patients


def benchmark_enqueue(
    queue_cls: type[HeapPriorityQueue] | type[OrderedLinkedPriorityQueue],
    patients: list[Patient],
    iterations: int = 5,
) -> float:
    total_time = 0.0
    for _ in range(iterations):
        queue = queue_cls()
        start = time.perf_counter()
        for patient in patients:
            queue.enqueue(patient)
        total_time += time.perf_counter() - start
    return total_time / iterations


def benchmark_dequeue(
    queue_cls: type[HeapPriorityQueue] | type[OrderedLinkedPriorityQueue],
    patients: list[Patient],
    iterations: int = 5,
) -> float:
    total_time = 0.0
    for _ in range(iterations):
        queue = queue_cls()
        for patient in patients:
            queue.enqueue(patient)
        start = time.perf_counter()
        while not queue.is_empty():
            queue.dequeue()
        total_time += time.perf_counter() - start
    return total_time / iterations


def run_performance_analysis() -> dict[str, dict[str, list[tuple[int, float]]]]:
    n_values = [10, 100, 500, 1000, 5000]
    results = {
        "heap": {"enqueue": [], "dequeue": []},
        "ordered_list": {"enqueue": [], "dequeue": []},
    }

    for n in n_values:
        patients = generate_patients(n)
        heap_enqueue = benchmark_enqueue(HeapPriorityQueue, patients)
        heap_dequeue = benchmark_dequeue(HeapPriorityQueue, patients)
        results["heap"]["enqueue"].append((n, heap_enqueue))
        results["heap"]["dequeue"].append((n, heap_dequeue))

        if n <= 1000:
            list_enqueue = benchmark_enqueue(OrderedLinkedPriorityQueue, patients)
            list_dequeue = benchmark_dequeue(OrderedLinkedPriorityQueue, patients)
            results["ordered_list"]["enqueue"].append((n, list_enqueue))
            results["ordered_list"]["dequeue"].append((n, list_dequeue))

    return results


def save_results_to_csv(
    results: dict[str, dict[str, list[tuple[int, float]]]],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "N",
                "Heap_Enqueue_ms",
                "Heap_Dequeue_ms",
                "List_Enqueue_ms",
                "List_Dequeue_ms",
            ]
        )
        for index, (n, heap_enqueue) in enumerate(results["heap"]["enqueue"]):
            heap_dequeue = results["heap"]["dequeue"][index][1]
            if index < len(results["ordered_list"]["enqueue"]):
                list_enqueue = results["ordered_list"]["enqueue"][index][1]
                list_dequeue = results["ordered_list"]["dequeue"][index][1]
            else:
                list_enqueue = None
                list_dequeue = None
            writer.writerow(
                [
                    n,
                    f"{heap_enqueue * 1000:.4f}",
                    f"{heap_dequeue * 1000:.4f}",
                    f"{list_enqueue * 1000:.4f}" if list_enqueue is not None else "N/A",
                    f"{list_dequeue * 1000:.4f}" if list_dequeue is not None else "N/A",
                ]
            )


def load_results_from_csv(csv_path: Path) -> list[dict[str, str]]:
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def plot_results(
    results: dict[str, dict[str, list[tuple[int, float]]]],
    output_path: Path,
) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return

    figure, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    heap_n = [row[0] for row in results["heap"]["enqueue"]]
    heap_enqueue = [row[1] * 1000 for row in results["heap"]["enqueue"]]
    heap_dequeue = [row[1] * 1000 for row in results["heap"]["dequeue"]]
    list_n = [row[0] for row in results["ordered_list"]["enqueue"]]
    list_enqueue = [row[1] * 1000 for row in results["ordered_list"]["enqueue"]]
    list_dequeue = [row[1] * 1000 for row in results["ordered_list"]["dequeue"]]

    ax1.plot(heap_n, heap_enqueue, "bo-", label="Heap Queue", linewidth=2)
    ax1.plot(list_n, list_enqueue, "ro-", label="Ordered List Queue", linewidth=2)
    ax1.set_title("Enqueue Performance")
    ax1.set_xlabel("Patients")
    ax1.set_ylabel("Time (ms)")
    ax1.set_xscale("log")
    ax1.set_yscale("log")
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    ax2.plot(heap_n, heap_dequeue, "bo-", label="Heap Queue", linewidth=2)
    ax2.plot(list_n, list_dequeue, "ro-", label="Ordered List Queue", linewidth=2)
    ax2.set_title("Dequeue Performance")
    ax2.set_xlabel("Patients")
    ax2.set_ylabel("Time (ms)")
    ax2.set_xscale("log")
    ax2.set_yscale("log")
    ax2.grid(True, alpha=0.3)
    ax2.legend()

    figure.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, dpi=220, bbox_inches="tight")
