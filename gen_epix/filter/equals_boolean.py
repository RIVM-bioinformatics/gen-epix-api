"""Boolean equality filter models."""

from typing import Literal

from pydantic import Field

from gen_epix.filter.enum import FilterType
from gen_epix.filter.equals import EqualsFilter


# TODO: LSP-3893 Expected: reject integer candidate 1; actual: it matches value=True
# through inherited Python equality. Confirm whether boolean filters may support 0/1.
class EqualsBooleanFilter(EqualsFilter):
    """Represents a filter matching a boolean value."""

    type: Literal[FilterType.EQUALS_BOOLEAN.value] = FilterType.EQUALS_BOOLEAN.value  # type: ignore[name-defined]

    value: bool = Field(description="The boolean value to match.", frozen=True)
