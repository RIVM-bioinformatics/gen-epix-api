"""UUID set-membership filter models."""

from typing import Any, Literal, Self
from uuid import UUID

from pydantic import Field, model_validator

from gen_epix.filter.base import Filter
from gen_epix.filter.enum import FilterType


class UuidSetFilter(Filter):
    """Represents a filter matching UUID values in an immutable set.

    Model validation:
    Initializes a direct UUID membership matcher.
    """

    members: frozenset[UUID] = Field(description="The UUIDs to match.", frozen=True)

    @model_validator(mode="after")
    def _validate_state(self) -> Self:
        """Build the optimized UUID membership matcher."""
        self._match = lambda x: x in self.members  # type: ignore
        return self

    def _match(self, value: Any) -> bool:
        """Match a value using the function generated during validation.

        Args:
            value: The UUID value to match.

        Returns:
            Whether the value belongs to the configured set.

        Raises:
            NotImplementedError: Always, until model validation supplies the function.
        """
        raise NotImplementedError(
            "Method is implemented dynamically in _validate_state"
        )


class TypedUuidSetFilter(UuidSetFilter):
    """Represents a UUID set filter carrying its serialized filter type."""

    type: Literal[FilterType.UUID_SET.value]  # type: ignore[name-defined]
