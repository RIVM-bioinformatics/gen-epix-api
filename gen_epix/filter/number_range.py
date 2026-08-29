"""Numeric range filter models."""

from decimal import Decimal
from typing import Annotated, Literal

from pydantic import Field, WithJsonSchema

from gen_epix.filter.enum import FilterType
from gen_epix.filter.range import RangeFilter


class NumberRangeFilter(RangeFilter):
    """Match numeric values within the configured range."""
    lower_bound: (
        Annotated[
            int | float | Decimal,
            WithJsonSchema({"type": "number"}),
        ]
        | None
    ) = Field(default=None, description="The lower bound of the range.", frozen=True)
    upper_bound: (
        Annotated[
            int | float | Decimal,
            WithJsonSchema({"type": "number"}),
        ]
        | None
    ) = Field(default=None, description="The upper bound of the range.", frozen=True)


class TypedNumberRangeFilter(NumberRangeFilter):
    """Numeric range filter carrying its serialized filter type."""
    type: Literal[FilterType.NUMBER_RANGE.value]  # type: ignore[name-defined]
