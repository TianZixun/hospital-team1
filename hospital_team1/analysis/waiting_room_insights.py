def detect_priority_anomalies() -> list[dict]:
    raise NotImplementedError("TODO: detect higher-priority waiting anomalies.")


def estimate_wait_time_for_new_arrival() -> dict:
    raise NotImplementedError("TODO: estimate wait time by incoming triage level.")
