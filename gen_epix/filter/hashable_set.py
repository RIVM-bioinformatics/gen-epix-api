from typing import Hashable

from pydantic import Field

from gen_epix.filter.base import Filter


class HashableSetFilter(Filter):
    members: frozenset[Hashable] = Field(
        default=None, description="The values to match.", frozen=True
    )

    def _match(self, value: Hashable) -> bool:
        return value in self.members


# No typed version of this filter is needed since the type of the values would be needed as well
# class TypedValueSetFilter(ValueSetFilter):
#     type_: Literal[FilterType.HASHABLE_SET]
