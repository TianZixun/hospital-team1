from __future__ import annotations

from datetime import datetime
from pathlib import Path

from hospital_team1.analysis.performance import benchmark_priority_queues
from hospital_team1.analysis.timeout_prediction import summarize_timeout_risk
from hospital_team1.analysis.waiting_room_analytics import run_waiting_room_analytics
from hospital_team1.data.csv_loader import load_patients_from_csv
from hospital_team1.models import TriageLevel
from hospital_team1.simulation.report import build_shift_report
from hospital_team1.simulation.shift_simulation import run_shift_simulation
from hospital_team1.structures import WaitingRoom


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = PROJECT_ROOT / "datasets" / "patients_dataset.csv"
PERFORMANCE_CSV_PATH = PROJECT_ROOT / "performance_results.csv"
PERFORMANCE_IMAGE_PATH = PROJECT_ROOT / "performance_comparison.png"
REQUIREMENTS_PATH = PROJECT_ROOT / "require.rtf"
SNAPSHOT_TIME = datetime(2026, 6, 30, 10, 0, 0)

TRIAGE_LABELS = {
    TriageLevel.CRITICAL: "Critical (危急)",
    TriageLevel.URGENT: "Urgent (紧急)",
    TriageLevel.SEMI_URGENT: "Semi-Urgent (次紧急)",
    TriageLevel.NON_URGENT: "Non-Urgent (非紧急)",
}

TRIAGE_TONES = {
    TriageLevel.CRITICAL: "high",
    TriageLevel.URGENT: "high",
    TriageLevel.SEMI_URGENT: "medium",
    TriageLevel.NON_URGENT: "low",
}


def _format_wait(value: float) -> str:
    return f"{value:.1f} min"


def _patient_code(patient_id: str | int) -> str:
    try:
        return f"P{int(str(patient_id)):04d}"
    except ValueError:
        return f"P-{patient_id}"


def _build_waiting_room(patients: list) -> WaitingRoom:
    waiting_room = WaitingRoom()
    for patient in patients:
        waiting_room.add_patient(patient)
    return waiting_room


def _build_heap_levels(patients: list) -> list[list[dict[str, str]]]:
    ordered = sorted(patients)[:7]
    levels = [ordered[:1], ordered[1:3], ordered[3:7]]
    built_levels: list[list[dict[str, str]]] = []
    for level in levels:
        built_levels.append(
            [
                {
                    "label": _patient_code(patient.patient_id),
                    "priority": TRIAGE_LABELS[patient.triage_level],
                    "tone": TRIAGE_TONES[patient.triage_level],
                }
                for patient in level
            ]
        )
    return built_levels


def _build_anomaly_breakdown(inversions: list[dict[str, object]]) -> list[dict[str, str]]:
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
    rows = performance.get("rows", [])
    loaded_rows: list[dict[str, str]] = []
    for row in rows:
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


