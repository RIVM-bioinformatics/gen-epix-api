"""String equality filter models."""

from typing import Literal

from pydantic import Field

from gen_epix.filter.enum import FilterType
from gen_epix.filter.equals import EqualsFilter


class EqualsStringFilter(EqualsFilter):
    """Represents a filter matching a string value."""

    value: str = Field(description="The string to match.", frozen=True)


class TypedEqualsStringFilter(EqualsStringFilter):
    """Represents a string equality filter carrying its serialized filter type."""

    type: Literal[FilterType.EQUALS_STRING.value]  # type: ignore[name-defined]
