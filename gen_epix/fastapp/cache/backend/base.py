"""Abstract cache store contract.

A backend is a dumb key-to-envelope store. It enforces capacity and, where it
can, expiry, but it never interprets tags, generations, scopes or staleness:
those belong to `CacheRegion`. Keeping the contract narrow is what allows an
in-memory store, a null store and a layered near cache to be substituted for
one another without changing behavior.
"""

from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator, Mapping

from gen_epix.fastapp.cache.lock import Mutex
from gen_epix.fastapp.cache.model import CachedValue, NoValue
from gen_epix.fastapp.cache.stats import CacheStatistics


class CacheBackend(ABC):
    """Encapsulates storing cache envelopes under string keys.

    Implementations must be safe for concurrent use and must treat `delete` and
    `clear` as idempotent. Multi-key operations have working defaults expressed
    in terms of the single-key ones; override them where the store supports a
    batch round trip.

    Attributes:
        name: Identifier used in statistics and diagnostics.
    """

    def __init__(self, name: str = "backend"):
        """Initialize a CacheBackend instance."""
        self.name = name

    @abstractmethod
    def get(self, key: str) -> CachedValue | NoValue:
        """Return the envelope stored under `key`, or `NO_VALUE`.

        Args:
            key: The fully composed cache key.
        """

    @abstractmethod
    def set(self, key: str, value: CachedValue) -> None:
        """Store `value` under `key`, replacing any previous entry.

        Args:
            key: The fully composed cache key.
            value: The envelope to store.
        """

    @abstractmethod
    def delete(self, key: str) -> None:
        """Remove `key` if present.

        Args:
            key: The fully composed cache key.
        """

    @abstractmethod
    def clear(self) -> None:
        """Remove every entry."""

    @abstractmethod
    def contains(self, key: str) -> bool:
        """Return whether an unexpired entry exists for `key`."""

    @abstractmethod
    def keys(self) -> Iterator[str]:
        """Yield the keys currently stored.

        A store that cannot enumerate its keys yields nothing, in which case
        callers must invalidate by tag or by generation instead of by scan.
        """

    def get_multi(self, keys: Iterable[str]) -> list[CachedValue | NoValue]:
        """Return the envelopes for `keys` in the order given.

        Args:
            keys: The fully composed cache keys.

        Returns:
            One entry per key, using `NO_VALUE` for the keys that are absent.
        """
        return [self.get(key) for key in keys]

    def set_multi(self, mapping: Mapping[str, CachedValue]) -> None:
        """Store several envelopes.

        Args:
            mapping: Keys and the envelopes to store under them. The mapping is
                not modified.
        """
        for key, value in mapping.items():
            self.set(key, value)

    def delete_multi(self, keys: Iterable[str]) -> None:
        """Remove several keys, ignoring the absent ones.

        Args:
            keys: The fully composed cache keys.
        """
        for key in keys:
            self.delete(key)

    def get_mutex(self, key: str) -> Mutex | None:
        """Return a store-provided mutex for regenerating `key`.

        Returns:
            A mutex when the store offers one, otherwise None. A region that
            receives None coordinates with a process-local lock, which is
            sufficient for a process-local store but not for a shared one.
        """
        return None

    def statistics(self) -> CacheStatistics:
        """Return the counters observed by this store."""
        return CacheStatistics()

    def close(self) -> None:
        """Release the resources held by the store."""


class ProxyBackend(CacheBackend):
    """Encapsulates altering the behavior of another backend without subclassing it.

    Proxies stack, so cross-cutting concerns such as logging, metrics or key
    rewriting can be composed independently of the store. Every method
    delegates by default; override only what changes.

    Attributes:
        proxied: The wrapped backend.
    """

    def __init__(self, proxied: CacheBackend | None = None, name: str = "proxy"):
        """Initialize a ProxyBackend instance."""
        super().__init__(name)
        self._proxied = proxied

    @property
    def proxied(self) -> CacheBackend:
        """Return the wrapped backend.

        Returns:
            The backend this proxy delegates to.

        Raises:
            RuntimeError: If the proxy was created without a backend and
                `wrap` has not been called yet.
        """
        if self._proxied is None:
            raise RuntimeError(f"Proxy backend {self.name} wraps nothing yet")
        return self._proxied

    def wrap(self, backend: CacheBackend) -> "ProxyBackend":
        """Attach a backend and return this proxy for chaining.

        Args:
            backend: The backend to delegate to.
        """
        self._proxied = backend
        return self

    def get(self, key: str) -> CachedValue | NoValue:
        """See base method."""
        return self.proxied.get(key)

    def set(self, key: str, value: CachedValue) -> None:
        """See base method."""
        self.proxied.set(key, value)

    def delete(self, key: str) -> None:
        """See base method."""
        self.proxied.delete(key)

    def clear(self) -> None:
        """See base method."""
        self.proxied.clear()

    def contains(self, key: str) -> bool:
        """See base method."""
        return self.proxied.contains(key)

    def keys(self) -> Iterator[str]:
        """See base method."""
        return self.proxied.keys()

    def get_multi(self, keys: Iterable[str]) -> list[CachedValue | NoValue]:
        """See base method."""
        return self.proxied.get_multi(keys)

    def set_multi(self, mapping: Mapping[str, CachedValue]) -> None:
        """See base method."""
        self.proxied.set_multi(mapping)

    def delete_multi(self, keys: Iterable[str]) -> None:
        """See base method."""
        self.proxied.delete_multi(keys)

    def get_mutex(self, key: str) -> Mutex | None:
        """See base method."""
        return self.proxied.get_mutex(key)

    def statistics(self) -> CacheStatistics:
        """See base method."""
        return self.proxied.statistics()

    def close(self) -> None:
        """See base method."""
        self.proxied.close()


__all__ = ["CacheBackend", "ProxyBackend"]
