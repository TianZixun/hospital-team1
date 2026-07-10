from enum import Enum


class TriageLevel(Enum):
    """Smaller values represent higher treatment priority."""

    CRITICAL = 1
    URGENT = 2
    SEMI_URGENT = 3
    NON_URGENT = 4

    @classmethod
    def from_integer(cls, num: int) -> "TriageLevel":
        for level in cls:
            if level.value == num:
                return level
        raise ValueError(f"Invalid triage level integer: {num}")
