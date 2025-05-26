from typing import Any, Literal, Self
from uuid import UUID

from pydantic import Field, model_validator

from gen_epix.filter.base import Filter
from gen_epix.filter.enum import FilterType


class UuidSetFilter(Filter):
    members: frozenset[UUID] = Field(
        default=None, description="The UUIDs to match.", frozen=True
    )

    @model_validator(mode="after")
    def _validate_state(self) -> Self:
        self._match = lambda x: x in self.members  # type: ignore
        return self

    def _match(self, value: Any) -> bool:
        # Function is implemented dynamically in _validate_state
        raise NotImplementedError()


class TypedUuidSetFilter(UuidSetFilter):
    type: Literal[FilterType.UUID_SET.value]
