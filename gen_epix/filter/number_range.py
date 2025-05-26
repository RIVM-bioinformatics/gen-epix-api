from decimal import Decimal
from typing import Annotated, Literal

from pydantic import Field, WithJsonSchema

from gen_epix.filter.enum import FilterType
from gen_epix.filter.range import RangeFilter


class NumberRangeFilter(RangeFilter):
    lower_bound: Annotated[
        int | float | Decimal,
        WithJsonSchema({"type": "number"}),
    ] = Field(default=None, description="The lower bound of the range.", frozen=True)
    upper_bound: Annotated[
        int | float | Decimal,
        WithJsonSchema({"type": "number"}),
    ] = Field(default=None, description="The upper bound of the range.", frozen=True)


class TypedNumberRangeFilter(NumberRangeFilter):
    type: Literal[FilterType.NUMBER_RANGE.value]
