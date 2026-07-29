from decimal import Decimal
from typing import Literal

from pydantic import Field

from gen_epix.filter.base import Filter
from gen_epix.filter.enum import FilterType


class NumberSetFilter(Filter):
    members: frozenset[int | float | Decimal] = Field(
        description="The numbers to match.", frozen=True
    )


class TypedNumberSetFilter(NumberSetFilter):
    type: Literal[FilterType.NUMBER_SET.value]
