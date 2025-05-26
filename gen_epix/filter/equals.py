from typing import Any

from pydantic import Field

from gen_epix.filter.base import Filter


class EqualsFilter(Filter):
    value: Any = Field(default=None, description="The value to match.", frozen=True)

    def _match(self, value: Any) -> bool:
        is_match: bool = value == self.value
        return is_match


# No typed version of this filter is needed since the type of the values would be needed as well
