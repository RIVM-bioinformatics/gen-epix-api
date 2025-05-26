import re
from typing import Any, Literal, Self

from pydantic import Field, model_validator

from gen_epix.filter.base import Filter
from gen_epix.filter.enum import FilterType


class RegexFilter(Filter):
    pattern: str = Field(description="The regular expression to match.", frozen=True)

    @model_validator(mode="after")
    def _validate_state(self) -> Self:
        try:
            self._pattern = re.compile(self.pattern)
        except re.error as exc:
            raise AssertionError("Invalid regular expression.") from exc
        return self

    def _match(self, value: Any) -> bool:
        return self._pattern.match(value) is not None


class TypedRegexFilter(RegexFilter):
    type: Literal[FilterType.REGEX.value]
