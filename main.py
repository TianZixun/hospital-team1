from __future__ import annotations

from collections import Counter
from datetime import datetime
from pathlib import Path

from hospital_team1.data.csv_loader import load_patients_from_csv
from hospital_team1.models import Patient, TriageLevel
from hospital_team1.queues.heap_priority_queue import HeapPriorityQueue
from hospital_team1.queues.sorted_linked_list_queue import (
    SortedLinkedListPriorityQueue,
)
from hospital_team1.structures import WaitingRoom


DATASET_PATH = Path(__file__).resolve().parent / "datasets" / "patients_dataset.csv"

TRIAGE_LABELS = {
    TriageLevel.CRITICAL: "CRITICAL    (1)",
    TriageLevel.URGENT: "URGENT      (2)",
    TriageLevel.SEMI_URGENT: "SEMI_URGENT (3)",
    TriageLevel.NON_URGENT: "NON_URGENT  (4)",
}

QueueLike = WaitingRoom | HeapPriorityQueue | SortedLinkedListPriorityQueue


def build_demo_patients() -> tuple[Patient, Patient]:
    return (
        Patient(
            1,
            "Alice",
            45,
            TriageLevel.CRITICAL,
            datetime(2026, 6, 30, 10, 0, 0),
            30,
        ),
        Patient(
            2,
            "Bob",
            60,
            TriageLevel.CRITICAL,
            datetime(2026, 6, 30, 10, 30, 0),
            25,
        ),
    )


def print_separator(title: str = "") -> None:
    if title:
        print(f"\n{'-' * 60}")
        print(f"  {title}")
        print(f"{'-' * 60}")
        return
    print("-" * 60)


def print_dataset_summary(patients: list[Patient]) -> None:
    distribution = Counter(patient.triage_level.name for patient in patients)

    print_separator("0. Dataset Loaded")
    print(f"    Source : {DATASET_PATH.name}")
    print(f"    Total  : {len(patients)} patients")
    print("    Breakdown:")
    print(f"      CRITICAL      : {distribution['CRITICAL']:>2}")
    print(f"      URGENT        : {distribution['URGENT']:>2}")
    print(f"      SEMI_URGENT   : {distribution['SEMI_URGENT']:>2}")
    print(f"      NON_URGENT    : {distribution['NON_URGENT']:>2}")
    print("\n    Sample (first 3 patients):")
    for patient in patients[:3]:
        print(f"      {patient}")


def add_patients_to_queue(queue: QueueLike, patients: list[Patient]) -> None:
    for patient in patients:
        if isinstance(queue, WaitingRoom):
            queue.add_patient(patient)
        else:
            queue.enqueue(patient)


def print_patient_rows(
    patients: list[Patient], limit: int, include_index: bool = False
) -> None:
    for index, patient in enumerate(patients[:limit], start=1):
        prefix = f"    {index:<4} " if include_index else "      "
        print(
            f"{prefix}{patient.patient_id:<5} {patient.name:<12} "
            f"{TRIAGE_LABELS[patient.triage_level]:<16} "
            f"{patient.arrival_time.strftime('%H:%M'):<8}"
            f"{'' if include_index else f' {patient.age:<5}'}"
        )


def drain_queue(queue: QueueLike) -> None:
    while not queue.is_empty():
        queue.dequeue()


def run_waiting_room_demo(patients: list[Patient]) -> None:
    print_separator("Task 1: Patient Model & WaitingRoom (Singly Linked List)")

    alice, bob = build_demo_patients()

    print("\n  [1a] Patient Tiebreaker (__lt__)")
    print("      Alice : CRITICAL, arrived 10:00")
    print("      Bob   : CRITICAL, arrived 10:30")
    print(f"      Alice < Bob ?  {alice < bob}  (expected: True)")
    print("      --> Same triage, earlier arrival = higher priority")
    assert alice < bob, "Tiebreaker failed"

    print("\n  [1b] WaitingRoom - Singly Linked List Operations")
    waiting_room = WaitingRoom()
    add_patients_to_queue(waiting_room, patients)

    print(
        f"      add_patient() x {len(patients)}  -->  size = {waiting_room.get_size()}"
    )

    found = waiting_room.find_patient_by_id(3)
    assert found is not None
    print(
        "      find_patient_by_id(3)   -->  "
        f"found: {found.name} ({found.triage_level.name}, "
        f"arrived {found.arrival_time.strftime('%H:%M')})"
    )

    removed = waiting_room.remove_patient_by_id(5)
    assert removed is not None
    print(
        "      remove_patient_by_id(5) -->  "
        f"removed: {removed.name}, remaining: {waiting_room.get_size()}"
    )

    assert waiting_room.find_patient_by_id(999) is None
    assert waiting_room.remove_patient_by_id(999) is None
    print("      find/remove non-existent ID 999  -->  None (no crash)")

    waiting_patients = waiting_room.get_all_waiting_patients()
    print(f"\n      Current WaitingRoom ({len(waiting_patients)} patients):")
    print(f"      {'ID':<5} {'Name':<12} {'Triage':<16} {'Arrival':<8} {'Age':<5}")
    print(f"      {'-' * 4} {'-' * 11} {'-' * 15} {'-' * 7} {'-' * 4}")
    print_patient_rows(waiting_patients, limit=8)
    if len(waiting_patients) > 8:
        print(f"      ... and {len(waiting_patients) - 8} more")


