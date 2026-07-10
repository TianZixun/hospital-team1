from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from hospital_team1.analysis_part2.performance import benchmark_priority_queues
from hospital_team1.analysis_part2.timeout_prediction import summarize_timeout_risk
from hospital_team1.analysis_part2.waiting_room_analytics import run_waiting_room_analytics
from hospital_team1.data_part1.csv_loader import load_patients_from_csv
from hospital_team1.models_part1 import Patient, TriageLevel
from hospital_team1.simulation_part2.report import build_shift_report
from hospital_team1.simulation_part2.shift_simulation import (
    DEFAULT_WORKSTATION_COUNT,
    build_queue_snapshot,
    run_shift_simulation,
)
from hospital_team1.structures_part1 import WaitingRoom


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = PROJECT_ROOT / "datasets" / "patients_dataset.csv"
PERFORMANCE_CSV_PATH = PROJECT_ROOT / "results" / "performance_results.csv"
PERFORMANCE_IMAGE_PATH = PROJECT_ROOT / "results" / "performance_comparison.png"
REQUIREMENTS_PATH = PROJECT_ROOT / "require.rtf"

SHIFT_START_TIME = datetime(2026, 6, 30, 8, 0, 0)
BASE_SNAPSHOT_TIME = datetime(2026, 6, 30, 10, 0, 0)
SNAPSHOT_STEP_MINUTES = 20
QUEUE_VIEW_LIMIT = 10
COMPLETED_VIEW_LIMIT = 5

RUNTIME_ADDED_PATIENTS: list[Patient] = []
RUNTIME_COMPLETED_PATIENT_IDS: set[str] = set()
RUNTIME_WAITING_PATIENT_IDS: set[str] = set()

TRIAGE_LABELS = {
    TriageLevel.CRITICAL: "Critical (危急)",
    TriageLevel.URGENT: "Urgent (紧急)",
    TriageLevel.SEMI_URGENT: "Semi-Urgent (次紧急)",
    TriageLevel.NON_URGENT: "Non-Urgent (非紧急)",
}

TRIAGE_TONES = {
    TriageLevel.CRITICAL: "critical",
    TriageLevel.URGENT: "urgent",
    TriageLevel.SEMI_URGENT: "semi",
    TriageLevel.NON_URGENT: "non",
}

TRIAGE_SEQUENCE = (
    TriageLevel.CRITICAL,
    TriageLevel.URGENT,
    TriageLevel.SEMI_URGENT,
    TriageLevel.NON_URGENT,
)

QUEUE_MODE_DETAILS = [
    {
        "key": "heap",
        "name": "Heap Queue (堆队列)",
        "desc": "Uses Python heap storage for priority ordering.",
        "complexity": "Enqueue O(log n), dequeue O(log n), peek O(1).",
    },
    {
        "key": "ordered_list",
        "name": "Ordered Linked Queue (有序链表队列)",
        "desc": "Uses an ordered linked list to keep the queue sorted.",
        "complexity": "Enqueue O(n), dequeue O(1), peek O(1).",
    },
]


def reset_runtime_state() -> None:
    RUNTIME_ADDED_PATIENTS.clear()
    RUNTIME_COMPLETED_PATIENT_IDS.clear()
    RUNTIME_WAITING_PATIENT_IDS.clear()


def _format_wait(value: float) -> str:
    return f"{value:.1f} min"


def _patient_code(patient_id: str | int) -> str:
    try:
        return f"P{int(str(patient_id)):04d}"
    except ValueError:
        return f"P-{patient_id}"


def _queue_priority_key(patient: Patient) -> tuple[int, int, datetime, str]:
    emergency_rank = 0 if patient.triage_level == TriageLevel.CRITICAL else 1
    return (
        emergency_rank,
        patient.triage_level.value,
        patient.arrival_time,
        str(patient.patient_id),
    )


