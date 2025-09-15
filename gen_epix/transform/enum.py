from enum import Enum


class TimeUnit(Enum):
    YEAR = "YEAR"
    QUARTER = "QUARTER"
    MONTH = "MONTH"
    WEEK = "WEEK"
    DAY = "DAY"


class TimeUnitTransformStrategy(Enum):
    EXACT_ONLY = "EXACT_ONLY"
    LARGEST_OVERLAP = "LARGEST_OVERLAP"


class NoMatchStrategy(Enum):
    RAISE = "RAISE"
    SET_NONE = "SET_NONE"


class TransformType(Enum):
    BASE = "BASE"


class TransformResultType(Enum):
    """Enum for different types of transformation results."""

    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    SKIPPED = "SKIPPED"
