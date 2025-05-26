from decimal import Decimal
from typing import Literal

from pydantic import Field

from gen_epix.filter.enum import FilterType
from gen_epix.filter.equals import EqualsFilter


class EqualsNumberFilter(EqualsFilter):
    value: int | float | Decimal = Field(
        description="The number to match.", frozen=True
    )


class TypedEqualsNumberFilter(EqualsNumberFilter):
    type: Literal[FilterType.EQUALS_NUMBER.value]
