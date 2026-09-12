"""Tests for the in-memory cache backend and its eviction strategies."""

import pytest

from gen_epix.fastapp.cache.backend.memory import MemoryBackend
from gen_epix.fastapp.cache.backend.null import NullBackend
from gen_epix.fastapp.cache.clock import ManualClock
from gen_epix.fastapp.cache.enum import EvictionPolicyType, RemovalCause
from gen_epix.fastapp.cache.eviction import (
    CountMinSketch,
    LFUEviction,
    LRUEviction,
    TinyLFUEviction,
    create_eviction_strategy,
)
from gen_epix.fastapp.cache.exc import CacheConfigurationError
from gen_epix.fastapp.cache.model import NO_VALUE, CachedValue, EntryMetadata


def make_value(
    payload: object,
    created_at: float = 0.0,
    expires_at: float | None = None,
    weight: int = 1,
) -> CachedValue:
    """Build an envelope for a backend test."""
    return CachedValue(
        payload,
        EntryMetadata(created_at=created_at, expires_at=expires_at, weight=weight),
    )


def test_round_trip_and_absent_keys() -> None:
    """A stored envelope is returned; an unknown key reports a miss."""
    backend = MemoryBackend(max_weight=10)

    backend.set("a", make_value(1))

    assert backend.get("a").payload == 1  # type: ignore[union-attr]
    assert backend.get("b") is NO_VALUE
    assert backend.contains("a")
    assert not backend.contains("b")


def test_expired_entries_are_removed_on_read() -> None:
    """An entry past its expiry is a miss and no longer occupies the store."""
    clock = ManualClock()
    removals: list[tuple[str, RemovalCause]] = []
    backend = MemoryBackend(
        max_weight=10,
        clock=clock,
        removal_listener=lambda key, value, cause: removals.append((key, cause)),
    )
    backend.set("a", make_value(1, expires_at=5.0))

    clock.advance(5)

    assert backend.get("a") is NO_VALUE
    assert removals == [("a", RemovalCause.EXPIRED)]
    assert len(backend) == 0


def test_expire_reclaims_entries_that_are_never_read_again() -> None:
    """Lazy expiry alone would leak entries nobody touches."""
    clock = ManualClock()
    backend = MemoryBackend(max_weight=10, clock=clock)
    backend.set("a", make_value(1, expires_at=5.0))
    backend.set("b", make_value(2))

    clock.advance(6)

    assert backend.expire() == ["a"]
    assert len(backend) == 1


def test_capacity_is_enforced_by_weight_not_by_count() -> None:
    """A heavy entry consumes more of the budget than a light one."""
    backend = MemoryBackend(max_weight=3)

    backend.set("a", make_value(1, weight=2))
    backend.set("b", make_value(2, weight=1))
    backend.set("c", make_value(3, weight=1))

    assert backend.weight <= 3
    assert backend.get("a") is NO_VALUE
    assert backend.get("c") is not NO_VALUE


def test_least_recently_used_entry_is_evicted_first() -> None:
    """Reading an entry protects it from the next eviction."""
    removals: list[tuple[str, RemovalCause]] = []
    backend = MemoryBackend(
        max_weight=2,
        eviction=EvictionPolicyType.LRU,
        removal_listener=lambda key, value, cause: removals.append((key, cause)),
    )
    backend.set("a", make_value(1))
    backend.set("b", make_value(2))
    backend.get("a")

    backend.set("c", make_value(3))

    assert backend.get("b") is NO_VALUE
    assert backend.get("a") is not NO_VALUE
    assert ("b", RemovalCause.SIZE) in removals


def test_replacing_an_entry_reports_the_previous_one() -> None:
    """A replacement must not be confused with an eviction."""
    removals: list[tuple[str, RemovalCause]] = []
    backend = MemoryBackend(
        max_weight=5,
        removal_listener=lambda key, value, cause: removals.append((key, cause)),
    )
    backend.set("a", make_value(1))

    backend.set("a", make_value(2))

    assert backend.get("a").payload == 2  # type: ignore[union-attr]
    assert removals == [("a", RemovalCause.REPLACED)]


