from decimal import Decimal
from typing import Literal

from pydantic import Field

from gen_epix.filter.enum import FilterType
from gen_epix.filter.hashable_set import HashableSetFilter


class NumberSetFilter(HashableSetFilter):
    members: frozenset[int | float | Decimal] = Field(
        default=None, description="The numbers to match.", frozen=True
    )


class TypedNumberSetFilter(NumberSetFilter):
    type: Literal[FilterType.NUMBER_SET.value]
