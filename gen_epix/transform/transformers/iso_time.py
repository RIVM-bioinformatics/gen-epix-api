"""
ISO time transformer implementation.
"""

import datetime
from typing import Callable

from gen_epix.transform.adapter import ObjectAdapter
from gen_epix.transform.enum import TimeUnit as TimeUnit
from gen_epix.transform.enum import (
    TimeUnitTransformStrategy as TimeUnitTransformStrategy,
)
from gen_epix.transform.transformer import Transformer


class IsoTimeTransformer(Transformer):
    """Transform ISO time values from one time unit to another."""

    DAY = TimeUnit.DAY
    WEEK = TimeUnit.WEEK
    MONTH = TimeUnit.MONTH
    QUARTER = TimeUnit.QUARTER
    YEAR = TimeUnit.YEAR

    EXACT_ONLY = TimeUnitTransformStrategy.EXACT_ONLY
    LARGEST_OVERLAP = TimeUnitTransformStrategy.LARGEST_OVERLAP

    # Static mapping of (src_unit, tgt_unit, strategy) to converter functions
    TRANSFORM_FN_MAP: dict[
        tuple[TimeUnit, TimeUnit, TimeUnitTransformStrategy],
        Callable[[str | None], str | None],
    ] = {}

    def __init__(
        self,
        field_name: str,
        src_unit: TimeUnit,
        tgt_unit: TimeUnit,
        strategy: TimeUnitTransformStrategy = TimeUnitTransformStrategy.EXACT_ONLY,
        tgt_field_name: str | None = None,
        name: str | None = None,
    ):
        super().__init__(name)
        self.field_name = field_name
        self.src_unit = src_unit
        self.tgt_unit = tgt_unit
        self.strategy = strategy
        self.tgt_field_name = tgt_field_name or field_name

        # Get the appropriate transform function
        self.transform_fn = self._get_transform_fn()

    def _get_transform_fn(self) -> Callable[[str | None], str | None]:
        """Get the appropriate transform function based on src_unit, tgt_unit, and strategy."""
        key = (self.src_unit, self.tgt_unit, self.strategy)
        if key in self.TRANSFORM_FN_MAP:
            return self.TRANSFORM_FN_MAP[key]

        # Fallback for unsupported combinations
        return self.convert_unsupported

    def transform(self, obj: ObjectAdapter) -> ObjectAdapter:
        """Transform the ISO time field if it exists."""
        if obj.has_key(self.field_name):
            current_value = obj.get(self.field_name)
            if current_value is not None:
                transformed_value = self.transform_fn(current_value)
                obj.set(self.tgt_field_name, transformed_value)
        return obj

    # Static converter methods for each combination

    @staticmethod
    def convert_same_unit(value: str | None) -> str | None:
        """Convert when source and target units are the same."""
        return value

    @staticmethod
    def convert_year_to_any(value: str | None) -> str | None:
        """Convert from YEAR (lowest resolution) to any other unit."""
        return None  # Cannot convert from lowest resolution

    @staticmethod
    def convert_quarter_to_year(value: str | None) -> str | None:
        """Convert from QUARTER to YEAR."""
        return None if value is None else value[0:4]

    @staticmethod
    def convert_quarter_to_unsupported(value: str | None) -> str | None:
        """Convert from QUARTER to unsupported target unit."""
        return None

    @staticmethod
    def convert_month_to_quarter(value: str | None) -> str | None:
        """Convert from MONTH to QUARTER."""
        if value is None:
            return None
        return value[0:4] + "-Q" + str((int(value[5:7]) + 2) // 3)

    @staticmethod
    def convert_month_to_year(value: str | None) -> str | None:
        """Convert from MONTH to YEAR."""
        return None if value is None else value[0:4]

    @staticmethod
    def convert_month_to_unsupported(value: str | None) -> str | None:
        """Convert from MONTH to unsupported target unit."""
        return None

    @staticmethod
    def convert_week_to_year_exact(value: str | None) -> str | None:
        """Convert from WEEK to YEAR using exact mode."""
        if value is None:
            return None

        week_start = IsoTimeTransformer._get_week_start(value)
        week_end = IsoTimeTransformer._get_week_end(value)

        # Only return year if both start and end are in the same year
        if week_start.year == week_end.year:
            return str(week_start.year)
        return None

    @staticmethod
    def convert_week_to_year_round(value: str | None) -> str | None:
        """Convert from WEEK to YEAR using round mode."""
        if value is None:
            return None

        week_start = IsoTimeTransformer._get_week_start(value)
        return str(week_start.year)

    @staticmethod
    def convert_week_to_quarter_exact(value: str | None) -> str | None:
        """Convert from WEEK to QUARTER using exact mode."""
        if value is None:
            return None

        week_start = IsoTimeTransformer._get_week_start(value)
        week_end = IsoTimeTransformer._get_week_end(value)

        start_quarter = (week_start.month + 2) // 3
        end_quarter = (week_end.month + 2) // 3

        # Only return quarter if both start and end are in the same quarter
        if week_start.year == week_end.year and start_quarter == end_quarter:
            return f"{week_start.year}-Q{start_quarter}"
        return None

    @staticmethod
    def convert_week_to_quarter_round(value: str | None) -> str | None:
        """Convert from WEEK to QUARTER using round mode."""
        if value is None:
            return None

        week_start = IsoTimeTransformer._get_week_start(value)
        week_mid = IsoTimeTransformer._get_week_mid(value)

        # Use the quarter where most days (4+) of the week fall
        if week_start.month == week_mid.month or week_mid.month not in [1, 4, 7, 10]:
            quarter = (week_start.month + 2) // 3
            return f"{week_start.year}-Q{quarter}"
        else:
            quarter = (week_mid.month + 2) // 3
            return f"{week_start.year}-Q{quarter}"

    @staticmethod
    def convert_week_to_month_exact(value: str | None) -> str | None:
        """Convert from WEEK to MONTH using exact mode."""
        if value is None:
            return None

        week_start = IsoTimeTransformer._get_week_start(value)
        week_end = IsoTimeTransformer._get_week_end(value)

        # Only return month if both start and end are in the same month
        if week_start.year == week_end.year and week_start.month == week_end.month:
            return f"{week_start.year}-{week_start.month:02}"
        return None

    @staticmethod
    def convert_week_to_month_round(value: str | None) -> str | None:
        """Convert from WEEK to MONTH using round mode."""
        if value is None:
            return None

        week_start = IsoTimeTransformer._get_week_start(value)
        week_mid = IsoTimeTransformer._get_week_mid(value)

        # Use the month where most days (4+) of the week fall
        if week_start.month == week_mid.month:
            return f"{week_start.year}-{week_start.month:02}"
        else:
            return f"{week_start.year}-{week_mid.month:02}"

    @staticmethod
    def convert_week_to_unsupported(value: str | None) -> str | None:
        """Convert from WEEK to unsupported target unit."""
        return None

    @staticmethod
    def convert_day_to_year(value: str | None) -> str | None:
        """Convert from DAY to YEAR."""
        return None if value is None else value[0:4]

    @staticmethod
    def convert_day_to_quarter(value: str | None) -> str | None:
        """Convert from DAY to QUARTER."""
        if value is None:
            return None
        return value[0:4] + "-Q" + str((int(value[5:7]) + 2) // 3)

    @staticmethod
    def convert_day_to_month(value: str | None) -> str | None:
        """Convert from DAY to MONTH."""
        return None if value is None else value[0:7]

    @staticmethod
    def convert_day_to_week(value: str | None) -> str | None:
        """Convert from DAY to WEEK."""
        if value is None:
            return None

        date_obj = datetime.date(int(value[0:4]), int(value[5:7]), int(value[8:10]))
        year, week, _ = date_obj.isocalendar()
        return f"{year}-W{week:02}"

    @staticmethod
    def convert_day_to_unsupported(value: str | None) -> str | None:
        """Convert from DAY to unsupported target unit."""
        return None

    @staticmethod
    def convert_unsupported(value: str | None) -> str | None:
        """Fallback for unsupported conversions."""
        return None

    @staticmethod
    def _get_week_start(value: str) -> datetime.date:
        """Calculate the start date of a given ISO week."""
        return datetime.date.fromisocalendar(int(value[0:4]), int(value[6:8]), 1)

    @staticmethod
    def _get_week_mid(value: str) -> datetime.date:
        """Calculate the middle date (Thursday) of a given ISO week."""
        return datetime.date.fromisocalendar(int(value[0:4]), int(value[6:8]), 4)

    @staticmethod
    def _get_week_end(value: str) -> datetime.date:
        """Calculate the end date of a given ISO week."""
        return datetime.date.fromisocalendar(int(value[0:4]), int(value[6:8]), 7)

    # Initialize the TRANSFORM_FN_MAP with enum values
    TRANSFORM_FN_MAP = {
        # Same unit conversions
        (YEAR, YEAR, EXACT_ONLY): convert_same_unit,
        (YEAR, YEAR, LARGEST_OVERLAP): convert_same_unit,
        (QUARTER, QUARTER, EXACT_ONLY): convert_same_unit,
        (QUARTER, QUARTER, LARGEST_OVERLAP): convert_same_unit,
        (MONTH, MONTH, EXACT_ONLY): convert_same_unit,
        (MONTH, MONTH, LARGEST_OVERLAP): convert_same_unit,
        (WEEK, WEEK, EXACT_ONLY): convert_same_unit,
        (WEEK, WEEK, LARGEST_OVERLAP): convert_same_unit,
        (DAY, DAY, EXACT_ONLY): convert_same_unit,
        (DAY, DAY, LARGEST_OVERLAP): convert_same_unit,
        # From YEAR (lowest resolution)
        (YEAR, QUARTER, EXACT_ONLY): convert_year_to_any,
        (YEAR, QUARTER, LARGEST_OVERLAP): convert_year_to_any,
        (YEAR, MONTH, EXACT_ONLY): convert_year_to_any,
        (YEAR, MONTH, LARGEST_OVERLAP): convert_year_to_any,
        (YEAR, WEEK, EXACT_ONLY): convert_year_to_any,
        (YEAR, WEEK, LARGEST_OVERLAP): convert_year_to_any,
        (YEAR, DAY, EXACT_ONLY): convert_year_to_any,
        (YEAR, DAY, LARGEST_OVERLAP): convert_year_to_any,
        # From QUARTER
        (QUARTER, YEAR, EXACT_ONLY): convert_quarter_to_year,
        (QUARTER, YEAR, LARGEST_OVERLAP): convert_quarter_to_year,
        (QUARTER, MONTH, EXACT_ONLY): convert_quarter_to_unsupported,
        (QUARTER, MONTH, LARGEST_OVERLAP): convert_quarter_to_unsupported,
        (QUARTER, WEEK, EXACT_ONLY): convert_quarter_to_unsupported,
        (QUARTER, WEEK, LARGEST_OVERLAP): convert_quarter_to_unsupported,
        (QUARTER, DAY, EXACT_ONLY): convert_quarter_to_unsupported,
        (QUARTER, DAY, LARGEST_OVERLAP): convert_quarter_to_unsupported,
        # From MONTH
        (MONTH, YEAR, EXACT_ONLY): convert_month_to_year,
        (MONTH, YEAR, LARGEST_OVERLAP): convert_month_to_year,
        (MONTH, QUARTER, EXACT_ONLY): convert_month_to_quarter,
        (MONTH, QUARTER, LARGEST_OVERLAP): convert_month_to_quarter,
        (MONTH, WEEK, EXACT_ONLY): convert_month_to_unsupported,
        (MONTH, WEEK, LARGEST_OVERLAP): convert_month_to_unsupported,
        (MONTH, DAY, EXACT_ONLY): convert_month_to_unsupported,
        (MONTH, DAY, LARGEST_OVERLAP): convert_month_to_unsupported,
        # From WEEK
        (WEEK, YEAR, EXACT_ONLY): convert_week_to_year_exact,
        (WEEK, YEAR, LARGEST_OVERLAP): convert_week_to_year_round,
        (WEEK, QUARTER, EXACT_ONLY): convert_week_to_quarter_exact,
        (WEEK, QUARTER, LARGEST_OVERLAP): convert_week_to_quarter_round,
        (WEEK, MONTH, EXACT_ONLY): convert_week_to_month_exact,
        (WEEK, MONTH, LARGEST_OVERLAP): convert_week_to_month_round,
        (WEEK, DAY, EXACT_ONLY): convert_week_to_unsupported,
        (WEEK, DAY, LARGEST_OVERLAP): convert_week_to_unsupported,
        # From DAY
        (DAY, YEAR, EXACT_ONLY): convert_day_to_year,
        (DAY, YEAR, LARGEST_OVERLAP): convert_day_to_year,
        (DAY, QUARTER, EXACT_ONLY): convert_day_to_quarter,
        (DAY, QUARTER, LARGEST_OVERLAP): convert_day_to_quarter,
        (DAY, MONTH, EXACT_ONLY): convert_day_to_month,
        (DAY, MONTH, LARGEST_OVERLAP): convert_day_to_month,
        (DAY, WEEK, EXACT_ONLY): convert_day_to_week,
        (DAY, WEEK, LARGEST_OVERLAP): convert_day_to_week,
    }
