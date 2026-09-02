"""In-process cache store with capacity management and expiry.

`MemoryBackend` is the default store: it holds envelopes in a dictionary,
enforces a weight budget through a pluggable `EvictionStrategy`, drops expired
entries lazily on access and eagerly on demand, and reports every removal with
its cause so that callers can keep a tag index or a metric in step.
"""

import threading
from collections.abc import Callable, Iterable, Iterator, Mapping

from gen_epix.fastapp.cache.backend.base import CacheBackend
from gen_epix.fastapp.cache.clock import Clock, SystemClock
from gen_epix.fastapp.cache.enum import EvictionPolicyType, RemovalCause
from gen_epix.fastapp.cache.eviction import EvictionStrategy, create_eviction_strategy
from gen_epix.fastapp.cache.exc import CacheConfigurationError
from gen_epix.fastapp.cache.lock import Mutex, ThreadMutex
from gen_epix.fastapp.cache.model import NO_VALUE, CachedValue, NoValue
from gen_epix.fastapp.cache.stats import CacheStatistics, InMemoryStatsRecorder

RemovalListener = Callable[[str, CachedValue, RemovalCause], None]
"""Callback receiving the key, envelope and reason of every removal."""


class MemoryBackend(CacheBackend):
    """Encapsulates storing envelopes in a dictionary bounded by a weight budget.

    Every mutation happens under one reentrant lock, which makes the store safe
    for concurrent use and lets the removal listener observe a consistent view.
    Expired entries are removed when they are next touched, so a region that
    stops reading a key still needs `expire` or eviction to reclaim its memory.

    Attributes:
        max_weight: Total weight the store may hold before evicting.
        clock: Time source used for expiry decisions.
        removal_listener: Optional callback invoked for every removal.
    """

    def __init__(
        self,
        max_weight: int = 1024,
        eviction: EvictionStrategy | EvictionPolicyType = EvictionPolicyType.LRU,
        clock: Clock | None = None,
        removal_listener: RemovalListener | None = None,
        name: str = "memory",
        record_statistics: bool = True,
    ):
        """Initialize a MemoryBackend instance.

        Args:
            max_weight: Total weight the store may hold.
            eviction: A strategy instance, or the policy to instantiate.
            clock: Time source, injectable for deterministic tests.
            removal_listener: Callback invoked for every removed entry.
            name: Identifier used in statistics and diagnostics.
            record_statistics: Whether to maintain hit and miss counters.

        Raises:
            CacheConfigurationError: If `max_weight` is not positive.
        """
        super().__init__(name)
        if max_weight <= 0:
            raise CacheConfigurationError("max_weight must be positive")
        self.max_weight = max_weight
        self.clock = clock if clock is not None else SystemClock()
        self.removal_listener = removal_listener
        self._eviction = (
            eviction
            if isinstance(eviction, EvictionStrategy)
            else create_eviction_strategy(eviction)
        )
        self._lock = threading.RLock()
        self._entries: dict[str, CachedValue] = {}
        self._weight = 0
        self._statistics = InMemoryStatsRecorder() if record_statistics else None

    @property
    def weight(self) -> int:
        """Return the total weight currently held."""
        with self._lock:
            return self._weight

    def __len__(self) -> int:
        """Return the number of entries currently held, including expired ones."""
        with self._lock:
            return len(self._entries)

    def get(self, key: str) -> CachedValue | NoValue:
        """See base method.

        An entry that passed its hard expiry is removed and reported as a miss.
        """
        now = self.clock.monotonic()
        with self._lock:
            entry = self._entries.get(key)
            if entry is None:
                self._record("misses")
                return NO_VALUE
            if entry.metadata.is_expired(now):
                self._remove(key, RemovalCause.EXPIRED)
                self._record("expirations")
                self._record("misses")
                return NO_VALUE
            self._eviction.record_access(key)
            self._record("hits")
            return entry

    def set(self, key: str, value: CachedValue) -> None:
        """See base method.

        Storing over an existing key reports the previous envelope as
        `REPLACED`. When the store exceeds its budget, entries are evicted and
        reported as `SIZE`; with an admission-aware strategy the incoming entry
        may itself be the one rejected.
        """
        with self._lock:
            previous = self._entries.get(key)
            if previous is not None:
                self._weight -= previous.metadata.weight
                self._notify(key, previous, RemovalCause.REPLACED)
            self._entries[key] = value
            self._weight += value.metadata.weight
            self._eviction.record_write(key, value.metadata.weight)
            self._record("sets")
            self._enforce_capacity(key)

    def delete(self, key: str) -> None:
        """See base method."""
        with self._lock:
            if key in self._entries:
                self._remove(key, RemovalCause.EXPLICIT)
                self._record("deletes")

    def delete_multi(self, keys: Iterable[str]) -> None:
        """See base method."""
        with self._lock:
            for key in list(keys):
                self.delete(key)

    def set_multi(self, mapping: Mapping[str, CachedValue]) -> None:
        """See base method."""
        with self._lock:
            for key, value in mapping.items():
                self.set(key, value)

    def clear(self) -> None:
        """See base method."""
        with self._lock:
            for key in list(self._entries):
                self._remove(key, RemovalCause.CLEARED)
            self._eviction.clear()
            self._weight = 0

    def contains(self, key: str) -> bool:
        """See base method."""
        now = self.clock.monotonic()
        with self._lock:
            entry = self._entries.get(key)
            return entry is not None and not entry.metadata.is_expired(now)

    def keys(self) -> Iterator[str]:
        """See base method.

        The snapshot is taken under the lock, so iteration is safe while other
        threads mutate the store, but it may include keys removed since.
        """
        with self._lock:
            return iter(list(self._entries))

    def expire(self) -> list[str]:
        """Remove every entry that passed its hard expiry.

        Lazy expiry only reclaims memory for keys that are read again, so a
        long-lived process should call this periodically.

        Returns:
            The keys that were removed.
        """
        now = self.clock.monotonic()
        with self._lock:
            expired = [
                key
                for key, entry in self._entries.items()
                if entry.metadata.is_expired(now)
            ]
            for key in expired:
                self._remove(key, RemovalCause.EXPIRED)
                self._record("expirations")
            return expired

    def get_mutex(self, key: str) -> Mutex | None:
        """See base method.

        A process-local store needs no distributed mutex, so a plain thread
        lock is returned and regeneration is coordinated per process.
        """
        return ThreadMutex()

    def statistics(self) -> CacheStatistics:
        """See base method."""
        if self._statistics is None:
            return CacheStatistics()
        return self._statistics.snapshot()

    def close(self) -> None:
        """See base method."""
        self.clear()

    def _enforce_capacity(self, candidate: str) -> None:
        """Evict entries until the weight budget is met.

        Args:
            candidate: The key that was just written, offered to the strategy
                for an admission decision against each nominated victim.
        """
        while self._weight > self.max_weight:
            victim = self._eviction.victim()
            if victim is None:
                return
            if victim != candidate and not self._eviction.admit(candidate, victim):
                self._remove(candidate, RemovalCause.SIZE)
                self._record("evictions")
                return
            self._remove(victim, RemovalCause.SIZE)
            self._record("evictions")

    def _remove(self, key: str, cause: RemovalCause) -> None:
        """Drop one entry and report it, assuming the lock is held.

        Args:
            key: The key to remove.
            cause: Why the entry is leaving.
        """
        entry = self._entries.pop(key, None)
        if entry is None:
            return
        self._weight -= entry.metadata.weight
        self._eviction.record_removal(key)
        self._notify(key, entry, cause)

    def _notify(self, key: str, entry: CachedValue, cause: RemovalCause) -> None:
        """Invoke the removal listener, absorbing its failures.

        Args:
            key: The removed key.
            entry: The removed envelope.
            cause: Why the entry left.
        """
        if self.removal_listener is None:
            return
        try:
            self.removal_listener(key, entry, cause)
        except Exception:  # noqa: BLE001 - a listener must not break the store
            return

    def _record(self, field: str, amount: float = 1) -> None:
        """Increment one statistics counter when statistics are enabled."""
        if self._statistics is not None:
            self._statistics.record(field, amount)