def _normalize_wait_estimates(estimates: dict) -> dict[TriageLevel, float]:
    raw_critical = float(estimates[TriageLevel.CRITICAL]["estimated_wait_minutes"])
    raw_urgent = float(estimates[TriageLevel.URGENT]["estimated_wait_minutes"])
    raw_semi = float(estimates[TriageLevel.SEMI_URGENT]["estimated_wait_minutes"])
    raw_non = float(estimates[TriageLevel.NON_URGENT]["estimated_wait_minutes"])

    critical = max(0.0, min(raw_critical, 10.0))
    urgent = min(45.0, max(critical + 8.0, raw_urgent))
    semi = min(52.0, max(urgent + 5.0, raw_semi))
    non = min(58.0, max(semi + 5.0, raw_non))

    return {
        TriageLevel.CRITICAL: critical,
        TriageLevel.URGENT: urgent,
        TriageLevel.SEMI_URGENT: semi,
        TriageLevel.NON_URGENT: non,
    }


def _record_end_time(record: dict[str, object]) -> datetime:
    patient = record["patient"]
    return record["treatment_time"] + timedelta(
        minutes=patient.estimated_treatment_minutes
    )


def _build_waiting_room(patients: list[Patient]) -> WaitingRoom:
    waiting_room = WaitingRoom()
    for patient in patients:
        waiting_room.add_patient(patient)
    return waiting_room


def _load_visible_patients() -> list[Patient]:
    all_patients = load_patients_from_csv(DATASET_PATH) + list(RUNTIME_ADDED_PATIENTS)
    visible_patients = [
        patient
        for patient in all_patients
        if str(patient.patient_id) not in RUNTIME_COMPLETED_PATIENT_IDS
    ]
    visible_patients.sort(key=lambda patient: patient.arrival_time)
    return visible_patients


def _next_patient_number(patients: list[Patient]) -> int:
    existing_numbers: list[int] = []
    for patient in patients:
        try:
            existing_numbers.append(int(str(patient.patient_id)))
        except ValueError:
            continue
    return max(existing_numbers, default=0) + 1


def _pick_new_patient_template(
    base_patients: list[Patient],
    current_time: datetime,
) -> Patient:
    arrived_patients = [
        patient for patient in base_patients if patient.arrival_time <= current_time
    ]
    normal_pool = [
        patient
        for patient in arrived_patients
        if patient.triage_level != TriageLevel.CRITICAL
    ]

    if normal_pool:
        sample_pool = sorted(normal_pool, key=_queue_priority_key)
    elif arrived_patients:
        sample_pool = sorted(arrived_patients, key=_queue_priority_key)
    else:
        sample_pool = sorted(base_patients, key=_queue_priority_key)

    if not sample_pool:
        raise ValueError("No patient template can be read from the CSV file.")

    return sample_pool[len(RUNTIME_ADDED_PATIENTS) % len(sample_pool)]


def _resolve_snapshot_time(offset_minutes: int) -> datetime:
    return BASE_SNAPSHOT_TIME + timedelta(minutes=max(0, offset_minutes))


def _real_now() -> datetime:
    return datetime.now().astimezone().replace(microsecond=0)


