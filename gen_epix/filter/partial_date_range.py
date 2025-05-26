import datetime
from typing import Literal, Self

import dateutil
from pydantic import Field, model_validator

from gen_epix.filter import enum
from gen_epix.filter.enum import FilterType
from gen_epix.filter.range import RangeFilter


class PartialDateRangeFilter(RangeFilter):
    lower_bound: str | None = Field(
        default=None, description="The lower bound of the range.", frozen=True
    )
    upper_bound: str | None = Field(
        default=None, description="The upper bound of the range.", frozen=True
    )

    @staticmethod
    def fromisoformat(datetime_str: str) -> datetime.datetime:
        return datetime.datetime.fromisoformat(datetime_str)

    @staticmethod
    def _get_datetime_bounds(value: str) -> tuple[datetime.datetime, datetime.datetime]:
        """
        Get the inclusive lower and exclusive upper bound of an ISO datetime string.
        """
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
        # Derive lower/upper lower bound and lower/upper upper bound from string bounds
        if self.lower_bound is not None:
            self._llb, self._ulb = self._get_datetime_bounds(self.lower_bound)
        else:
            self._llb, self._ulb = (None, None)
        if self.upper_bound is not None:
            self._lub, self._uub = self._get_datetime_bounds(self.upper_bound)
        else:
            self._lub, self._uub = (None, None)
        # Generate the function to check if a value is within the range
        # The function is generated instead of defined to be able to optimize the check
        if self.lower_bound is not None and self.upper_bound is not None:
            if (
                self.lower_bound_censor == enum.ComparisonOperator.GTE
                and self.upper_bound_censor == enum.ComparisonOperator.ST
            ):

                def _match(value: str) -> bool:
                    l_value, u_value = PartialDateRangeFilter._get_datetime_bounds(
                        value
                    )
                    return self._llb <= l_value and u_value <= self._lub

            elif (
                self.lower_bound_censor == enum.ComparisonOperator.GTE
                and self.upper_bound_censor == enum.ComparisonOperator.STE
            ):

                def _match(value: str) -> bool:
                    l_value, u_value = PartialDateRangeFilter._get_datetime_bounds(
                        value
                    )
                    return self._llb <= l_value and u_value <= self._uub

            elif (
                self.lower_bound_censor == enum.ComparisonOperator.GT
                and self.upper_bound_censor == enum.ComparisonOperator.ST
            ):

                def _match(value: str) -> bool:
                    l_value, u_value = PartialDateRangeFilter._get_datetime_bounds(
                        value
                    )
                    return self._ulb <= l_value and u_value <= self._lub

            elif (
                self.lower_bound_censor == enum.ComparisonOperator.GT
                and self.upper_bound_censor == enum.ComparisonOperator.STE
            ):

                def _match(value: str) -> bool:
                    l_value, u_value = PartialDateRangeFilter._get_datetime_bounds(
                        value
                    )
                    return self._ulb <= l_value and u_value <= self._uub

        elif self.lower_bound is not None:
            if self.lower_bound_censor == enum.ComparisonOperator.GTE:

                def _match(value: str) -> bool:
                    l_value, _ = PartialDateRangeFilter._get_datetime_bounds(value)
                    return self._llb <= l_value

            elif self.lower_bound_censor == enum.ComparisonOperator.GT:

                def _match(value: str) -> bool:
                    l_value, _ = PartialDateRangeFilter._get_datetime_bounds(value)
                    return self._ulb <= l_value

        elif self.upper_bound is not None:
            if self.upper_bound_censor == enum.ComparisonOperator.ST:

                def _match(value: str) -> bool:
                    _, u_value = PartialDateRangeFilter._get_datetime_bounds(value)
                    return u_value <= self._lub

            elif self.upper_bound_censor == enum.ComparisonOperator.STE:

                def _match(value: str) -> bool:
                    _, u_value = PartialDateRangeFilter._get_datetime_bounds(value)
                    return u_value <= self._uub

        self._match = _match  # type: ignore
        return self


class TypedPartialDateRangeFilter(PartialDateRangeFilter):
    type: Literal[FilterType.PARTIAL_DATE_RANGE.value]
