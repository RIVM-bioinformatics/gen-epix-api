"""
ISO time transformer implementation.
"""

import datetime
from typing import Callable

from gen_epix.transform.adapter import ObjectAdapter
from gen_epix.transform.enum import TimeUnit, TimeUnitTransformStrategy
from gen_epix.transform.transformer import Transformer


class IsoTimeTransformer(Transformer):
    """Transform ISO time values from one time unit to another."""

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
        name: str | None = None,
    ):
        super().__init__(name)
        self.field_name = field_name
        self.src_unit = src_unit
        self.tgt_unit = tgt_unit
        self.strategy = strategy

        # Get the appropriate transform function
        self.transform_fn = self._get_transform_fn()

    def _get_transform_fn(self) -> Callable[[str | None], str | None]:
        """Get the appropriate transform function based on src_unit, tgt_unit, and strategy."""
        key = (self.src_unit, self.tgt_unit, self.strategy)
        if key in self.TRANSFORM_FN_MAP:
            return self.TRANSFORM_FN_MAP[key]

        # Fallback for unsupported combinations
        return self._convert_unsupported

    def transform(self, obj: ObjectAdapter) -> ObjectAdapter:
        """Transform the ISO time field if it exists."""
        if obj.has_key(self.field_name):
            current_value = obj.get(self.field_name)
            if current_value is not None:
                transformed_value = self.transform_fn(current_value)
                obj.set(self.field_name, transformed_value)
        return obj

    # Static converter methods for each combination

    @staticmethod
    def _convert_same_unit(value: str | None) -> str | None:
        """Convert when source and target units are the same."""
        return value

    @staticmethod
    def _convert_year_to_any(value: str | None) -> str | None:
        """Convert from YEAR (lowest resolution) to any other unit."""
        return None  # Cannot convert from lowest resolution

    @staticmethod
    def _convert_quarter_to_year(value: str | None) -> str | None:
        """Convert from QUARTER to YEAR."""
        return None if value is None else value[0:4]

    @staticmethod
    def _convert_quarter_to_unsupported(value: str | None) -> str | None:
        """Convert from QUARTER to unsupported target unit."""
        return None

    @staticmethod
    def _convert_month_to_quarter(value: str | None) -> str | None:
        """Convert from MONTH to QUARTER."""
        if value is None:
            return None
        return value[0:4] + "-Q" + str((int(value[5:7]) + 2) // 3)

    @staticmethod
    def _convert_month_to_year(value: str | None) -> str | None:
        """Convert from MONTH to YEAR."""
        return None if value is None else value[0:4]

    @staticmethod
    def _convert_month_to_unsupported(value: str | None) -> str | None:
        """Convert from MONTH to unsupported target unit."""
        return None

    @staticmethod
    def _convert_week_to_year_exact(value: str | None) -> str | None:
        """Convert from WEEK to YEAR using exact mode."""
        if value is None:
            return None

        week_start = datetime.date.fromisocalendar(int(value[0:4]), int(value[6:8]), 1)
        week_end = datetime.date.fromisocalendar(int(value[0:4]), int(value[6:8]), 7)

        # Only return year if both start and end are in the same year
        if week_start.year == week_end.year:
            return str(week_start.year)
        return None

    @staticmethod
    def _convert_week_to_year_round(value: str | None) -> str | None:
        """Convert from WEEK to YEAR using round mode."""
        if value is None:
            return None

        week_start = datetime.date.fromisocalendar(int(value[0:4]), int(value[6:8]), 1)
        return str(week_start.year)

    @staticmethod
    def _convert_week_to_quarter_exact(value: str | None) -> str | None:
        """Convert from WEEK to QUARTER using exact mode."""
        if value is None:
            return None

        week_start = datetime.date.fromisocalendar(int(value[0:4]), int(value[6:8]), 1)
        week_end = datetime.date.fromisocalendar(int(value[0:4]), int(value[6:8]), 7)

        start_quarter = (week_start.month + 2) // 3
        end_quarter = (week_end.month + 2) // 3

        # Only return quarter if both start and end are in the same quarter
        if week_start.year == week_end.year and start_quarter == end_quarter:
            return f"{week_start.year}-Q{start_quarter}"
        return None

    @staticmethod
    def _convert_week_to_quarter_round(value: str | None) -> str | None:
        """Convert from WEEK to QUARTER using round mode."""
        if value is None:
            return None

        week_start = datetime.date.fromisocalendar(int(value[0:4]), int(value[6:8]), 1)
        week_mid = datetime.date.fromisocalendar(int(value[0:4]), int(value[6:8]), 4)

        # Use the quarter where most days (4+) of the week fall
        if week_start.month == week_mid.month or week_mid.month not in [1, 4, 7, 10]:
            quarter = (week_start.month + 2) // 3
            return f"{week_start.year}-Q{quarter}"
        else:
            quarter = (week_mid.month + 2) // 3
            return f"{week_start.year}-Q{quarter}"

    @staticmethod
    def _convert_week_to_month_exact(value: str | None) -> str | None:
        """Convert from WEEK to MONTH using exact mode."""
        if value is None:
            return None

        week_start = datetime.date.fromisocalendar(int(value[0:4]), int(value[6:8]), 1)
        week_end = datetime.date.fromisocalendar(int(value[0:4]), int(value[6:8]), 7)

        # Only return month if both start and end are in the same month
        if week_start.year == week_end.year and week_start.month == week_end.month:
            return f"{week_start.year}-{week_start.month:02}"
        return None

    @staticmethod
    def _convert_week_to_month_round(value: str | None) -> str | None:
        """Convert from WEEK to MONTH using round mode."""
        if value is None:
            return None

        week_start = datetime.date.fromisocalendar(int(value[0:4]), int(value[6:8]), 1)
        week_mid = datetime.date.fromisocalendar(int(value[0:4]), int(value[6:8]), 4)

        # Use the month where most days (4+) of the week fall
        if week_start.month == week_mid.month:
            return f"{week_start.year}-{week_start.month:02}"
        else:
            return f"{week_start.year}-{week_mid.month:02}"

    @staticmethod
    def _convert_week_to_unsupported(value: str | None) -> str | None:
        """Convert from WEEK to unsupported target unit."""
        return None

    @staticmethod
    def _convert_day_to_year(value: str | None) -> str | None:
        """Convert from DAY to YEAR."""
        return None if value is None else value[0:4]

    @staticmethod
    def _convert_day_to_quarter(value: str | None) -> str | None:
        """Convert from DAY to QUARTER."""
        if value is None:
            return None
        return value[0:4] + "-Q" + str((int(value[5:7]) + 2) // 3)

    @staticmethod
    def _convert_day_to_month(value: str | None) -> str | None:
        """Convert from DAY to MONTH."""
        return None if value is None else value[0:7]

    @staticmethod
    def _convert_day_to_week(value: str | None) -> str | None:
        """Convert from DAY to WEEK."""
        if value is None:
            return None

        date_obj = datetime.date(int(value[0:4]), int(value[5:7]), int(value[8:10]))
        year, week, _ = date_obj.isocalendar()
        return f"{year}-W{week:02}"

    @staticmethod
    def _convert_day_to_unsupported(value: str | None) -> str | None:
        """Convert from DAY to unsupported target unit."""
        return None

    @staticmethod
    def _convert_unsupported(value: str | None) -> str | None:
        """Fallback for unsupported conversions."""
        return None

    # Initialize the TRANSFORM_FN_MAP with enum values
    TRANSFORM_FN_MAP = {
        # Same unit conversions
        (
            TimeUnit.YEAR,
            TimeUnit.YEAR,
            TimeUnitTransformStrategy.EXACT_ONLY,
        ): _convert_same_unit,
        (
            TimeUnit.YEAR,
            TimeUnit.YEAR,
            TimeUnitTransformStrategy.LARGEST_OVERLAP,
        ): _convert_same_unit,
        (
            TimeUnit.QUARTER,
            TimeUnit.QUARTER,
            TimeUnitTransformStrategy.EXACT_ONLY,
        ): _convert_same_unit,
        (
            TimeUnit.QUARTER,
            TimeUnit.QUARTER,
            TimeUnitTransformStrategy.LARGEST_OVERLAP,
        ): _convert_same_unit,
        (
            TimeUnit.MONTH,
            TimeUnit.MONTH,
            TimeUnitTransformStrategy.EXACT_ONLY,
        ): _convert_same_unit,
        (
            TimeUnit.MONTH,
            TimeUnit.MONTH,
            TimeUnitTransformStrategy.LARGEST_OVERLAP,
        ): _convert_same_unit,
        (
            TimeUnit.WEEK,
            TimeUnit.WEEK,
            TimeUnitTransformStrategy.EXACT_ONLY,
        ): _convert_same_unit,
        (
            TimeUnit.WEEK,
            TimeUnit.WEEK,
            TimeUnitTransformStrategy.LARGEST_OVERLAP,
        ): _convert_same_unit,
        (
            TimeUnit.DAY,
            TimeUnit.DAY,
            TimeUnitTransformStrategy.EXACT_ONLY,
        ): _convert_same_unit,
        (
            TimeUnit.DAY,
            TimeUnit.DAY,
            TimeUnitTransformStrategy.LARGEST_OVERLAP,
        ): _convert_same_unit,
        # From YEAR (lowest resolution)
        (
            TimeUnit.YEAR,
            TimeUnit.QUARTER,
            TimeUnitTransformStrategy.EXACT_ONLY,
        ): _convert_year_to_any,
        (
            TimeUnit.YEAR,
            TimeUnit.QUARTER,
            TimeUnitTransformStrategy.LARGEST_OVERLAP,
        ): _convert_year_to_any,
        (
            TimeUnit.YEAR,
            TimeUnit.MONTH,
            TimeUnitTransformStrategy.EXACT_ONLY,
        ): _convert_year_to_any,
        (
            TimeUnit.YEAR,
            TimeUnit.MONTH,
            TimeUnitTransformStrategy.LARGEST_OVERLAP,
        ): _convert_year_to_any,
        (
            TimeUnit.YEAR,
            TimeUnit.WEEK,
            TimeUnitTransformStrategy.EXACT_ONLY,
        ): _convert_year_to_any,
        (
            TimeUnit.YEAR,
            TimeUnit.WEEK,
            TimeUnitTransformStrategy.LARGEST_OVERLAP,
        ): _convert_year_to_any,
        (
            TimeUnit.YEAR,
            TimeUnit.DAY,
            TimeUnitTransformStrategy.EXACT_ONLY,
        ): _convert_year_to_any,
        (
            TimeUnit.YEAR,
            TimeUnit.DAY,
            TimeUnitTransformStrategy.LARGEST_OVERLAP,
        ): _convert_year_to_any,
        # From QUARTER
        (
            TimeUnit.QUARTER,
            TimeUnit.YEAR,
            TimeUnitTransformStrategy.EXACT_ONLY,
        ): _convert_quarter_to_year,
        (
            TimeUnit.QUARTER,
            TimeUnit.YEAR,
            TimeUnitTransformStrategy.LARGEST_OVERLAP,
        ): _convert_quarter_to_year,
        (
            TimeUnit.QUARTER,
            TimeUnit.MONTH,
            TimeUnitTransformStrategy.EXACT_ONLY,
        ): _convert_quarter_to_unsupported,
        (
            TimeUnit.QUARTER,
            TimeUnit.MONTH,
            TimeUnitTransformStrategy.LARGEST_OVERLAP,
        ): _convert_quarter_to_unsupported,
        (
            TimeUnit.QUARTER,
            TimeUnit.WEEK,
            TimeUnitTransformStrategy.EXACT_ONLY,
        ): _convert_quarter_to_unsupported,
        (
            TimeUnit.QUARTER,
            TimeUnit.WEEK,
            TimeUnitTransformStrategy.LARGEST_OVERLAP,
        ): _convert_quarter_to_unsupported,
        (
            TimeUnit.QUARTER,
            TimeUnit.DAY,
            TimeUnitTransformStrategy.EXACT_ONLY,
        ): _convert_quarter_to_unsupported,
        (
            TimeUnit.QUARTER,
            TimeUnit.DAY,
            TimeUnitTransformStrategy.LARGEST_OVERLAP,
        ): _convert_quarter_to_unsupported,
        # From MONTH
        (
            TimeUnit.MONTH,
            TimeUnit.YEAR,
            TimeUnitTransformStrategy.EXACT_ONLY,
        ): _convert_month_to_year,
        (
            TimeUnit.MONTH,
            TimeUnit.YEAR,
            TimeUnitTransformStrategy.LARGEST_OVERLAP,
        ): _convert_month_to_year,
        (
            TimeUnit.MONTH,
            TimeUnit.QUARTER,
            TimeUnitTransformStrategy.EXACT_ONLY,
        ): _convert_month_to_quarter,
        (
            TimeUnit.MONTH,
            TimeUnit.QUARTER,
            TimeUnitTransformStrategy.LARGEST_OVERLAP,
        ): _convert_month_to_quarter,
        (
            TimeUnit.MONTH,
            TimeUnit.WEEK,
            TimeUnitTransformStrategy.EXACT_ONLY,
        ): _convert_month_to_unsupported,
        (
            TimeUnit.MONTH,
            TimeUnit.WEEK,
            TimeUnitTransformStrategy.LARGEST_OVERLAP,
        ): _convert_month_to_unsupported,
        (
            TimeUnit.MONTH,
            TimeUnit.DAY,
            TimeUnitTransformStrategy.EXACT_ONLY,
        ): _convert_month_to_unsupported,
        (
            TimeUnit.MONTH,
            TimeUnit.DAY,
            TimeUnitTransformStrategy.LARGEST_OVERLAP,
        ): _convert_month_to_unsupported,
        # From WEEK
        (
            TimeUnit.WEEK,
            TimeUnit.YEAR,
            TimeUnitTransformStrategy.EXACT_ONLY,
        ): _convert_week_to_year_exact,
        (
            TimeUnit.WEEK,
            TimeUnit.YEAR,
            TimeUnitTransformStrategy.LARGEST_OVERLAP,
        ): _convert_week_to_year_round,
        (
            TimeUnit.WEEK,
            TimeUnit.QUARTER,
            TimeUnitTransformStrategy.EXACT_ONLY,
        ): _convert_week_to_quarter_exact,
        (
            TimeUnit.WEEK,
            TimeUnit.QUARTER,
            TimeUnitTransformStrategy.LARGEST_OVERLAP,
        ): _convert_week_to_quarter_round,
        (
            TimeUnit.WEEK,
            TimeUnit.MONTH,
            TimeUnitTransformStrategy.EXACT_ONLY,
        ): _convert_week_to_month_exact,
        (
            TimeUnit.WEEK,
            TimeUnit.MONTH,
            TimeUnitTransformStrategy.LARGEST_OVERLAP,
        ): _convert_week_to_month_round,
        (
            TimeUnit.WEEK,
            TimeUnit.DAY,
            TimeUnitTransformStrategy.EXACT_ONLY,
        ): _convert_week_to_unsupported,
        (
            TimeUnit.WEEK,
            TimeUnit.DAY,
            TimeUnitTransformStrategy.LARGEST_OVERLAP,
        ): _convert_week_to_unsupported,
        # From DAY
        (
            TimeUnit.DAY,
            TimeUnit.YEAR,
            TimeUnitTransformStrategy.EXACT_ONLY,
        ): _convert_day_to_year,
        (
            TimeUnit.DAY,
            TimeUnit.YEAR,
            TimeUnitTransformStrategy.LARGEST_OVERLAP,
        ): _convert_day_to_year,
        (
            TimeUnit.DAY,
            TimeUnit.QUARTER,
            TimeUnitTransformStrategy.EXACT_ONLY,
        ): _convert_day_to_quarter,
        (
            TimeUnit.DAY,
            TimeUnit.QUARTER,
            TimeUnitTransformStrategy.LARGEST_OVERLAP,
        ): _convert_day_to_quarter,
        (
            TimeUnit.DAY,
            TimeUnit.MONTH,
            TimeUnitTransformStrategy.EXACT_ONLY,
        ): _convert_day_to_month,
        (
            TimeUnit.DAY,
            TimeUnit.MONTH,
            TimeUnitTransformStrategy.LARGEST_OVERLAP,
        ): _convert_day_to_month,
        (
            TimeUnit.DAY,
            TimeUnit.WEEK,
            TimeUnitTransformStrategy.EXACT_ONLY,
        ): _convert_day_to_week,
        (
            TimeUnit.DAY,
            TimeUnit.WEEK,
            TimeUnitTransformStrategy.LARGEST_OVERLAP,
        ): _convert_day_to_week,
    }
