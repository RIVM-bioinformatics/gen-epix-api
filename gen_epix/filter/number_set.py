"""Numeric set-membership filter models."""

from decimal import Decimal
from typing import Literal

from pydantic import Field

from gen_epix.filter.enum import FilterType
from gen_epix.filter.hashable_set import HashableSetFilter


class NumberSetFilter(HashableSetFilter):
    """Match numeric values contained in an immutable set."""

    members: frozenset[int | float | Decimal] = Field(
        description="The numbers to match.", frozen=True
    )


class TypedNumberSetFilter(NumberSetFilter):
    """Numeric set filter carrying its serialized filter type."""

    type: Literal[FilterType.NUMBER_SET.value]  # type: ignore[name-defined]
