"""Enumerations used by transform strategies and result classification."""

from enum import Enum


class TimeUnit(Enum):
    """Supported ISO time granularities for time transformations."""

    YEAR = "YEAR"
    QUARTER = "QUARTER"
    MONTH = "MONTH"
    WEEK = "WEEK"
    DAY = "DAY"


class TimeUnitTransformStrategy(Enum):
    """Strategies for reducing an ISO time value to a coarser granularity."""

    EXACT_ONLY = "EXACT_ONLY"
    LARGEST_OVERLAP = "LARGEST_OVERLAP"


class IntervalTransformStrategy(Enum):
    """Strategies for mapping intervals between categorizations."""

    CONTAINS_ONLY = "CONTAINS_ONLY"
    LARGEST_OVERLAP = "LARGEST_OVERLAP"


class TransformType(Enum):
    """High-level transformation categories."""

    BASE = "BASE"


class TransformResultType(Enum):
    """Enum for different types of transformation results."""

    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    SKIPPED = "SKIPPED"
