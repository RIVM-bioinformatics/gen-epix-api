"""Numeric equality filter models."""

from decimal import Decimal
from typing import Literal

from pydantic import Field

from gen_epix.filter.enum import FilterType
from gen_epix.filter.equals import EqualsFilter


class EqualsNumberFilter(EqualsFilter):
    """Represents a filter matching an integer, floating-point, or decimal value."""

    type: Literal[FilterType.EQUALS_NUMBER.value] = FilterType.EQUALS_NUMBER.value  # type: ignore[name-defined]

    value: int | float | Decimal = Field(
        description="The number to match.", frozen=True
    )
