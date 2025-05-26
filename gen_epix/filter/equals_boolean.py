from typing import Literal

from pydantic import Field

from gen_epix.filter.enum import FilterType
from gen_epix.filter.equals import EqualsFilter


class EqualsBooleanFilter(EqualsFilter):
    value: bool = Field(description="The boolean value to match.", frozen=True)


class TypedEqualsBooleanFilter(EqualsBooleanFilter):
    type: Literal[FilterType.EQUALS_BOOLEAN.value]