def _max_snapshot_offset(patients: list[Patient]) -> int:
    if not patients:
        return 0

    latest_arrival = max(patient.arrival_time for patient in patients)
    total_minutes = max(
        0,
        int((latest_arrival - BASE_SNAPSHOT_TIME).total_seconds() // 60),
    )
    rounded_minutes = (
        (total_minutes + SNAPSHOT_STEP_MINUTES - 1) // SNAPSHOT_STEP_MINUTES
    ) * SNAPSHOT_STEP_MINUTES
    return max(rounded_minutes, SNAPSHOT_STEP_MINUTES * 3)


def _split_manual_waiting_patients(
    patients: list[Patient],
    current_time: datetime,
) -> tuple[list[Patient], list[Patient]]:
    normal_patients: list[Patient] = []
    forced_waiting_patients: list[Patient] = []

    for patient in patients:
        patient_id = str(patient.patient_id)
        if (
            patient_id in RUNTIME_WAITING_PATIENT_IDS
            and current_time <= patient.arrival_time
        ):
            forced_waiting_patients.append(patient)
            continue

        if patient_id in RUNTIME_WAITING_PATIENT_IDS and current_time > patient.arrival_time:
            RUNTIME_WAITING_PATIENT_IDS.discard(patient_id)
        normal_patients.append(patient)

    return normal_patients, forced_waiting_patients


def _build_snapshot_state(
    patients: list[Patient],
    current_time: datetime,
) -> dict[str, object]:
    normal_patients, forced_waiting_patients = _split_manual_waiting_patients(
        patients,
        current_time,
    )
    snapshot = build_queue_snapshot(
        normal_patients,
        snapshot_time=current_time,
        workstation_count=DEFAULT_WORKSTATION_COUNT,
    )

    waiting_patients = list(snapshot["waiting_patients"]) + list(forced_waiting_patients)
    waiting_patients.sort(key=_queue_priority_key)

    in_service_patients = list(snapshot["in_service_patients"])
    records = list(snapshot["records"])

    record_lookup: dict[str, dict[str, object]] = {}
    completed_rows: list[dict[str, object]] = []
    for record in records:
        patient = record["patient"]
        patient_id = str(patient.patient_id)
        end_time = _record_end_time(record)
        record_lookup[patient_id] = {
            "wait_minutes": float(record["wait_minutes"]),
            "start_time": record["treatment_time"],
            "end_time": end_time,
        }
        if end_time <= current_time:
            completed_rows.append(
                {
                    "patient": patient,
                    "wait_minutes": float(record["wait_minutes"]),
                    "start_time": record["treatment_time"],
                    "end_time": end_time,
                }
            )

    completed_rows.sort(key=lambda row: row["end_time"], reverse=True)
    return {
        "records": records,
        "waiting_patients": waiting_patients,
        "in_service_patients": in_service_patients,
        "completed_rows": completed_rows,
        "record_lookup": record_lookup,
        "station_available_times": snapshot["station_available_times"],
    }


def add_runtime_patient(snapshot_offset_minutes: int = 0) -> dict[str, str]:
    base_patients = load_patients_from_csv(DATASET_PATH)
    current_time = _resolve_snapshot_time(snapshot_offset_minutes)
    template = _pick_new_patient_template(base_patients, current_time)
    new_number = _next_patient_number(base_patients + list(RUNTIME_ADDED_PATIENTS))

    new_patient = Patient(
        patient_id=str(new_number),
        name=f"Walk-in {new_number}",
        age=template.age,
        triage_level=template.triage_level,
        arrival_time=current_time,
        estimated_treatment_minutes=template.estimated_treatment_minutes,
    )
    RUNTIME_ADDED_PATIENTS.append(new_patient)
    RUNTIME_WAITING_PATIENT_IDS.add(str(new_patient.patient_id))

    return {
        "patient_id": _patient_code(new_patient.patient_id),
        "name": new_patient.name,
        "priority": TRIAGE_LABELS[new_patient.triage_level],
    }


def complete_runtime_patient(
    patient_id: str,
    snapshot_offset_minutes: int = 0,
) -> dict[str, str | bool]:
    patients = _load_visible_patients()
    current_time = _resolve_snapshot_time(snapshot_offset_minutes)
    snapshot_state = _build_snapshot_state(patients, current_time)
    completed_rows = snapshot_state["completed_rows"]

    target_row = next(
        (
            row
            for row in completed_rows
            if str(row["patient"].patient_id) == str(patient_id)
        ),
        None,
    )
    if target_row is None:
        return {
            "ok": False,
            "message": "Only completed patients can be removed from the board.",
        }

    patient = target_row["patient"]
    patient_key = str(patient.patient_id)
    RUNTIME_COMPLETED_PATIENT_IDS.add(patient_key)
    RUNTIME_WAITING_PATIENT_IDS.discard(patient_key)
    RUNTIME_ADDED_PATIENTS[:] = [
        item for item in RUNTIME_ADDED_PATIENTS if str(item.patient_id) != patient_key
    ]

    return {
        "ok": True,
        "message": f"{_patient_code(patient.patient_id)} has been removed from completed patients.",
        "patient_id": _patient_code(patient.patient_id),
    }


def _build_queue_display_items(
    visible_patients: list[Patient],
    waiting_patients: list[Patient],
    in_service_patients: list[Patient],
    record_lookup: dict[str, dict[str, object]],
    current_time: datetime,
) -> list[dict[str, object]]:
    active_ids = {
        str(patient.patient_id) for patient in waiting_patients + in_service_patients
    }
    waiting_ids = {str(patient.patient_id) for patient in waiting_patients}
    in_service_ids = {str(patient.patient_id) for patient in in_service_patients}

    upcoming_patients = [
        patient
        for patient in sorted(visible_patients, key=lambda patient: patient.arrival_time)
        if str(patient.patient_id) not in active_ids
        and patient.arrival_time > current_time
    ]

    queue_patients = sorted(
        waiting_patients + in_service_patients,
        key=_queue_priority_key,
    )
    if len(queue_patients) < QUEUE_VIEW_LIMIT:
        queue_patients.extend(
            upcoming_patients[: QUEUE_VIEW_LIMIT - len(queue_patients)]
        )

    queue_items: list[dict[str, object]] = []
    for patient in queue_patients[:QUEUE_VIEW_LIMIT]:
        patient_id = str(patient.patient_id)
        if patient_id in waiting_ids:
            status = "Waiting (候诊中)"
            wait_minutes = max(patient.calculate_wait_minutes(current_time), 0.0)
        elif patient_id in in_service_ids:
            status = "In Service (就诊中)"
            wait_minutes = record_lookup.get(patient_id, {}).get("wait_minutes", 0.0)
        else:
            status = "Scheduled (即将到达)"
            wait_minutes = 0.0

        queue_items.append(
            {
                "raw_id": patient_id,
                "patient_id": _patient_code(patient.patient_id),
                "name": patient.name,
                "priority": TRIAGE_LABELS[patient.triage_level],
                "arrival": patient.arrival_time.strftime("%H:%M"),
                "wait": _format_wait(wait_minutes),
                "status": status,
                "tone": TRIAGE_TONES[patient.triage_level],
                "treatment_minutes": patient.estimated_treatment_minutes,
            }
        )

    return queue_items


def _build_heap_display_items(
    visible_patients: list[Patient],
    waiting_patients: list[Patient],
    in_service_patients: list[Patient],
    record_lookup: dict[str, dict[str, object]],
    current_time: datetime,
    estimated_waits: dict[TriageLevel, float],
) -> list[dict[str, object]]:
    active_ids = {
        str(patient.patient_id) for patient in waiting_patients + in_service_patients
    }
    waiting_ids = {str(patient.patient_id) for patient in waiting_patients}
    in_service_ids = {str(patient.patient_id) for patient in in_service_patients}

    upcoming_patients = [
        patient
        for patient in visible_patients
        if str(patient.patient_id) not in active_ids
        and patient.arrival_time > current_time
    ]

    heap_patients = sorted(
        waiting_patients + in_service_patients + upcoming_patients,
        key=_queue_priority_key,
    )

    heap_items: list[dict[str, object]] = []
    for patient in heap_patients[:QUEUE_VIEW_LIMIT]:
        patient_id = str(patient.patient_id)
        if patient_id in waiting_ids:
            status = "Waiting (候诊中)"
            wait_minutes = max(patient.calculate_wait_minutes(current_time), 0.0)
        elif patient_id in in_service_ids:
            status = "In Service (就诊中)"
            wait_minutes = record_lookup.get(patient_id, {}).get("wait_minutes", 0.0)
        else:
            status = "Scheduled (即将到达)"
            wait_minutes = 0.0

        wait_minutes = estimated_waits.get(patient.triage_level, wait_minutes)

        heap_items.append(
            {
                "raw_id": patient_id,
                "patient_id": _patient_code(patient.patient_id),
                "name": patient.name,
                "priority": TRIAGE_LABELS[patient.triage_level],
                "arrival": patient.arrival_time.strftime("%H:%M"),
                "wait": _format_wait(wait_minutes),
                "status": status,
                "tone": TRIAGE_TONES[patient.triage_level],
                "treatment_minutes": patient.estimated_treatment_minutes,
            }
        )

    return heap_items


def _build_heap_levels(
    heap_items: list[dict[str, object]],
) -> list[list[dict[str, object]]]:
    priority_order = {
        "critical": 0,
        "urgent": 1,
        "semi": 2,
        "non": 3,
    }
    status_order = {
        "In Service (就诊中)": 0,
        "Waiting (候诊中)": 1,
        "Scheduled (即将到达)": 2,
    }

    def heap_sort_key(item: dict[str, object]) -> tuple[int, int, str]:
        return (
            priority_order.get(str(item.get("tone")), 99),
            status_order.get(str(item.get("status")), 99),
            str(item.get("arrival", "")),
        )

    heap_items = sorted(heap_items, key=heap_sort_key)
    levels = [
        heap_items[:1],
        heap_items[1:3],
        heap_items[3:7],
        heap_items[7:10],
    ]
    return [level for level in levels if level]


def _build_completed_items(
    completed_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for row in completed_rows[:COMPLETED_VIEW_LIMIT]:
        patient = row["patient"]
        output.append(
            {
                "raw_id": str(patient.patient_id),
                "patient_id": _patient_code(patient.patient_id),
                "name": patient.name,
                "priority": TRIAGE_LABELS[patient.triage_level],
                "wait": _format_wait(float(row["wait_minutes"])),
                "finished_at": row["end_time"].strftime("%H:%M"),
                "tone": TRIAGE_TONES[patient.triage_level],
            }
        )
    return output


def _build_anomaly_breakdown(
    inversions: list[dict[str, object]],
) -> list[dict[str, str]]:
    high = sum(1 for item in inversions if float(item["wait_gap"]) >= 90)
    medium = sum(1 for item in inversions if 45 <= float(item["wait_gap"]) < 90)
    low = sum(1 for item in inversions if float(item["wait_gap"]) < 45)
    return [
        {"count": str(high), "label": "High Risk (高风险)", "tone": "high"},
        {"count": str(medium), "label": "Medium Risk (中风险)", "tone": "medium"},
        {"count": str(low), "label": "Low Risk (低风险)", "tone": "low"},
    ]


def _load_performance_rows() -> tuple[list[dict[str, str]], dict]:
    performance = benchmark_priority_queues()
    loaded_rows: list[dict[str, str]] = []

    for row in performance.get("rows", []):
        heap_enqueue = row["Heap_Enqueue_ms"]
        heap_dequeue = row["Heap_Dequeue_ms"]
        list_enqueue = row["List_Enqueue_ms"]
        list_dequeue = row["List_Dequeue_ms"]

        heap_total = f"{float(heap_enqueue) + float(heap_dequeue):.4f} ms"
        if list_enqueue == "N/A" or list_dequeue == "N/A":
            second_total = "N/A"
            full_total = "N/A"
        else:
            second_total = f"{float(list_enqueue) + float(list_dequeue):.4f} ms"
            full_total = (
                f"{float(heap_enqueue) + float(heap_dequeue) + float(list_enqueue) + float(list_dequeue):.4f} ms"
            )

        loaded_rows.append(
            {
                "size": row["N"],
                "heap": heap_total,
                "second": second_total,
                "simulation": full_total,
            }
        )

    return loaded_rows, performance


def _weighted_average_wait(wait_groups: dict) -> float:
    total_wait = 0.0
    total_count = 0
    for key, value in wait_groups.items():
        if isinstance(key, TriageLevel):
            total_wait += value["avg_wait"] * value["count"]
            total_count += value["count"]
    return total_wait / max(total_count, 1)


def _threshold_violations(wait_groups: dict) -> int:
    violations = 0
    for key, value in wait_groups.items():
        if isinstance(key, TriageLevel):
            violations += value["violations"]
    return violations


def _estimate_trend(wait_minutes: float) -> str:
    if wait_minutes >= 120:
        return "Escalating (升高)"
    if wait_minutes >= 60:
        return "Moderate (中等)"
    return "Stable (稳定)"


def _build_wait_trend_chart(
    patients: list[Patient],
    snapshot_offset_minutes: int,
    history_points: int = 7,
) -> tuple[list[dict[str, str]], list[str]]:
    end_offset = max(0, snapshot_offset_minutes)
    start_offset = max(0, end_offset - SNAPSHOT_STEP_MINUTES * (history_points - 1))
    offsets = list(
        range(start_offset, end_offset + SNAPSHOT_STEP_MINUTES, SNAPSHOT_STEP_MINUTES)
    )
    if len(offsets) == 1:
        offsets = [0, SNAPSHOT_STEP_MINUTES]

    history = {level: [] for level in TriageLevel}
    labels: list[str] = []

    for offset in offsets:
        snapshot_time = _resolve_snapshot_time(offset)
        snapshot_state = _build_snapshot_state(patients, snapshot_time)
        active_patients = (
            list(snapshot_state["waiting_patients"])
            + list(snapshot_state["in_service_patients"])
        )
        waiting_room = _build_waiting_room(active_patients)
        analytics = run_waiting_room_analytics(
            waiting_room,
            snapshot_time,
            station_available_times=snapshot_state["station_available_times"],
            workstation_count=DEFAULT_WORKSTATION_COUNT,
        )
        estimates = analytics["estimates"]
        labels.append(snapshot_time.strftime("%H:%M"))
        normalized = _normalize_wait_estimates(estimates)
        for level in TRIAGE_SEQUENCE:
            history[level].append(normalized[level])

    width = 320
    height = 120
    x_padding = 14
    y_padding = 14
    usable_width = width - x_padding * 2
    usable_height = height - y_padding * 2
    max_value = max(max(values) for values in history.values()) or 1.0

    def build_points(values: list[float]) -> str:
        if len(values) == 1:
            values = values * 2

        points: list[str] = []
        for index, value in enumerate(values):
            x_pos = x_padding + (usable_width * index / max(len(values) - 1, 1))
            y_pos = y_padding + (usable_height * (1 - value / max_value))
            points.append(f"{x_pos:.1f},{y_pos:.1f}")
        return " ".join(points)

    lines = []
    for level in TRIAGE_SEQUENCE:
        lines.append(
            {
                "label": TRIAGE_LABELS[level],
                "tone": TRIAGE_TONES[level],
                "points": build_points(history[level]),
            }
        )
    return lines, labels


def get_dashboard_context(
    snapshot_offset_minutes: int = 0,
    queue_mode: str = "heap",
) -> dict[str, object]:
    visible_patients = _load_visible_patients()
    current_time = _resolve_snapshot_time(snapshot_offset_minutes)
    real_time = _real_now()
    selected_queue_mode = next(
        (mode for mode in QUEUE_MODE_DETAILS if mode["key"] == queue_mode),
        QUEUE_MODE_DETAILS[0],
    )

    snapshot_state = _build_snapshot_state(visible_patients, current_time)
    waiting_patients = list(snapshot_state["waiting_patients"])
    in_service_patients = list(snapshot_state["in_service_patients"])
    completed_rows = list(snapshot_state["completed_rows"])
    record_lookup = dict(snapshot_state["record_lookup"])

    active_patients = waiting_patients + in_service_patients
    waiting_room = _build_waiting_room(active_patients)

    simulation_result = run_shift_simulation(
        visible_patients,
        slot_interval=20,
        workstation_count=DEFAULT_WORKSTATION_COUNT,
    )
    shift_report = build_shift_report(simulation_result)
    waiting_metrics = run_waiting_room_analytics(
        waiting_room,
        current_time,
        station_available_times=snapshot_state["station_available_times"],
        workstation_count=DEFAULT_WORKSTATION_COUNT,
    )
    timeout_summary = summarize_timeout_risk(current_time, patients=visible_patients)
    performance_rows, performance_artifact = _load_performance_rows()
    wait_trend_lines, wait_trend_labels = _build_wait_trend_chart(
        visible_patients,
        snapshot_offset_minutes=snapshot_offset_minutes,
    )

    average_wait = _weighted_average_wait(waiting_metrics["avg_wait"])
    threshold_violations = _threshold_violations(waiting_metrics["avg_wait"])
    inversions = waiting_metrics["inversions"]
    estimates = waiting_metrics["estimates"]
    normalized_estimates = _normalize_wait_estimates(estimates)

    queue_items = _build_queue_display_items(
        visible_patients,
        waiting_patients,
        in_service_patients,
        record_lookup,
        current_time,
    )
    heap_items = _build_heap_display_items(
        visible_patients,
        waiting_patients,
        in_service_patients,
        record_lookup,
        current_time,
        normalized_estimates,
    )
    heap_levels = _build_heap_levels(heap_items)
    heap_detail = heap_levels[0][0] if heap_levels else None
    completed_items = _build_completed_items(completed_rows)

    predicted_rows = []
    for level in TRIAGE_SEQUENCE:
        estimate_minutes = normalized_estimates[level]
        predicted_rows.append(
            {
                "priority": TRIAGE_LABELS[level],
                "wait": _format_wait(estimate_minutes),
                "trend": _estimate_trend(estimate_minutes),
                "tone": TRIAGE_TONES[level],
            }
        )

    if timeout_summary["risk_percent"] >= 70:
        risk_label = "High (高)"
    elif timeout_summary["risk_percent"] >= 35:
        risk_label = "Medium (中)"
    else:
        risk_label = "Low (低)"

    recent_anomalies = [
        {
            "time": item["higher_priority"].arrival_time.strftime("%H:%M"),
            "message": (
                f"{_patient_code(item['higher_priority'].patient_id)} has waited "
                f"{item['higher_wait']} min, while lower-priority "
                f"{_patient_code(item['lower_priority'].patient_id)} waited "
                f"{item['lower_wait']} min."
            ),
        }
        for item in inversions[:3]
    ]
    if not recent_anomalies:
        recent_anomalies = [
            {
                "time": current_time.strftime("%H:%M"),
                "message": "No priority inversion is detected in the current snapshot.",
            }
        ]

    max_offset_minutes = _max_snapshot_offset(visible_patients)
    next_snapshot_offset = snapshot_offset_minutes + SNAPSHOT_STEP_MINUTES
    if next_snapshot_offset > max_offset_minutes:
        next_snapshot_offset = 0

    runtime_delta = current_time - SHIFT_START_TIME
    runtime_hours, runtime_remainder = divmod(
        int(runtime_delta.total_seconds()),
        3600,
    )
    runtime_minutes = runtime_remainder // 60

    return {
        "app_title": "Hospital Triage Scheduler (医院分诊调度系统)",
        "subtitle": "Simple Flask dashboard with queue logic, simulation, and real CSV data.",
        "current_snapshot_offset": snapshot_offset_minutes,
        "next_snapshot_offset": next_snapshot_offset,
        "max_snapshot_offset": max_offset_minutes,
        "refresh_step_minutes": SNAPSHOT_STEP_MINUTES,
        "summary_cards": [
            {
                "badge": "AQ",
                "title": "Active Queue (当前排队)",
                "value": str(len(active_patients)),
                "delta": f"Top {len(queue_items)} shown in queue view (队列视图最多展示前 10 位).",
                "tone": "neutral",
            },
            {
                "badge": "AW",
                "title": "Average Wait (平均等待)",
                "value": _format_wait(average_wait),
                "delta": f"{threshold_violations} threshold alerts in this snapshot (当前快照 {threshold_violations} 个超时提醒).",
                "tone": "warning",
            },
            {
                "badge": "CP",
                "title": "Compliance (合规率)",
                "value": f"{shift_report['compliance_rate']:.1f}%",
                "delta": f"{shift_report['treated_patients']} treated in the shift simulation (班次仿真处理 {shift_report['treated_patients']} 人).",
                "tone": "positive",
            },
            {
                "badge": "RT",
                "title": "Risk Trend (风险趋势)",
                "value": f"{timeout_summary['risk_percent']}%",
                "delta": f"{len(timeout_summary['at_risk_ids'])} at-risk patients right now (当前 {len(timeout_summary['at_risk_ids'])} 位风险患者).",
                "tone": "high" if timeout_summary["risk_percent"] >= 70 else "warning",
            },
        ],
        "queue_modes": [
            {
                "key": "heap",
                "name": "Heap Queue (堆队列)",
                "desc": "Implemented in hospital_team1/queues/heap_priority_queue.py",
            },
            {
                "key": "ordered_list",
                "name": "Ordered Linked Queue (有序链表队列)",
                "desc": "Implemented in hospital_team1/queues/ordered_linked_priority_queue.py",
            },
        ],
        "selected_queue_mode": selected_queue_mode,
        "queue_mode_note": "Both implementations are expected to return the same patient order. The difference is the internal data structure and performance cost.",
        "control_buttons": [
            {
                "action": "run-simulation",
                "label": "Run Simulation (运行仿真)",
                "tone": "success",
            },
            {
                "action": "add-patient",
                "label": "Add New Patient (新增病人)",
                "tone": "primary",
            },
            {
                "action": "open-dataset",
                "label": "Open Dataset (打开数据集)",
                "tone": "warning",
            },
            {
                "action": "inspect-queue",
                "label": "Inspect Queue (查看队列)",
                "tone": "outline",
            },
            {
                "action": "refresh-snapshot",
                "label": "Refresh Snapshot (刷新快照)",
                "tone": "danger",
            },
        ],
        "system_overview": {
            "clock": current_time.strftime("%H:%M:%S"),
            "snapshot_clock": current_time.strftime("%H:%M:%S"),
            "real_clock": real_time.strftime("%Y-%m-%d %H:%M:%S"),
            "real_clock_iso": real_time.isoformat(),
            "status": "System Online (系统在线)",
            "runtime": f"{runtime_hours:02d}:{runtime_minutes:02d}:00",
            "simulated_patients": str(len(visible_patients)),
            "utilization_label": f"{shift_report['compliance_rate']:.1f}%",
            "utilization_percent": max(
                1,
                min(100, int(round(shift_report["compliance_rate"]))),
            ),
        },
        "dataset_overview": {
            "file_name": DATASET_PATH.name,
            "rows": str(len(visible_patients)),
            "generated_at": datetime.fromtimestamp(DATASET_PATH.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
        },
        "waiting_room_patients": queue_items,
        "heap_levels": heap_levels,
        "heap_detail": heap_detail,
        "recent_completed_patients": completed_items,
        "anomaly_breakdown": _build_anomaly_breakdown(inversions),
        "recent_anomalies": recent_anomalies,
        "predicted_rows": predicted_rows,
        "wait_trend_lines": wait_trend_lines,
        "wait_trend_labels": wait_trend_labels,
        "overtime_card": {
            "risk_percent": timeout_summary["risk_percent"],
            "risk_label": risk_label,
            "details": [
                ("Queue Size (队列人数)", str(len(active_patients))),
                ("At-Risk Patients (风险患者)", str(len(timeout_summary["at_risk_ids"]))),
                (
                    "Top At-Risk IDs (高风险编号)",
                    ", ".join(
                        _patient_code(patient_id)
                        for patient_id in timeout_summary["at_risk_ids"][:4]
                    )
                    or "None",
                ),
            ],
        },
        "workstation_cards": [
            {
                "title": "Station A (诊室 A)",
                "status": "Always handles the highest-priority patient first (优先处理最高优先级患者).",
                "detail": f"Current head: {queue_items[0]['patient_id'] if queue_items else 'N/A'}",
            },
            {
                "title": "Station B (诊室 B)",
                "status": "Compares heap queue and ordered linked queue (对比两种队列实现).",
                "detail": f"Benchmark rows loaded: {len(performance_rows)}",
            },
            {
                "title": "Station C (诊室 C)",
                "status": "Tracks risk and anomaly alerts (监控风险与异常).",
                "detail": f"Priority inversions detected: {len(inversions)}",
            },
        ],
        "simulation_summary": {
            "treated_patients": shift_report["treated_patients"],
            "compliance_rate": shift_report["compliance_rate"],
            "max_wait_minutes": shift_report["max_wait_minutes"],
            "at_risk_count": len(timeout_summary["at_risk_ids"]),
            "snapshot_time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        },
        "performance_rows": performance_rows,
        "performance_chart_available": PERFORMANCE_IMAGE_PATH.exists(),
        "performance_chart_path": str(PERFORMANCE_IMAGE_PATH),
        "performance_csv_available": PERFORMANCE_CSV_PATH.exists(),
        "performance_source_path": performance_artifact.get(
            "csv_path",
            str(PERFORMANCE_CSV_PATH),
        ),
        "requirements_path": str(REQUIREMENTS_PATH),
    }
