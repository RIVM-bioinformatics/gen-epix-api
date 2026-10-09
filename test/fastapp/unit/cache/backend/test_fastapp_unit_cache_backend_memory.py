"""Tests for the in-memory cache backend."""

import pytest

from gen_epix.fastapp.cache.backend.memory import MemoryBackend
from gen_epix.fastapp.cache.clock import ManualClock
from gen_epix.fastapp.cache.enum import EvictionPolicyType, RemovalCause
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
    """An expired entry is a miss and frees its capacity."""
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
    """Expired entries can be reclaimed without another read."""
    clock = ManualClock()
    backend = MemoryBackend(max_weight=10, clock=clock)
    backend.set("a", make_value(1, expires_at=5.0))
    backend.set("b", make_value(2))

    clock.advance(6)

    assert backend.expire() == ["a"]
    assert len(backend) == 1


def test_capacity_is_enforced_by_weight_not_by_count() -> None:
    """A heavy entry consumes more of the capacity budget."""
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
    """A replacement is distinct from an eviction."""
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
    """Clearing reports removal causes and resets the capacity count."""
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
    """A listener failure cannot surface as a cache failure."""

    def explode(key: str, value: CachedValue, cause: RemovalCause) -> None:
        """Simulate a defective removal listener."""
        raise RuntimeError("listener defect")

    backend = MemoryBackend(max_weight=1, removal_listener=explode)
    backend.set("a", make_value(1))

    backend.set("b", make_value(2))

    assert backend.get("b") is not NO_VALUE


def test_a_non_positive_capacity_is_rejected() -> None:
    """A backend that can hold nothing is invalid configuration."""
    with pytest.raises(CacheConfigurationError):
        MemoryBackend(max_weight=0)
