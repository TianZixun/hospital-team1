from hospital_team1.models_part1.patient import Patient


def is_wait_time_compliant(patient: Patient, wait_minutes: float) -> bool:
    """判断某病人的等待时间是否在其分诊级别的合规范围内。

    合规阈值统一从 Patient.get_max_allowed_wait() 获取，
    避免在多处维护相同的分诊级别-时限映射。
    """
    return wait_minutes <= patient.get_max_allowed_wait()
