from typing import Literal

from pydantic import Field

from gen_epix.filter.enum import FilterType
from gen_epix.filter.equals import EqualsFilter


class EqualsStringFilter(EqualsFilter):
    value: str = Field(description="The string to match.", frozen=True)


class TypedEqualsStringFilter(EqualsStringFilter):
    type: Literal[FilterType.EQUALS_STRING.value]
