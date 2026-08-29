"""UUID set-membership filter models."""

from typing import Any, Literal, Self
from uuid import UUID

from pydantic import Field, model_validator

from gen_epix.filter.base import Filter
from gen_epix.filter.enum import FilterType


class UuidSetFilter(Filter):
    """Match UUID values contained in an immutable set."""
    members: frozenset[UUID] = Field(description="The UUIDs to match.", frozen=True)

    @model_validator(mode="after")
    def _validate_state(self) -> Self:
        """Build the optimized UUID membership matcher."""
        self._match = lambda x: x in self.members  # type: ignore
        return self

    def _match(self, value: Any) -> bool:
        """Match a value using the function generated during validation."""
        raise NotImplementedError(
            "Method is implemented dynamically in _validate_state"
        )


class TypedUuidSetFilter(UuidSetFilter):
    """UUID set filter carrying its serialized filter type."""
    type: Literal[FilterType.UUID_SET.value]  # type: ignore[name-defined]
