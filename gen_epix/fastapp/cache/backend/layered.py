"""A near cache in front of a shared store.

`LayeredBackend` reads from a fast process-local tier and falls back to a shared
tier, promoting what it finds. This removes most of the network round trips of a
remote cache, but it introduces the coherence problem that defines hybrid
caching: a deletion performed by one process leaves every other process serving
its own stale near copy. The class therefore exposes `invalidate_near`, which an
invalidation bus calls on every process when a key changes anywhere.
"""

from collections.abc import Iterable, Iterator, Mapping

from gen_epix.fastapp.cache.backend.base import CacheBackend
from gen_epix.fastapp.cache.lock import Mutex
from gen_epix.fastapp.cache.model import NO_VALUE, CachedValue, NoValue
from gen_epix.fastapp.cache.stats import CacheStatistics


class LayeredBackend(CacheBackend):
    """Encapsulates combining a local near tier with a shared remote tier.

    Reads consult the near tier first and promote a remote hit into it. Writes
    and deletions are applied to both tiers, near tier first on deletion so
    that a failure of the shared tier cannot leave a stale local copy behind.

    Attributes:
        near: The fast process-local tier.
        remote: The shared tier.
        promote: Whether a remote hit is copied into the near tier.
    """

    def __init__(
        self,
        near: CacheBackend,
        remote: CacheBackend,
        promote: bool = True,
        name: str = "layered",
    ):
        """Initialize a LayeredBackend instance."""
        super().__init__(name)
        self.near = near
        self.remote = remote
        self.promote = promote

    def get(self, key: str) -> CachedValue | NoValue:
        """See base method."""
        value = self.near.get(key)
        if value is not NO_VALUE:
            return value
        value = self.remote.get(key)
        if value is not NO_VALUE and self.promote:
            self.near.set(key, value)
        return value

    def get_multi(self, keys: Iterable[str]) -> list[CachedValue | NoValue]:
        """See base method.

        Only the keys missing from the near tier are requested remotely, so a
        partially warm batch costs one round trip for the remainder.
        """
        ordered = list(keys)
        results = self.near.get_multi(ordered)
        missing = [
            (index, key)
            for index, (key, value) in enumerate(zip(ordered, results, strict=True))
            if value is NO_VALUE
        ]
        if not missing:
            return results
        remote_values = self.remote.get_multi([key for _, key in missing])
        for (index, key), value in zip(missing, remote_values, strict=True):
            results[index] = value
            if value is not NO_VALUE and self.promote:
                self.near.set(key, value)
        return results

    def set(self, key: str, value: CachedValue) -> None:
        """See base method."""
        self.remote.set(key, value)
        self.near.set(key, value)

    def set_multi(self, mapping: Mapping[str, CachedValue]) -> None:
        """See base method."""
        self.remote.set_multi(mapping)
        self.near.set_multi(mapping)

    def delete(self, key: str) -> None:
        """See base method."""
        self.near.delete(key)
        self.remote.delete(key)

    def delete_multi(self, keys: Iterable[str]) -> None:
        """See base method."""
        ordered = list(keys)
        self.near.delete_multi(ordered)
        self.remote.delete_multi(ordered)

    def clear(self) -> None:
        """See base method."""
        self.near.clear()
        self.remote.clear()

    def contains(self, key: str) -> bool:
        """See base method."""
        return self.near.contains(key) or self.remote.contains(key)

    def keys(self) -> Iterator[str]:
        """See base method.

        Only the shared tier is enumerated, because it is the authoritative one
        and the near tier holds a subset.
        """
        return self.remote.keys()

    def get_mutex(self, key: str) -> Mutex | None:
        """See base method.

        The shared tier is asked first, because only a mutex it provides can
        coordinate regeneration across processes.
        """
        return self.remote.get_mutex(key) or self.near.get_mutex(key)

    def invalidate_near(self, key: str) -> None:
        """Drop one key from the local tier only.

        An invalidation bus calls this on every process after any process has
        changed the underlying data, so that near copies do not outlive the
        shared entry.

        Args:
            key: The fully composed cache key.
        """
        self.near.delete(key)

    def clear_near(self) -> None:
        """Drop every entry from the local tier only."""
        self.near.clear()

    def statistics(self) -> CacheStatistics:
        """See base method.

        The tiers are summed, so `hits` counts near and remote hits together
        while the near tier's own counters remain available on `near`.
        """
        return self.near.statistics() + self.remote.statistics()

    def close(self) -> None:
        """See base method."""
        self.near.close()
        self.remote.close()
