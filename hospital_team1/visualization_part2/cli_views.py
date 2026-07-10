from hospital_team1.models_part1 import Patient


def render_waiting_room_table(patients: list[Patient]) -> str:
    lines = ["patient_id | name | triage | arrival_time | est_minutes"]
    for patient in patients:
        lines.append(
            " | ".join(
                [
                    patient.patient_id,
                    patient.name,
                    patient.triage_level.name,
                    patient.arrival_time.strftime("%H:%M"),
                    str(patient.estimated_treatment_minutes),
                ]
            )
        )
    return "\n".join(lines)
