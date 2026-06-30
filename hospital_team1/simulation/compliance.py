from hospital_team1.models import TriageLevel


SERVICE_LIMIT_MINUTES = {
    TriageLevel.CRITICAL: 15,
    TriageLevel.URGENT: 30,
    TriageLevel.SEMI_URGENT: 60,
    TriageLevel.NON_URGENT: 120,
}


def is_wait_time_compliant(triage_level: TriageLevel, wait_minutes: int) -> bool:
    return wait_minutes <= SERVICE_LIMIT_MINUTES[triage_level]
