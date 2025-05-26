from typing import Literal
from uuid import UUID

from pydantic import Field

from gen_epix.filter.enum import FilterType
from gen_epix.filter.equals import EqualsFilter


class EqualsUuidFilter(EqualsFilter):
    value: UUID = Field(description="The UUID to match.", frozen=True)


class TypedEqualsUuidFilter(EqualsUuidFilter):
    type: Literal[FilterType.EQUALS_UUID.value]
