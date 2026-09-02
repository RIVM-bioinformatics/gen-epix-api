"""Date-valued inclusive and exclusive range filters."""

import datetime
from typing import Literal

from pydantic import Field

from gen_epix.filter.enum import FilterType
from gen_epix.filter.range import RangeFilter


class DateRangeFilter(RangeFilter):
    """Represents a filter matching dates within the configured bounds."""

    lower_bound: datetime.date | None = Field(
        default=None, description="The lower bound of the range.", frozen=True
    )
    upper_bound: datetime.date | None = Field(
        default=None, description="The upper bound of the range.", frozen=True
    )


class TypedDateRangeFilter(DateRangeFilter):
    """Represents a date range filter carrying its serialized filter type."""

    type: Literal[FilterType.DATE_RANGE.value]  # type: ignore[name-defined]
