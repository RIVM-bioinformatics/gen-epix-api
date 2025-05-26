import datetime
from typing import Literal

from pydantic import Field

from gen_epix.filter.enum import FilterType
from gen_epix.filter.range import RangeFilter


class DatetimeRangeFilter(RangeFilter):
    lower_bound: datetime.datetime = Field(
        default=None, description="The lower bound of the range.", frozen=True
    )
    upper_bound: datetime.datetime = Field(
        default=None, description="The upper bound of the range.", frozen=True
    )


class TypedDatetimeRangeFilter(DatetimeRangeFilter):
    type: Literal[FilterType.DATETIME_RANGE.value]
