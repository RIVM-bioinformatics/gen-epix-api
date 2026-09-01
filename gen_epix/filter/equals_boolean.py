"""Boolean equality filter models."""

from typing import Literal

from pydantic import Field

from gen_epix.filter.enum import FilterType
from gen_epix.filter.equals import EqualsFilter


class EqualsBooleanFilter(EqualsFilter):
    """Match a boolean value."""

    value: bool = Field(description="The boolean value to match.", frozen=True)


class TypedEqualsBooleanFilter(EqualsBooleanFilter):
    """Boolean equality filter carrying its serialized filter type."""

    type: Literal[FilterType.EQUALS_BOOLEAN.value]  # type: ignore[name-defined]
