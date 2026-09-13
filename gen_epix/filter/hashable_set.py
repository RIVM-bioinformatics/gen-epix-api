"""Filter implementation for membership in a hashable value set."""

from collections.abc import Hashable

from pydantic import Field

from gen_epix.filter.base import Filter


class HashableSetFilter(Filter):
    """Represents a filter matching values in an immutable set of hashable members."""

    members: frozenset[Hashable] = Field(
        description="The values to match.", frozen=True
    )

    def _match(self, value: Hashable) -> bool:
        """Return whether a value is a configured set member."""
        return value in self.members


# No typed version of this filter is needed since the type of the values would be needed as well
# HashableSetFilter intentionally inherits Filter's BASE discriminator.
