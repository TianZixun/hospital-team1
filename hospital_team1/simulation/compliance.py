from hospital_team1.models import TriageLevel


SERVICE_LIMIT_MINUTES = {
    TriageLevel.CRITICAL: 0,
    TriageLevel.URGENT: 20,
    TriageLevel.SEMI_URGENT: 35,
    TriageLevel.NON_URGENT: 60,
}


def is_wait_time_compliant(triage_level: TriageLevel, wait_minutes: int) -> bool:
    return wait_minutes <= SERVICE_LIMIT_MINUTES[triage_level]
