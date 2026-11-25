"""Boolean equality filter models."""

from typing import Any, Literal

from pydantic import Field

from gen_epix.filter.enum import FilterType
from gen_epix.filter.equals import EqualsFilter


class EqualsBooleanFilter(EqualsFilter):
    """Represents a filter matching a boolean value."""

    type: Literal[FilterType.EQUALS_BOOLEAN.value] = FilterType.EQUALS_BOOLEAN.value  # type: ignore[name-defined]

    value: bool = Field(description="The boolean value to match.", frozen=True)

    def _match(self, value: Any) -> bool:
        """Match only boolean candidates, avoiding Python's bool/int equality."""
        return isinstance(value, bool) and value is self.value
