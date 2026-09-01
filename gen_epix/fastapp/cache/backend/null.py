"""A store that never caches.

`NullBackend` turns a region into a pass-through. It exists so that caching can
be switched off per environment through configuration alone, and so that a test
suite can be run twice, cached and uncached, to prove that no behavior depends
on a cache hit.
"""

from collections.abc import Iterable, Iterator, Mapping

from gen_epix.fastapp.cache.backend.base import CacheBackend
from gen_epix.fastapp.cache.model import NO_VALUE, CachedValue, NoValue


class NullBackend(CacheBackend):
    """Accept every write, report every read as a miss."""

    def __init__(self, name: str = "null"):
        """Initialize a NullBackend instance."""
        super().__init__(name)

    def get(self, key: str) -> CachedValue | NoValue:
        """See base method."""
        return NO_VALUE

    def get_multi(self, keys: Iterable[str]) -> list[CachedValue | NoValue]:
        """See base method."""
        return [NO_VALUE for _ in keys]

    def set(self, key: str, value: CachedValue) -> None:
        """See base method."""

    def set_multi(self, mapping: Mapping[str, CachedValue]) -> None:
        """See base method."""

    def delete(self, key: str) -> None:
        """See base method."""

    def delete_multi(self, keys: Iterable[str]) -> None:
        """See base method."""

    def clear(self) -> None:
        """See base method."""

    def contains(self, key: str) -> bool:
        """See base method."""
        return False

    def keys(self) -> Iterator[str]:
        """See base method."""
        return iter(())
