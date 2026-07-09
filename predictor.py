from __future__ import annotations

from datetime import datetime

from .timeout_prediction import summarize_timeout_risk


def predict_overtime_patients(
    current_time: datetime | None = None,
) -> list[dict[str, object]]:
    summary = summarize_timeout_risk(current_time)
    return summary["details"]
