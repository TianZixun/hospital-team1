from __future__ import annotations

from pathlib import Path


def get_dashboard_context() -> dict:
    """Return placeholder-friendly dashboard content for the Flask UI."""

    project_root = Path(__file__).resolve().parents[2]

    summary_cards = [
        {
            "badge": "WT",
            "title": "Avg Wait (平均等待)",
            "value": "18.6 min",
            "delta": "↓ 2.3 min vs yesterday (较昨日)",
            "tone": "positive",
        },
        {
            "badge": "CR",
            "title": "Compliance (合规率)",
            "value": "92.4%",
            "delta": "↑ 3.6% vs yesterday (较昨日)",
            "tone": "positive",
        },
        {
            "badge": "MW",
            "title": "Max Wait (最长等待)",
            "value": "78.0 min",
            "delta": "↑ 5.1 min vs yesterday (较昨日)",
            "tone": "warning",
        },
        {
            "badge": "AS",
            "title": "Active Stations (活跃诊室)",
            "value": "6 / 10",
            "delta": "60% utilization (利用率)",
            "tone": "neutral",
        },
    ]

    queue_modes = [
        {
            "key": "heap",
            "name": "Heap Queue (堆队列)",
            "desc": "Primary implementation: hospital_team1/queues/heap_priority_queue.py",
        },
        {
            "key": "ordered_list",
            "name": "Ordered Linked Queue (有序链表队列)",
            "desc": "Second implementation: hospital_team1/queues/ordered_linked_priority_queue.py",
        },
    ]

    control_buttons = [
        {"label": "Start (开始)", "tone": "success"},
        {"label": "Pause (暂停)", "tone": "warning"},
        {"label": "Step (单步)", "tone": "outline"},
        {"label": "Reset (重置)", "tone": "danger"},
    ]

    system_overview = {
        "clock": "2026-07-01 10:28:29",
        "status": "System Online (系统在线)",
        "runtime": "01:24:36",
        "simulated_patients": "342",
        "utilization_label": "68%",
        "utilization_percent": 68,
    }

    dataset_overview = {
        "file_name": "patients_sample.csv",
        "rows": "1,250",
        "generated_at": "10:20:01",
    }

    waiting_room_patients = [
        {
            "patient_id": "P0012",
            "name": "Zhang Wei",
            "priority": "High (高)",
            "arrival": "10:18",
            "wait": "22 min",
            "tone": "high",
        },
        {
            "patient_id": "P0045",
            "name": "Lin Na",
            "priority": "Medium (中)",
            "arrival": "10:20",
            "wait": "20 min",
            "tone": "medium",
        },
        {
            "patient_id": "P0078",
            "name": "Wang Lei",
            "priority": "Medium (中)",
            "arrival": "10:21",
            "wait": "19 min",
            "tone": "medium",
        },
        {
            "patient_id": "P0099",
            "name": "Chen Fang",
            "priority": "Low (低)",
            "arrival": "10:22",
            "wait": "18 min",
            "tone": "low",
        },
    ]

    heap_levels = [
        [{"label": "P0012", "priority": "High (高)", "tone": "high"}],
        [
            {"label": "P0045", "priority": "Medium (中)", "tone": "medium"},
            {"label": "P0078", "priority": "Medium (中)", "tone": "medium"},
        ],
        [
            {"label": "P0099", "priority": "Low (低)", "tone": "low"},
            {"label": "P0105", "priority": "Low (低)", "tone": "low"},
            {"label": "P0112", "priority": "Low (低)", "tone": "low"},
            {"label": "P0120", "priority": "Low (低)", "tone": "low"},
        ],
    ]

    recent_anomalies = [
        {
            "time": "10:05",
            "message": "Wait time spike detected at 10:05 (10:05 检测到等待时长突增)",
        },
        {
            "time": "09:58",
            "message": "Station 3 idle for more than 15 min (3 号诊室空闲超过 15 分钟)",
        },
        {
            "time": "09:52",
            "message": "High-priority queue threshold exceeded (高优先级患者队列超出阈值)",
        },
    ]

    predicted_rows = [
        {"priority": "High (高)", "wait": "15 - 25 min", "trend": "↗", "tone": "high"},
        {"priority": "Medium (中)", "wait": "25 - 40 min", "trend": "→", "tone": "medium"},
        {"priority": "Low (低)", "wait": "40 - 70 min", "trend": "↘", "tone": "low"},
    ]

    overtime_card = {
        "risk_percent": 62,
        "risk_label": "Medium (中)",
        "details": [
            ("Estimated Overtime (预计加班)", "1.8 hrs"),
            ("Overtime Probability (加班概率)", "62%"),
            ("Peak Risk Time (高风险时段)", "17:00 - 20:00"),
        ],
    }

    workstation_cards = [
        {
            "title": "Station A (诊室 A)",
            "status": "Treating P0012 (正在接诊 P0012)",
            "detail": "Expected finish (预计结束): 10:34",
        },
        {
            "title": "Station B (诊室 B)",
            "status": "Treating P0045 (正在接诊 P0045)",
            "detail": "Expected finish (预计结束): 10:41",
        },
        {
            "title": "Station C (诊室 C)",
            "status": "Open for next patient (等待下一位患者)",
            "detail": "Open interval rule (开放间隔规则): every 10 min",
        },
    ]

    performance_rows = [
        {"size": "10", "heap": "0.2 ms", "second": "0.3 ms", "simulation": "1.1 ms"},
        {"size": "100", "heap": "0.9 ms", "second": "1.8 ms", "simulation": "8.6 ms"},
        {"size": "500", "heap": "4.1 ms", "second": "12.4 ms", "simulation": "42.0 ms"},
        {"size": "1000", "heap": "8.8 ms", "second": "28.7 ms", "simulation": "83.4 ms"},
    ]

    project_map = [
        ("models/", "Patient and triage enum (患者与分诊枚举)"),
        ("structures/", "Linked list and waiting room (链表与候诊区)"),
        ("queues/", "Heap queue and second queue implementation (堆队列与第二队列实现)"),
        ("data/", "CSV generation and import (CSV 生成与导入)"),
        ("simulation/", "Scheduling simulation and compliance logic (调度仿真与合规逻辑)"),
        ("analysis/", "Performance and waiting-room analysis (性能与候诊区分析)"),
        ("visualization/", "CLI/GUI views (命令行与界面视图)"),
        ("utils/", "Shared constants and time helpers (共享常量与时间工具)"),
        ("tests/", "Unit and integration tests (单元与集成测试)"),
        ("scripts/", "Utility scripts (工具脚本)"),
        ("datasets/", "Sample datasets (示例数据集)"),
        ("docs/", "Documentation (Markdown 文档)"),
        ("slides/", "Presentation slides (演示文稿)"),
        ("main.py", "Application entry point (应用入口)"),
        ("test.py", "Run all tests (运行所有测试)"),
        ("README.md", "Project overview (项目概述)"),
        ("pyproject.toml", "Project configuration (项目配置)"),
    ]

    content_slots = [
        {
            "title": "Dataset Input (数据集输入)",
            "path": str(project_root / "datasets" / "patients_dataset.csv"),
            "hint": "Place the real patient CSV here (后续将真实患者 CSV 放在这里).",
        },
        {
            "title": "Simulation Output (仿真输出)",
            "path": "hospital_team1/simulation/report.py",
            "hint": "Generate summary metrics and time logs here (在这里生成统计指标和时间日志).",
        },
        {
            "title": "Benchmark Result (性能对比结果)",
            "path": "hospital_team1/analysis/performance.py",
            "hint": "Replace demo values with measured benchmark data (后续替换成真实测得性能数据).",
        },
        {
            "title": "Prediction Result (预测结果)",
            "path": "hospital_team1/analysis/predictor.py",
            "hint": "Write open-challenge prediction logic here (在这里实现开放题预测逻辑).",
        },
    ]

    return {
        "app_title": "Hospital Triage Scheduler (医院分诊调度系统)",
        "subtitle": "Scheduling dashboard (调度看板) for queue, simulation, analysis, and project structure.",
        "summary_cards": summary_cards,
        "queue_modes": queue_modes,
        "control_buttons": control_buttons,
        "system_overview": system_overview,
        "dataset_overview": dataset_overview,
        "waiting_room_patients": waiting_room_patients,
        "heap_levels": heap_levels,
        "recent_anomalies": recent_anomalies,
        "predicted_rows": predicted_rows,
        "overtime_card": overtime_card,
        "workstation_cards": workstation_cards,
        "performance_rows": performance_rows,
        "project_map": project_map,
        "content_slots": content_slots,
    }
