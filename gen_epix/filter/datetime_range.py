"""Datetime-valued inclusive and exclusive range filters."""

import datetime
from collections.abc import Callable
from typing import Any, Literal

from pydantic import Field

from gen_epix.filter.enum import FilterType
from gen_epix.filter.range import RangeFilter


class DatetimeRangeFilter(RangeFilter):
    """Represents a filter matching datetimes within the configured bounds."""

    type: Literal[FilterType.DATETIME_RANGE.value] = FilterType.DATETIME_RANGE.value  # type: ignore[name-defined]

    lower_bound: datetime.datetime | None = Field(
        default=None, description="The lower bound of the range.", frozen=True
    )
    upper_bound: datetime.datetime | None = Field(
        default=None, description="The upper bound of the range.", frozen=True
    )

    @staticmethod
    def _is_timezone_aware(value: datetime.datetime) -> bool:
        """Return whether a datetime has a usable UTC offset."""
        return value.tzinfo is not None and value.utcoffset() is not None

    def _validate_state_bounds(self) -> None:
        """Reject bounds that mix timezone-aware and naive datetimes."""
        if (
            self.lower_bound is not None
            and self.upper_bound is not None
            and self._is_timezone_aware(self.lower_bound)
            != self._is_timezone_aware(self.upper_bound)
        ):
            raise ValueError(
                "Datetime range bounds must both be timezone-aware or both be naive."
            )
        super()._validate_state_bounds()

    def _wrap_matcher(self) -> None:
        """Raise a clear error if a candidate has different timezone awareness."""
        matcher: Callable[[Any], bool] = self._match
        bound = self.lower_bound if self.lower_bound is not None else self.upper_bound
        assert bound is not None
        bound_is_aware = self._is_timezone_aware(bound)

        def match(value: Any) -> bool:
            if (
                isinstance(value, datetime.datetime)
                and self._is_timezone_aware(value) != bound_is_aware
            ):
                raise ValueError(
                    "Datetime filter candidate and bounds must have the same "
                    "timezone awareness."
                )
            return matcher(value)

        self._match = match  # type: ignore[method-assign]

    def _build_bounded_matcher(self) -> None:
        """Build a bounded matcher with a candidate-awareness guard."""
        super()._build_bounded_matcher()
        self._wrap_matcher()

    def _build_lower_bound_matcher(self) -> None:
        """Build a lower-bounded matcher with a candidate-awareness guard."""
        super()._build_lower_bound_matcher()
        self._wrap_matcher()

    def _build_upper_bound_matcher(self) -> None:
        """Build an upper-bounded matcher with a candidate-awareness guard."""
        super()._build_upper_bound_matcher()
        self._wrap_matcher()
