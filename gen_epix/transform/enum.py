from enum import Enum


class TimeUnit(Enum):
    YEAR = "YEAR"
    QUARTER = "QUARTER"
    MONTH = "MONTH"
    WEEK = "WEEK"
    DAY = "DAY"


class TransformType(Enum):
    BASE = "base"
