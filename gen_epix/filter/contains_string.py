"""String equality filter models."""

from typing import Any, Literal

from pydantic import Field

from gen_epix.filter.base import Filter
from gen_epix.filter.enum import FilterType


class ContainsStringFilter(Filter):
    """Represents a filter matching a substring within a string value."""

    type: Literal[FilterType.CONTAINS_STRING.value] = FilterType.CONTAINS_STRING.value  # type: ignore[name-defined]

    value: str = Field(description="The substring to match.", frozen=True, min_length=1)

    def _match(self, value: Any) -> bool:
        """Return whether a value contains the configured value as a substring."""
        is_match: bool = self.value in value
        return is_match
