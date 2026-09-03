"""Enumerations for temporal granularity, interval mapping, and result status."""

from enum import Enum


class TimeUnit(Enum):
    """Encapsulates supported ISO time granularities."""

    YEAR = "YEAR"
    QUARTER = "QUARTER"
    MONTH = "MONTH"
    WEEK = "WEEK"
    DAY = "DAY"


class TimeUnitTransformStrategy(Enum):
    """Encapsulates strategies for reducing ISO time granularity."""

    EXACT_ONLY = "EXACT_ONLY"
    LARGEST_OVERLAP = "LARGEST_OVERLAP"


class IntervalTransformStrategy(Enum):
    """Encapsulates strategies for mapping interval categorizations."""

    CONTAINS_ONLY = "CONTAINS_ONLY"
    LARGEST_OVERLAP = "LARGEST_OVERLAP"


class TransformType(Enum):
    """Encapsulates high-level transformation categories."""

    BASE = "BASE"


class TransformResultType(Enum):
    """Encapsulates transformation outcome classifications."""

    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    SKIPPED = "SKIPPED"
