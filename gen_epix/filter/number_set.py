"""Define NumberSetFilter for membership in numeric value sets.

NumberSetFilter specializes HashableSetFilter with integer, float, and Decimal
members while retaining the shared Filter matching interface.
"""

from decimal import Decimal
from typing import Literal

from pydantic import Field

from gen_epix.filter.enum import FilterType
from gen_epix.filter.hashable_set import HashableSetFilter


class NumberSetFilter(HashableSetFilter):
    """Represents a filter matching numeric values in an immutable set."""

    type: Literal[FilterType.NUMBER_SET.value] = FilterType.NUMBER_SET.value  # type: ignore[name-defined]

    members: frozenset[int | float | Decimal] = Field(
        description="The numbers to match.", frozen=True
    )
