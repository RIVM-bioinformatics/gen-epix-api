"""String set-membership filters with optional case normalization."""

import enum as _stdlib_enum
from typing import Any, Literal, Self

from pydantic import Field, PrivateAttr, model_validator

from gen_epix.filter.base import Filter
from gen_epix.filter.enum import FilterType


def _enum_to_str(x: Any) -> str:
    """Return an enum member name or the supplied string-like value."""
    return x.name if isinstance(x, _stdlib_enum.Enum) else x


class StringSetFilter(Filter):
    """Represents a filter matching strings with optional case sensitivity.

    Model validation:
    Case-insensitive members and matched enum names are normalized to lowercase
    before membership is evaluated.
    """

    members: frozenset[str] = Field(description="The strings to match.", frozen=True)
    case_sensitive: bool = Field(
        default=False, description="Whether the match is case sensitive.", frozen=True
    )
    _members: frozenset[str] = PrivateAttr()

    @model_validator(mode="after")
    def _validate_state(self) -> Self:
        """Normalize members and build the optimized membership matcher."""
        if not self.case_sensitive:
            self._members = frozenset({x.lower() for x in self.members})
        else:
            self._members = self.members
        # Generate the function to check if a value is in the set of terms
        # The function is generated instead of defined to be able to optimize the check
        if self.case_sensitive:
            self._match = lambda x: _enum_to_str(x) in self._members  # type: ignore
        else:
            self._match = lambda x: _enum_to_str(x).lower() in self._members  # type: ignore
        return self

    def _match(self, value: Any) -> bool:
        """Match a value using the function generated during validation.

        Args:
            value: The string-like value to match.

        Returns:
            Whether the value belongs to the configured set.

        Raises:
            NotImplementedError: Always, until model validation supplies the function.
        """
        raise NotImplementedError(
            "Method is implemented dynamically in _validate_state"
        )


class TypedStringSetFilter(StringSetFilter):
    """Represents a string set filter carrying its serialized filter type."""

    type: Literal[FilterType.STRING_SET.value]  # type: ignore[name-defined]
