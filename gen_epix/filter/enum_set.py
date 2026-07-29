from enum import Enum
from typing import Any, Literal

from pydantic import Field

from gen_epix.filter.base import Filter
from gen_epix.filter.enum import FilterType


def _enum_to_str(x: Any) -> str:
    return x.name if isinstance(x, Enum) else x


class EnumSetFilter(Filter):
    members: frozenset[Enum] = Field(description="The enums to match.", frozen=True)


class TypedEnumSetFilter(EnumSetFilter):
    type: Literal[FilterType.ENUM_SET.value]