def run_priority_queue_demo(patients: list[Patient]) -> None:
    print_separator("Task 2: Priority Queue Implementations")

    heap_queue = HeapPriorityQueue()
    linked_queue = SortedLinkedListPriorityQueue()
    add_patients_to_queue(heap_queue, patients)
    add_patients_to_queue(linked_queue, patients)

    assert heap_queue.get_size() == len(patients)
    assert linked_queue.get_size() == len(patients)
    print(f"\n    Enqueued {len(patients)} patients into both queues.")

    heap_order = heap_queue.get_all_sorted_patients()
    linked_order = linked_queue.get_all_sorted_patients()
    assert len(heap_order) == len(linked_order)
    assert all(
        heap_patient.patient_id == linked_patient.patient_id
        for heap_patient, linked_patient in zip(heap_order, linked_order)
    ), "Queue order mismatch"
    print("    Heap <--> SortedLinkedList order: IDENTICAL")

    triages = [patient.triage_level.value for patient in heap_order]
    assert triages == sorted(triages), "Dequeue order violation"
    print("    Priority order: CRITICAL --> URGENT --> SEMI_URGENT --> NON_URGENT")

    for level in TriageLevel:
        same_level_patients = [
            patient for patient in heap_order if patient.triage_level == level
        ]
        for index in range(len(same_level_patients) - 1):
            assert (
                same_level_patients[index].arrival_time
                <= same_level_patients[index + 1].arrival_time
            )
    print("    Tiebreaker (same triage): earlier arrival first")

    print("\n    Full Dequeue Order (HeapPriorityQueue):")
    print(f"    {'#':<4} {'ID':<5} {'Name':<12} {'Triage':<16} {'Arrival':<8}")
    print(f"    {'-' * 3} {'-' * 4} {'-' * 11} {'-' * 15} {'-' * 7}")
    print_patient_rows(heap_order, limit=len(heap_order), include_index=True)

    print("\n  [2e] Peek / Dequeue Consistency")
    demo_queue = HeapPriorityQueue()
    alice, bob = build_demo_patients()
    demo_queue.enqueue(alice)
    demo_queue.enqueue(bob)

    top_patient = demo_queue.peek()
    assert top_patient is not None and top_patient.patient_id == alice.patient_id
    print(f"      Peek    --> #{top_patient.patient_id} {top_patient.name}")

    dequeued_patient = demo_queue.dequeue()
    assert (
        dequeued_patient is not None
        and dequeued_patient.patient_id == alice.patient_id
    )
    print(f"      Dequeue --> #{dequeued_patient.patient_id} {dequeued_patient.name}")
    print(f"      Remaining size: {demo_queue.get_size()}")

    print("\n  [2f] Empty Queue Edge Cases")
    drain_queue(heap_queue)
    drain_queue(linked_queue)

    assert heap_queue.is_empty() and linked_queue.is_empty()
    assert heap_queue.dequeue() is None
    assert heap_queue.peek() is None
    assert linked_queue.dequeue() is None
    assert linked_queue.peek() is None
    print("      Fully drained both queues")
    print("      dequeue() on empty --> None (no crash)")
    print("      peek() on empty    --> None (no crash)")


def main() -> None:
    patients = load_patients_from_csv(DATASET_PATH)

    print("=" * 60)
    print("    HOSPITAL PATIENT TRIAGE SYSTEM")
    print("    Part 1 - Software Toolbox Demo")
    print("=" * 60)

    print_dataset_summary(patients)
    run_waiting_room_demo(patients)
    run_priority_queue_demo(patients)

    print("\n" + "=" * 60)
    print("    All Part 1 checks passed.")
    print("    GUI dashboard is still available via: python scripts/launch_gui.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
