from datetime import datetime

from hospital_team1 import Patient, TriageLevel


def run_smoke_demo() -> None:
    patient = Patient(
        patient_id="P001",
        name="Zhang San",
        age=45,
        triage_level=TriageLevel.CRITICAL,
        arrival_time=datetime(2026, 6, 30, 8, 5),
        estimated_treatment_minutes=20,
    )
    print("Project scaffold smoke test is running.")
    print(patient)
    print("Triage priority value:", patient.triage_level.value)


if __name__ == "__main__":
    run_smoke_demo()
