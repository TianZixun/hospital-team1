from __future__ import annotations


def build_shift_report(simulation_result: dict) -> dict:
    records = simulation_result.get("records", [])
    untreated = simulation_result.get("untreated", [])
    if not records:
        return {
            "treated_patients": 0,
            "average_wait_minutes": 0.0,
            "compliance_rate": 0.0,
            "max_wait_minutes": 0.0,
            "untreated_patients": len(untreated),
        }

    average_wait = sum(record["wait_minutes"] for record in records) / len(records)
    compliance = (
        sum(1 for record in records if record["within_threshold"]) / len(records) * 100
    )
    max_wait = max(record["wait_minutes"] for record in records)
    return {
        "treated_patients": len(records),
        "average_wait_minutes": round(average_wait, 1),
        "compliance_rate": round(compliance, 1),
        "max_wait_minutes": round(max_wait, 1),
        "untreated_patients": len(untreated),
    }
