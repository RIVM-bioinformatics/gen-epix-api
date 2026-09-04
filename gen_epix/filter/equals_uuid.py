"""UUID equality filter models."""

from typing import Literal
from uuid import UUID

from pydantic import Field

from gen_epix.filter.enum import FilterType
from gen_epix.filter.equals import EqualsFilter


class EqualsUuidFilter(EqualsFilter):
    """Represents a filter matching a UUID value."""

    type: Literal[FilterType.EQUALS_UUID.value] = FilterType.EQUALS_UUID.value  # type: ignore[name-defined]

    value: UUID = Field(description="The UUID to match.", frozen=True)
