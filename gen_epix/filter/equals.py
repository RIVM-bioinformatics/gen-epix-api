"""Provide generic value equality filtering through the shared Filter API.

EqualsFilter defines scalar equality matching and inherits column and row
filtering behavior from Filter.
"""

from typing import Any

from pydantic import Field

from gen_epix.filter.base import Filter


class EqualsFilter(Filter):
    """Represents a filter matching values equal to the configured value."""

    value: Any = Field(default=None, description="The value to match.", frozen=True)

    def _match(self, value: Any) -> bool:
        """Return whether a value equals the configured value."""
        is_match: bool = value == self.value
        return is_match


# No typed version of this filter is needed since the type of the values would be needed as well
