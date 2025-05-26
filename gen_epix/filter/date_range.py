import datetime
from typing import Literal

from pydantic import Field

from gen_epix.filter.enum import FilterType
from gen_epix.filter.range import RangeFilter


class DateRangeFilter(RangeFilter):
    lower_bound: datetime.date = Field(
        default=None, description="The lower bound of the range.", frozen=True
    )
    upper_bound: datetime.date = Field(
        default=None, description="The upper bound of the range.", frozen=True
    )


class TypedDateRangeFilter(DateRangeFilter):
    type: Literal[FilterType.DATE_RANGE.value]
