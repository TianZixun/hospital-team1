from datetime import datetime


def minutes_between(start_time: datetime, end_time: datetime) -> int:
    delta = end_time - start_time
    return int(delta.total_seconds() // 60)
