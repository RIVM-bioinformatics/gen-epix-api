"""Eviction strategies that choose which entry leaves a full cache.

A strategy observes writes, reads and removals and, when the backend is over
budget, nominates a victim. `TinyLFUEviction` additionally implements
admission: a newly loaded key that is less popular than the current victim is
refused, which keeps a scan of one-shot keys from flushing a hot working set.
"""

import random
from abc import ABC, abstractmethod
from collections import OrderedDict
from collections.abc import Iterator

from gen_epix.fastapp.cache.enum import EvictionPolicyType
from gen_epix.fastapp.cache.exc import CacheConfigurationError


class EvictionStrategy(ABC):
    """Encapsulates tracking access order or frequency and nominate eviction victims.

    A backend calls `record_write` for every stored entry, `record_access` for
    every hit and `record_removal` whenever an entry leaves, then asks for a
    `victim` while it is over its capacity budget. Implementations are not
    thread safe; the backend serializes calls.
    """

    @abstractmethod
    def record_write(self, key: str, weight: int = 1) -> None:
        """Register that `key` was stored or replaced.

        Args:
            key: The stored key.
            weight: The capacity cost of the entry, for strategies that use it.
        """

    @abstractmethod
    def record_access(self, key: str) -> None:
        """Register a cache hit on `key`."""

    @abstractmethod
    def record_removal(self, key: str) -> None:
        """Register that `key` no longer exists in the backend."""

    @abstractmethod
    def victim(self) -> str | None:
        """Return the key that should be evicted next, or None when empty."""

    @abstractmethod
    def clear(self) -> None:
        """Forget all bookkeeping."""

    def admit(self, candidate: str, victim: str) -> bool:
        """Return whether `candidate` may displace `victim`.

        The default accepts every candidate, which reproduces classic LRU and
        LFU behavior.

        Args:
            candidate: The key that has just been loaded.
            victim: The key nominated for eviction.
        """
        return True

    def keys(self) -> Iterator[str]:
        """Yield the tracked keys in an unspecified order."""
        return iter(())


class LRUEviction(EvictionStrategy):
    """Encapsulates evicting the least recently used entry."""

    __slots__ = ("_order",)

    def __init__(self) -> None:
        """Initialize an LRUEviction instance."""
        self._order: OrderedDict[str, None] = OrderedDict()

    def record_write(self, key: str, weight: int = 1) -> None:
        """See base method."""
        self._order[key] = None
        self._order.move_to_end(key)

    def record_access(self, key: str) -> None:
        """See base method."""
        if key in self._order:
            self._order.move_to_end(key)

    def record_removal(self, key: str) -> None:
        """See base method."""
        self._order.pop(key, None)

    def victim(self) -> str | None:
        """See base method."""
        return next(iter(self._order), None)

    def clear(self) -> None:
        """See base method."""
        self._order.clear()

    def keys(self) -> Iterator[str]:
        """See base method."""
        return iter(list(self._order))


class FIFOEviction(EvictionStrategy):
    """Encapsulates evicting the entry that was written first, ignoring reads."""

    __slots__ = ("_order",)

    def __init__(self) -> None:
        """Initialize a FIFOEviction instance."""
        self._order: OrderedDict[str, None] = OrderedDict()

    def record_write(self, key: str, weight: int = 1) -> None:
        """See base method.

        A rewrite counts as a re-insertion and moves the key to the back.
        """
        self._order.pop(key, None)
        self._order[key] = None

    def record_access(self, key: str) -> None:
        """See base method."""

    def record_removal(self, key: str) -> None:
        """See base method."""
        self._order.pop(key, None)

    def victim(self) -> str | None:
        """See base method."""
        return next(iter(self._order), None)

    def clear(self) -> None:
        """See base method."""
        self._order.clear()

    def keys(self) -> Iterator[str]:
        """See base method."""
        return iter(list(self._order))


class LFUEviction(EvictionStrategy):
    """Encapsulates evicting the entry that has been read least often.

    Selecting a victim scans the tracked keys, so this strategy suits caches of
    moderate size where retention should follow long-term popularity.
    """

    __slots__ = ("_counts",)

    def __init__(self) -> None:
        """Initialize an LFUEviction instance."""
        self._counts: dict[str, int] = {}

    def record_write(self, key: str, weight: int = 1) -> None:
        """See base method."""
        self._counts.setdefault(key, 0)

    def record_access(self, key: str) -> None:
        """See base method."""
        if key in self._counts:
            self._counts[key] += 1

    def record_removal(self, key: str) -> None:
        """See base method."""
        self._counts.pop(key, None)

    def victim(self) -> str | None:
        """See base method."""
        if not self._counts:
            return None
        return min(self._counts, key=self._counts.__getitem__)

    def clear(self) -> None:
        """See base method."""
        self._counts.clear()

    def keys(self) -> Iterator[str]:
        """See base method."""
        return iter(list(self._counts))


