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


def line(title: str = "") -> None:
    if title:
        print(f"\n{'-' * 60}")
        print(f"  {title}")
        print(f"{'-' * 60}")
    else:
        print("-" * 60)


def make_demo_people() -> tuple[Patient, Patient]:
    alice = Patient(
        1,
        "Alice",
        45,
        TriageLevel.CRITICAL,
        datetime(2026, 6, 30, 10, 0, 0),
        30,
    )
    bob = Patient(
        2,
        "Bob",
        60,
        TriageLevel.CRITICAL,
        datetime(2026, 6, 30, 10, 30, 0),
        25,
    )
    return alice, bob


def show_dataset(patients: list[Patient]) -> None:
    distribution = Counter(patient.triage_level.name for patient in patients)

    line("0. Dataset Loaded")
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


def run_waiting_room_demo(patients: list[Patient]) -> None:
    line("Task 1: Patient Model & WaitingRoom (Singly Linked List)")

    alice, bob = make_demo_people()

    print("\n  [1a] Patient Tiebreaker (__lt__)")
    print("      Alice : CRITICAL, arrived 10:00")
    print("      Bob   : CRITICAL, arrived 10:30")
    print(f"      Alice < Bob ?  {alice < bob}  (expected: True)")
    print("      --> Same triage, earlier arrival = higher priority")
    assert alice < bob, "Tiebreaker failed"

    print("\n  [1b] WaitingRoom - Singly Linked List Operations")
    waiting_room = WaitingRoom()
    for patient in patients:
        waiting_room.add_patient(patient)

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
    for patient in waiting_patients[:8]:
        print(
            f"      {patient.patient_id:<5} {patient.name:<12} "
            f"{TRIAGE_LABELS[patient.triage_level]:<16} "
            f"{patient.arrival_time.strftime('%H:%M'):<8} {patient.age:<5}"
        )
    if len(waiting_patients) > 8:
        print(f"      ... and {len(waiting_patients) - 8} more")


def run_priority_queue_demo(patients: list[Patient]) -> None:
    line("Task 2: Priority Queue Implementations")

    heap_queue = HeapPriorityQueue()
    linked_queue = SortedLinkedListPriorityQueue()
    for patient in patients:
        heap_queue.enqueue(patient)
        linked_queue.enqueue(patient)

    assert heap_queue.get_size() == len(patients)
    assert linked_queue.get_size() == len(patients)
    print(f"\n    Enqueued {len(patients)} patients into both queues.")

    heap_order = heap_queue.get_all_sorted_patients()
    linked_order = linked_queue.get_all_sorted_patients()
    assert len(heap_order) == len(linked_order), "Queue size mismatch"
    for i in range(len(heap_order)):
        assert heap_order[i].patient_id == linked_order[i].patient_id, "Queue order mismatch"
    print("    Heap <--> SortedLinkedList order: IDENTICAL")

    triages = [patient.triage_level.value for patient in heap_order]
    assert triages == sorted(triages), "Dequeue order violation"
    print("    Priority order: CRITICAL --> URGENT --> SEMI_URGENT --> NON_URGENT")

    for level in TriageLevel:
        same_level_patients: list[Patient] = []
        for patient in heap_order:
            if patient.triage_level == level:
                same_level_patients.append(patient)
        for i in range(len(same_level_patients) - 1):
            assert (
                same_level_patients[i].arrival_time
                <= same_level_patients[i + 1].arrival_time
            )
    print("    Tiebreaker (same triage): earlier arrival first")

    print("\n    Full Dequeue Order (HeapPriorityQueue):")
    print(f"    {'#':<4} {'ID':<5} {'Name':<12} {'Triage':<16} {'Arrival':<8}")
    print(f"    {'-' * 3} {'-' * 4} {'-' * 11} {'-' * 15} {'-' * 7}")
    for i, patient in enumerate(heap_order, start=1):
        print(
            f"    {i:<4} {patient.patient_id:<5} {patient.name:<12} "
            f"{TRIAGE_LABELS[patient.triage_level]:<16} "
            f"{patient.arrival_time.strftime('%H:%M'):<8}"
        )

    print("\n  [2e] Peek / Dequeue Consistency")
    demo_queue = HeapPriorityQueue()
    alice, bob = make_demo_people()
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
    while not heap_queue.is_empty():
        heap_queue.dequeue()
    while not linked_queue.is_empty():
        linked_queue.dequeue()

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

    show_dataset(patients)
    run_waiting_room_demo(patients)
    run_priority_queue_demo(patients)

    print("\n" + "=" * 60)
    print("    All Part 1 checks passed.")
    print("    GUI dashboard is still available via: python scripts/launch_gui.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
