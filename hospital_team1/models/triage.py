from enum import Enum


class TriageLevel(Enum):
    """Smaller values represent higher treatment priority."""

    CRITICAL = 1
    URGENT = 2
    SEMI_URGENT = 3
    NON_URGENT = 4
