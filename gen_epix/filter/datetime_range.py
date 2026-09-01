"""Datetime-valued inclusive and exclusive range filters."""

import datetime
from typing import Literal

from pydantic import Field

from gen_epix.filter.enum import FilterType
from gen_epix.filter.range import RangeFilter


class DatetimeRangeFilter(RangeFilter):
    """Match datetimes within the configured lower and upper bounds."""

    lower_bound: datetime.datetime | None = Field(
        default=None, description="The lower bound of the range.", frozen=True
    )
    upper_bound: datetime.datetime | None = Field(
        default=None, description="The upper bound of the range.", frozen=True
    )


class TypedDatetimeRangeFilter(DatetimeRangeFilter):
    """Datetime range filter carrying its serialized filter type."""

    type: Literal[FilterType.DATETIME_RANGE.value]  # type: ignore[name-defined]
