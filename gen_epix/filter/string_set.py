import enum as _stdlib_enum
from typing import Any, Literal, Self

from pydantic import Field, PrivateAttr, model_validator

from gen_epix.filter.base import Filter
from gen_epix.filter.enum import FilterType


def _enum_to_str(x: Any) -> str:
    return x.name if isinstance(x, _stdlib_enum.Enum) else x


class StringSetFilter(Filter):
    members: frozenset[str] = Field(description="The strings to match.", frozen=True)
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
            self._match = lambda x: _enum_to_str(x) in self._members  # type: ignore
        else:
            self._match = lambda x: _enum_to_str(x).lower() in self._members  # type: ignore
        return self

    def _match(self, value: Any) -> bool:
        """Function is implemented dynamically in _validate_state"""
        raise NotImplementedError(
            "Method is implemented dynamically in _validate_state"
        )


class TypedStringSetFilter(StringSetFilter):
    type: Literal[FilterType.STRING_SET.value]