def test_clear_reports_every_entry_as_cleared() -> None:
    """Clearing a region must let a tag index drop its associations."""
    removals: list[RemovalCause] = []
    backend = MemoryBackend(
        max_weight=5,
        removal_listener=lambda key, value, cause: removals.append(cause),
    )
    backend.set("a", make_value(1))
    backend.set("b", make_value(2))

    backend.clear()

    assert removals == [RemovalCause.CLEARED, RemovalCause.CLEARED]
    assert len(backend) == 0
    assert backend.weight == 0


def test_a_failing_removal_listener_cannot_break_the_store() -> None:
    """Instrumentation defects must not surface as cache failures."""

    def explode(key: str, value: CachedValue, cause: RemovalCause) -> None:
        """Removal listener that always fails.

        Args:
            key: The removed key.
            value: The removed envelope.
            cause: Why the entry left.

        Raises:
            RuntimeError: Always, to simulate a defective listener.
        """
        raise RuntimeError("listener defect")

    backend = MemoryBackend(max_weight=1, removal_listener=explode)
    backend.set("a", make_value(1))

    backend.set("b", make_value(2))

    assert backend.get("b") is not NO_VALUE


def test_tiny_lfu_rejects_a_candidate_less_popular_than_its_victim() -> None:
    """A scan of one-shot keys must not flush a hot working set."""
    backend = MemoryBackend(max_weight=2, eviction=TinyLFUEviction())
    backend.set("hot", make_value(1))
    backend.set("warm", make_value(2))
    for _ in range(20):
        backend.get("hot")
        backend.get("warm")

    backend.set("scan", make_value(3))

    assert backend.get("scan") is NO_VALUE
    assert backend.get("hot") is not NO_VALUE
    assert backend.get("warm") is not NO_VALUE


def test_least_frequently_used_entry_is_evicted_first() -> None:
    """LFU retains by long-term popularity rather than by recency."""
    strategy = LFUEviction()
    strategy.record_write("a")
    strategy.record_write("b")
    for _ in range(3):
        strategy.record_access("a")

    assert strategy.victim() == "b"


def test_lru_strategy_forgets_removed_keys() -> None:
    """A removed key must not be nominated as a victim later."""
    strategy = LRUEviction()
    strategy.record_write("a")
    strategy.record_write("b")

    strategy.record_removal("a")

    assert strategy.victim() == "b"


def test_sketch_estimates_never_underreport() -> None:
    """A count-min sketch may overreport but must never lose an access."""
    sketch = CountMinSketch(width=64, depth=3, sample_size=1000)
    for _ in range(5):
        sketch.increment("a")

    assert sketch.estimate("a") >= 5
    assert sketch.estimate("never-seen") == 0


def test_sketch_halves_counters_once_the_sample_budget_is_reached() -> None:
    """Ageing the sketch lets past popularity decay."""
    sketch = CountMinSketch(width=16, depth=2, sample_size=4)
    for _ in range(4):
        sketch.increment("a")

    assert sketch.estimate("a") == 2


def test_invalid_sketch_dimensions_are_rejected() -> None:
    """A zero-width sketch cannot store anything."""
    with pytest.raises(CacheConfigurationError):
        CountMinSketch(width=0)


def test_every_configured_policy_can_be_created() -> None:
    """Configuration selects a strategy by name."""
    for policy in EvictionPolicyType:
        assert create_eviction_strategy(policy) is not None


def test_a_non_positive_capacity_is_rejected() -> None:
    """A store that can hold nothing is a configuration error."""
    with pytest.raises(CacheConfigurationError):
        MemoryBackend(max_weight=0)


def test_the_null_backend_never_stores_anything() -> None:
    """Disabling the cache must not change any call site."""
    backend = NullBackend()

    backend.set("a", make_value(1))

    assert backend.get("a") is NO_VALUE
    assert not backend.contains("a")
    assert list(backend.keys()) == []
    assert backend.get_multi(["a", "b"]) == [NO_VALUE, NO_VALUE]
