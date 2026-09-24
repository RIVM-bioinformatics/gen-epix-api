"""Define shared bounds and validation patterns for commondb domain values.

The module provides the null UUID sentinel, datetime and request-size limits,
and compiled regular expressions used to validate numeric and ISO-like temporal
representations across commondb models and services.
"""

import datetime
import re
from uuid import UUID

NULL_ID = UUID("00000000-0000-0000-0000-000000000000")

MIN_DATETIME = datetime.datetime(1, 1, 1, 0, 0, 0)
MAX_DATETIME = datetime.datetime(9999, 12, 31, 23, 59, 59, 999999)

MAX_CODE_FIELD_LENGTH = 255
MAX_REQUEST_BODY_ITERABLE_FIELD_LENGTH = 10000
MAX_REQUEST_BODY_FILE_CONTENT_LENGTH = 100 * 1024 * 1024  # 100 MB

FLOAT_PATTERN = re.compile(
    r"^[+-]?("
    r"(?:\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?"  # normal floats + scientific notation
    r"|inf(?:inity)?"  # inf / infinity
    r"|nan"  # nan
    r")$",
    re.IGNORECASE,
)

DECIMAL_PATTERN = re.compile(r"^[+-]?([0-9]*[.,])?[0-9]+$")

TIME_YEAR_PATTERN = re.compile(r"^\d{4}$")
TIME_QUARTER_PATTERN = re.compile(r"^\d{4}-Q[1-4]$")
TIME_MONTH_PATTERN = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")
TIME_WEEK_PATTERN = re.compile(r"^\d{4}-W(0[1-9]|[1-4]\d|5[0-3])$")
TIME_DAY_PATTERN = re.compile(r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$")

# TODO: consider full and partial ISO 8601 pattern
ISODATE_PATTERN = re.compile(
    r"^"
    r"\d{4}"  # YYYY (year only)
    r"|"
    r"\d{4}-(0[1-9]|1[0-2])"  # YYYY-MM (year + month only)
    r"|"
    r"\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])"  # YYYY-MM-DD
    r"|"
    r"\d{4}-Q[1-4]"  # YYYY-QN (quarter)
    r"|"
    r"\d{4}-W(0[1-9]|[1-4]\d|5[0-3])"  # YYYY-WNN (week)
    r"$"
)
