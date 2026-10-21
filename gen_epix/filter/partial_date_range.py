"""Range filters for dates represented at partial ISO precision."""

import datetime
from typing import Callable, Literal, Self

import dateutil
from pydantic import Field, model_validator

from gen_epix.filter import enum
from gen_epix.filter.enum import FilterType
from gen_epix.filter.range import RangeFilter


class PartialDateRangeFilter(RangeFilter):
    """Represents a filter matching partial dates within a configured range.

    Model validation:
    Bound strings are expanded to their represented intervals before matching.
    """

    type: Literal[FilterType.PARTIAL_DATE_RANGE.value] = (  # type: ignore[name-defined]
        FilterType.PARTIAL_DATE_RANGE.value
    )

    lower_bound: str | None = Field(
        default=None, description="The lower bound of the range.", frozen=True
    )
    upper_bound: str | None = Field(
        default=None, description="The upper bound of the range.", frozen=True
    )

    @staticmethod
    def fromisoformat(datetime_str: str) -> datetime.datetime:
        """Parse an ISO-formatted datetime string."""
        return datetime.datetime.fromisoformat(datetime_str)

    @staticmethod
    def _get_datetime_bounds(value: str) -> tuple[datetime.datetime, datetime.datetime]:
        """Return the inclusive lower and exclusive upper datetime bounds."""
        fromisoformat = PartialDateRangeFilter.fromisoformat
        if len(value) == 4:
            # YYYY
            datetime_ = fromisoformat(f"{value}-01-01")
            return datetime_, datetime_ + dateutil.relativedelta.relativedelta(years=1)
        if len(value) == 7:
            if "Q" in value:
                # YYYY-Qq
                match value[-1]:
                    case "1":
                        datetime_ = fromisoformat(value[0:4] + "-01-01")
                    case "2":
                        datetime_ = fromisoformat(value[0:4] + "-04-01")
                    case "3":
                        datetime_ = fromisoformat(value[0:4] + "-07-01")
                    case "4":
                        datetime_ = fromisoformat(value[0:4] + "-10-01")
                    case _:
                        raise ValueError(f"Invalid partial-date quarter: {value}")
                return datetime_, datetime_ + dateutil.relativedelta.relativedelta(
                    months=3
                )
            else:
                # YYYY-MM
                datetime_ = fromisoformat(f"{value}-01")
                return datetime_, datetime_ + dateutil.relativedelta.relativedelta(
                    months=1
                )
        if len(value) == 8:
            if "W" in value:
                # YYYY-Www
                datetime_ = fromisoformat(value)
                return datetime_, datetime_ + datetime.timedelta(weeks=1)
            else:
                # YYYYMMDD
                datetime_ = fromisoformat(value)
                return datetime_, datetime_ + datetime.timedelta(days=1)
        if len(value) == 10:
            # YYYY-MM-DD
            datetime_ = fromisoformat(value)
            return datetime_, datetime_ + datetime.timedelta(days=1)
        if len(value) == 13:
            # YYYY-MM-DDTHH
            datetime_ = fromisoformat(value)
            return datetime_, datetime_ + datetime.timedelta(hours=1)
        if len(value) == 16:
            # YYYY-MM-DDTHH:MM
            datetime_ = fromisoformat(value)
            return datetime_, datetime_ + datetime.timedelta(minutes=1)
        if len(value) == 19:
            # YYYY-MM-DDTHH:MM:SS
            datetime_ = fromisoformat(value)
            return datetime_, datetime_ + datetime.timedelta(seconds=1)
        # Anything else, seconds resolution used
        datetime_ = fromisoformat(value)
        return datetime_, datetime_ + datetime.timedelta(seconds=1)

    @model_validator(mode="after")
    def _validate_state(self) -> Self:
        """Derive bound intervals and build the partial-date matching function."""
        self._derive_bound_intervals()
        self._match = self._build_matcher()  # type: ignore
        return self

    def _derive_bound_intervals(self) -> None:
        """Derive inclusive and exclusive intervals for configured bounds."""
        # Derive lower/upper lower bound and lower/upper upper bound from string bounds
        lower_bounds: tuple[datetime.datetime | None, datetime.datetime | None] = (
            self._get_datetime_bounds(self.lower_bound)
            if self.lower_bound is not None
            else (None, None)
        )
        self._llb, self._ulb = lower_bounds
        upper_bounds: tuple[datetime.datetime | None, datetime.datetime | None] = (
            self._get_datetime_bounds(self.upper_bound)
            if self.upper_bound is not None
            else (None, None)
        )
        self._lub, self._uub = upper_bounds

    def _build_matcher(self) -> Callable[[str], bool]:
        # Generate the function to check if a value is within the range
        # The function is generated instead of defined to be able to optimize the check
        if self.lower_bound is not None and self.upper_bound is not None:
            return self._build_partial_bounded_matcher()
        elif self.lower_bound is not None:
            return self._build_partial_lower_bound_matcher()
        elif self.upper_bound is not None:
            return self._build_partial_upper_bound_matcher()
        raise AssertionError("At least one bound must be set.")

    def _build_partial_bounded_matcher(self) -> Callable[[str], bool]:
        """Build a matcher for a partial-date range with both bounds."""
        lower_start, lower_end = self._llb, self._ulb
        upper_start, upper_end = self._lub, self._uub
        assert (
            lower_start is not None
            and lower_end is not None
            and upper_start is not None
            and upper_end is not None
        )
        if (
            self.lower_bound_censor == enum.ComparisonOperator.GTE
            and self.upper_bound_censor == enum.ComparisonOperator.ST
        ):

            def _match(value: str) -> bool:
                """Match a partial date with inclusive lower and exclusive upper bounds."""
                l_value, u_value = PartialDateRangeFilter._get_datetime_bounds(value)
                return lower_start <= l_value and u_value <= upper_start

        elif (
            self.lower_bound_censor == enum.ComparisonOperator.GTE
            and self.upper_bound_censor == enum.ComparisonOperator.STE
        ):

            def _match(value: str) -> bool:
                """Match a partial date with inclusive range bounds."""
                l_value, u_value = PartialDateRangeFilter._get_datetime_bounds(value)
                return lower_start <= l_value and u_value <= upper_end

        elif (
            self.lower_bound_censor == enum.ComparisonOperator.GT
            and self.upper_bound_censor == enum.ComparisonOperator.ST
        ):

            def _match(value: str) -> bool:
                """Match a partial date with exclusive lower and upper bounds."""
                l_value, u_value = PartialDateRangeFilter._get_datetime_bounds(value)
                return lower_end <= l_value and u_value <= upper_start

        else:

            def _match(value: str) -> bool:
                """Match a partial date with exclusive lower and inclusive upper bounds."""
                l_value, u_value = PartialDateRangeFilter._get_datetime_bounds(value)
                return lower_end <= l_value and u_value <= upper_end

        return _match

    def _build_partial_lower_bound_matcher(self) -> Callable[[str], bool]:
        """Build a matcher for a partial-date lower bound."""
        lower_start, lower_end = self._llb, self._ulb
        assert lower_start is not None and lower_end is not None
        if self.lower_bound_censor == enum.ComparisonOperator.GTE:

            def _match(value: str) -> bool:
                """Match a partial date against an inclusive lower bound."""
                l_value, _ = PartialDateRangeFilter._get_datetime_bounds(value)
                return lower_start <= l_value

        else:

            def _match(value: str) -> bool:
                """Match a partial date against an exclusive lower bound."""
                l_value, _ = PartialDateRangeFilter._get_datetime_bounds(value)
                return lower_end <= l_value

        return _match

    def _build_partial_upper_bound_matcher(self) -> Callable[[str], bool]:
        """Build a matcher for a partial-date upper bound."""
        upper_start, upper_end = self._lub, self._uub
        assert upper_start is not None and upper_end is not None
        if self.upper_bound_censor == enum.ComparisonOperator.ST:

            def _match(value: str) -> bool:
                """Match a partial date against an exclusive upper bound."""
                _, u_value = PartialDateRangeFilter._get_datetime_bounds(value)
                return u_value <= upper_start

        else:

            def _match(value: str) -> bool:
                """Match a partial date against an inclusive upper bound."""
                _, u_value = PartialDateRangeFilter._get_datetime_bounds(value)
                return u_value <= upper_end

        return _match
