from typing import Any, Literal, Self

from pydantic import Field, PrivateAttr, model_validator

from gen_epix.filter.base import Filter
from gen_epix.filter.enum import FilterType


class StringSetFilter(Filter):
    members: frozenset[str] = Field(
        default=None, description="The strings to match.", frozen=True
    )
    case_sensitive: bool = Field(
        default=False, description="Whether the match is case sensitive.", frozen=True
    )
    _members: frozenset[str] = PrivateAttr()

    @model_validator(mode="after")
    def _validate_state(self) -> Self:
        if not self.case_sensitive:
            self._members = frozenset({x.lower() for x in self.members})
        else:
            self._members = self.members
        # Generate the function to check if a value is in the set of terms
        # The function is generated instead of defined to be able to optimize the check
        if self.case_sensitive:
            self._match = lambda x: x in self._members  # type: ignore
        else:
            self._match = lambda x: x.lower() in self._members  # type: ignore
        return self

    def _match(self, value: Any) -> bool:
        # Function is implemented dynamically in _validate_state
        raise NotImplementedError()


class TypedStringSetFilter(StringSetFilter):
    type: Literal[FilterType.STRING_SET.value]