def get_dashboard_context() -> dict:
    patients = load_patients_from_csv(DATASET_PATH)
    current_time = SNAPSHOT_TIME
    active_patients = [patient for patient in patients if patient.arrival_time <= current_time]
    waiting_room = _build_waiting_room(active_patients)

    simulation_result = run_shift_simulation(patients, slot_interval=20)
    shift_report = build_shift_report(simulation_result)
    waiting_metrics = run_waiting_room_analytics(waiting_room, current_time)
    timeout_summary = summarize_timeout_risk(current_time)
    performance_rows, performance_artifact = _load_performance_rows()

    average_wait = _weighted_average_wait(waiting_metrics["avg_wait"])
    threshold_violations = _threshold_violations(waiting_metrics["avg_wait"])
    inversions = waiting_metrics["inversions"]
    estimates = waiting_metrics["estimates"]

    waiting_room_patients = []
    for patient in sorted(active_patients)[:4]:
        waiting_room_patients.append(
            {
                "patient_id": _patient_code(patient.patient_id),
                "name": patient.name,
                "priority": TRIAGE_LABELS[patient.triage_level],
                "arrival": patient.arrival_time.strftime("%H:%M"),
                "wait": _format_wait(max(patient.calculate_wait_minutes(current_time), 0.0)),
                "tone": TRIAGE_TONES[patient.triage_level],
            }
        )

    estimate_rows = []
    for level in TriageLevel:
        estimate = estimates[level]
        estimate_rows.append(
            {
                "priority": TRIAGE_LABELS[level],
                "wait": _format_wait(estimate["estimated_wait_minutes"]),
                "trend": _estimate_trend(estimate["estimated_wait_minutes"]),
                "tone": TRIAGE_TONES[level],
            }
        )

    if timeout_summary["risk_percent"] >= 70:
        top_risk_label = "High (高)"
    elif timeout_summary["risk_percent"] >= 35:
        top_risk_label = "Medium (中)"
    else:
        top_risk_label = "Low (低)"

    queue_modes = [
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
    ]

    content_slots = [
        {
            "title": "Dataset Input (数据集输入)",
            "path": str(DATASET_PATH),
            "hint": "Patient records are loaded from the zip package CSV.",
        },
        {
            "title": "Assignment Brief (作业要求)",
            "path": str(REQUIREMENTS_PATH),
            "hint": "Use this file when you need to add report, slide, or requirement details later.",
        },
        {
            "title": "Waiting Analytics (候诊分析)",
            "path": "hospital_team1/analysis/waiting_room_analytics.py",
            "hint": "Average wait, priority inversion detection, and new-arrival estimates are calculated here.",
        },
        {
            "title": "Timeout Prediction (超时预测)",
            "path": "hospital_team1/analysis/timeout_prediction.py",
            "hint": "The overtime-risk widget is driven by this module.",
        },
        {
            "title": "Performance Results (性能结果)",
            "path": str(PERFORMANCE_CSV_PATH),
            "hint": "The benchmark table and chart read the real output from the zip package.",
        },
    ]

    project_map = [
        ("hospital_team1/", "Core package root (核心代码根目录)"),
        ("models/", "Patient model and triage enum (患者模型与分诊枚举)"),
        ("structures/", "Linked list and waiting room (链表与候诊区)"),
        ("queues/", "Heap queue and second queue implementation (堆队列与第二队列实现)"),
        ("data/", "CSV generation and import (CSV 生成与导入)"),
        ("simulation/", "Scheduling simulation and compliance logic (调度仿真与合规逻辑)"),
        ("analysis/", "Performance and waiting-room analysis (性能与候诊分析)"),
        ("visualization/", "Flask dashboard and views (Flask 看板与视图)"),
        ("utils/", "Shared constants and helpers (共享常量与工具函数)"),
        ("tests/", "Test cases for each module (各模块测试用例)"),
        ("scripts/", "Convenience run scripts (运行脚本)"),
        ("datasets/", "CSV datasets used by the dashboard (看板使用的数据集)"),
        ("docs/", "Written report materials (文档与报告材料)"),
        ("slides/", "Presentation materials (展示与答辩材料)"),
        ("main.py", "Simple local entry point (本地入口程序)"),
        ("test.py", "Quick smoke test script (快速测试脚本)"),
        ("README.md", "Project overview and usage notes (项目说明)"),
        ("pyproject.toml", "Python package and dependency settings (依赖与打包配置)"),
    ]

    runtime_hours = current_time.hour - 8
    runtime_minutes = current_time.minute

    return {
        "app_title": "Hospital Triage Scheduler (医院分诊调度系统)",
        "subtitle": (
            "Real-data Flask dashboard from your zip package, queue logic, simulation, and analysis."
        ),
        "summary_cards": [
            {
                "badge": "AQ",
                "title": "Active Queue (当前排队)",
                "value": str(len(active_patients)),
                "delta": f"Top {len(waiting_room_patients)} shown in queue view (队列视图展示前 {len(waiting_room_patients)} 位).",
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
                "delta": f"{shift_report['treated_patients']} treated in shift simulation (班次仿真处理 {shift_report['treated_patients']} 人).",
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
        "queue_modes": queue_modes,
        "control_buttons": [
            {"label": "Run Simulation (运行仿真)", "tone": "success"},
            {"label": "Open Dataset (打开数据集)", "tone": "warning"},
            {"label": "Inspect Queue (查看队列)", "tone": "outline"},
            {"label": "Refresh Snapshot (刷新快照)", "tone": "danger"},
        ],
        "system_overview": {
            "clock": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": "System Online (系统在线)",
            "runtime": f"{runtime_hours:02d}:{runtime_minutes:02d}:00",
            "simulated_patients": str(len(patients)),
            "utilization_label": f"{shift_report['compliance_rate']:.1f}%",
            "utilization_percent": max(1, min(100, int(round(shift_report["compliance_rate"])))),
        },
        "dataset_overview": {
            "file_name": DATASET_PATH.name,
            "rows": str(len(patients)),
            "generated_at": datetime.fromtimestamp(DATASET_PATH.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
        },
        "waiting_room_patients": waiting_room_patients,
        "heap_levels": _build_heap_levels(active_patients),
        "anomaly_breakdown": _build_anomaly_breakdown(inversions),
        "recent_anomalies": [
            {
                "time": item["higher_priority"].arrival_time.strftime("%H:%M"),
                "message": (
                    f"{_patient_code(item['higher_priority'].patient_id)} has waited {item['higher_wait']} min, "
                    f"while lower-priority {_patient_code(item['lower_priority'].patient_id)} waited {item['lower_wait']} min "
                    "(高优先级患者等待更久，存在优先级反转风险)."
                ),
            }
            for item in inversions[:3]
        ]
        or [
            {
                "time": current_time.strftime("%H:%M"),
                "message": "No priority inversion detected in the current snapshot (当前快照未发现优先级反转).",
            }
        ],
        "predicted_rows": estimate_rows,
        "overtime_card": {
            "risk_percent": timeout_summary["risk_percent"],
            "risk_label": top_risk_label,
            "details": [
                ("Queue Size (队列人数)", str(timeout_summary["queue_size"])),
                ("At-Risk Patients (风险患者)", str(len(timeout_summary["at_risk_ids"]))),
                (
                    "Top At-Risk IDs (高风险编号)",
                    ", ".join(_patient_code(patient_id) for patient_id in timeout_summary["at_risk_ids"][:4]) or "None",
                ),
            ],
        },
        "workstation_cards": [
            {
                "title": "Station A (诊室 A)",
                "status": "Serving the highest-priority patient first (按最高优先级接诊).",
                "detail": f"Current head: {waiting_room_patients[0]['patient_id'] if waiting_room_patients else 'N/A'}",
            },
            {
                "title": "Station B (诊室 B)",
                "status": "Comparing heap queue and ordered linked queue (对比两种队列实现).",
                "detail": f"Benchmark rows loaded: {len(performance_rows)}",
            },
            {
                "title": "Station C (诊室 C)",
                "status": "Monitoring analytics and overtime risk (监控分析与超时风险).",
                "detail": f"Priority inversions detected: {len(inversions)}",
            },
        ],
        "performance_rows": performance_rows,
        "performance_chart_available": PERFORMANCE_IMAGE_PATH.exists(),
        "performance_chart_path": str(PERFORMANCE_IMAGE_PATH),
        "performance_csv_available": PERFORMANCE_CSV_PATH.exists(),
        "performance_source_path": performance_artifact.get("csv_path", str(PERFORMANCE_CSV_PATH)),
        "project_map": project_map,
        "content_slots": content_slots,
    }