class RandomEviction(EvictionStrategy):
    """Encapsulates evicting an arbitrary entry.

    Random replacement keeps bookkeeping to a minimum and degrades gracefully
    under workloads without temporal locality.

    Attributes:
        rng: The random source, injectable to keep tests deterministic.
    """

    __slots__ = ("_keys", "rng")

    def __init__(self, rng: random.Random | None = None):
        """Initialize a RandomEviction instance."""
        self._keys: dict[str, None] = {}
        self.rng = rng if rng is not None else random.Random()

    def record_write(self, key: str, weight: int = 1) -> None:
        """See base method."""
        self._keys[key] = None

    def record_access(self, key: str) -> None:
        """See base method."""

    def record_removal(self, key: str) -> None:
        """See base method."""
        self._keys.pop(key, None)

    def victim(self) -> str | None:
        """See base method."""
        if not self._keys:
            return None
        return self.rng.choice(list(self._keys))

    def clear(self) -> None:
        """See base method."""
        self._keys.clear()

    def keys(self) -> Iterator[str]:
        """See base method."""
        return iter(list(self._keys))


class CountMinSketch:
    """Encapsulates estimating access frequencies in fixed memory.

    Counters are shared between keys, so an estimate never underreports but may
    overreport. Halving all counters once a sample budget is reached ages out
    keys that were popular in the past.

    Attributes:
        width: Number of counters per row.
        depth: Number of independent rows.
        sample_size: Number of increments after which counters are halved.
    """

    __slots__ = ("width", "depth", "sample_size", "_rows", "_additions")

    def __init__(self, width: int = 1024, depth: int = 4, sample_size: int = 8192):
        """Initialize a CountMinSketch instance.

        Args:
            width: Number of counters per row.
            depth: Number of independent rows.
            sample_size: Number of increments after which counters are halved.

        Raises:
            CacheConfigurationError: If any dimension is not positive.
        """
        if width <= 0 or depth <= 0 or sample_size <= 0:
            raise CacheConfigurationError("Sketch dimensions must be positive")
        self.width = width
        self.depth = depth
        self.sample_size = sample_size
        self._rows = [[0] * width for _ in range(depth)]
        self._additions = 0

    def increment(self, key: str) -> None:
        """Record one access to `key` and age the sketch when it is full."""
        for row_index, position in enumerate(self._positions(key)):
            row = self._rows[row_index]
            if row[position] < 255:
                row[position] += 1
        self._additions += 1
        if self._additions >= self.sample_size:
            self.reset()

    def estimate(self, key: str) -> int:
        """Return the estimated access count of `key`."""
        return min(
            self._rows[row_index][position]
            for row_index, position in enumerate(self._positions(key))
        )

    def reset(self) -> None:
        """Halve every counter so that old popularity decays."""
        for row in self._rows:
            for index, value in enumerate(row):
                row[index] = value >> 1
        self._additions = 0

    def clear(self) -> None:
        """Zero every counter."""
        self._rows = [[0] * self.width for _ in range(self.depth)]
        self._additions = 0

    def _positions(self, key: str) -> list[int]:
        """Return one counter position per row for `key`."""
        base = hash(key)
        return [
            (base ^ (row_index * 0x9E3779B1)) % self.width
            for row_index in range(self.depth)
        ]


class TinyLFUEviction(EvictionStrategy):
    """Encapsulates combining recency ordering with frequency-based admission.

    Victims are chosen by recency, but a candidate is only admitted when the
    sketch believes it is at least as popular as the victim. This preserves a
    hot working set during a scan over many single-use keys, which is the
    failure mode of plain LRU.

    Attributes:
        sketch: The frequency estimator consulted on admission.
    """

    __slots__ = ("_order", "sketch")

    def __init__(self, sketch: CountMinSketch | None = None):
        """Initialize a TinyLFUEviction instance."""
        self._order: OrderedDict[str, None] = OrderedDict()
        self.sketch = sketch if sketch is not None else CountMinSketch()

    def record_write(self, key: str, weight: int = 1) -> None:
        """See base method."""
        self.sketch.increment(key)
        self._order[key] = None
        self._order.move_to_end(key)

    def record_access(self, key: str) -> None:
        """See base method."""
        self.sketch.increment(key)
        if key in self._order:
            self._order.move_to_end(key)

    def record_removal(self, key: str) -> None:
        """See base method."""
        self._order.pop(key, None)

    def victim(self) -> str | None:
        """See base method."""
        return next(iter(self._order), None)

    def admit(self, candidate: str, victim: str) -> bool:
        """See base method.

        A candidate is admitted when its estimated frequency is at least that
        of the victim, so ties favor the newer entry.
        """
        return self.sketch.estimate(candidate) >= self.sketch.estimate(victim)

    def clear(self) -> None:
        """See base method."""
        self._order.clear()
        self.sketch.clear()

    def keys(self) -> Iterator[str]:
        """See base method."""
        return iter(list(self._order))


def create_eviction_strategy(
    policy: EvictionPolicyType,
    rng: random.Random | None = None,
) -> EvictionStrategy:
    """Return a new strategy for a configured policy.

    Args:
        policy: The policy selected in configuration.
        rng: Random source forwarded to policies that need one.

    Returns:
        A fresh strategy instance, since a strategy holds per-cache state.

    Raises:
        CacheConfigurationError: If the policy is not implemented.
    """
    match policy:
        case EvictionPolicyType.LRU:
            return LRUEviction()
        case EvictionPolicyType.LFU:
            return LFUEviction()
        case EvictionPolicyType.FIFO:
            return FIFOEviction()
        case EvictionPolicyType.RANDOM:
            return RandomEviction(rng)
        case EvictionPolicyType.TINY_LFU:
            return TinyLFUEviction()
        case _:
            raise CacheConfigurationError(f"Unsupported eviction policy {policy}")
