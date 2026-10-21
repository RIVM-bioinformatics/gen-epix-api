"""Tests for cache eviction and admission strategies."""

import pytest

from gen_epix.fastapp.cache.backend.memory import MemoryBackend
from gen_epix.fastapp.cache.enum import EvictionPolicyType
from gen_epix.fastapp.cache.eviction import (
    CountMinSketch,
    LFUEviction,
    LRUEviction,
    TinyLFUEviction,
    create_eviction_strategy,
)
from gen_epix.fastapp.cache.exc import CacheConfigurationError
from gen_epix.fastapp.cache.model import NO_VALUE, CachedValue, EntryMetadata


def make_value(payload: object) -> CachedValue:
    """Build an envelope for an eviction test."""
    return CachedValue(payload, EntryMetadata(created_at=0.0))


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
    """LFU retains by long-term popularity rather than recency."""
    strategy = LFUEviction()
    strategy.record_write("a")
    strategy.record_write("b")
    for _ in range(3):
        strategy.record_access("a")

    assert strategy.victim() == "b"


def test_lru_strategy_forgets_removed_keys() -> None:
    """A removed key must not be nominated as an eviction victim."""
    strategy = LRUEviction()
    strategy.record_write("a")
    strategy.record_write("b")

    strategy.record_removal("a")

    assert strategy.victim() == "b"


def test_sketch_estimates_never_underreport() -> None:
    """A count-min sketch may overreport but must retain observed accesses."""
    sketch = CountMinSketch(width=64, depth=3, sample_size=1000)
    seen_positions = sketch._positions("a")

    def has_no_counter_collision(candidate: str) -> bool:
        """Check that the candidate uses different counters in every row."""
        return all(
            observed != candidate_position
            for observed, candidate_position in zip(
                seen_positions, sketch._positions(candidate), strict=True
            )
        )

    unseen_key = next(
        f"never-seen-{index}"
        for index in range(1000)
        if has_no_counter_collision(f"never-seen-{index}")
    )
    for _ in range(5):
        sketch.increment("a")

    assert sketch.estimate("a") >= 5
    assert sketch.estimate(unseen_key) == 0


def test_sketch_halves_counters_once_the_sample_budget_is_reached() -> None:
    """Aging lets past popularity decay."""
    sketch = CountMinSketch(width=16, depth=2, sample_size=4)
    for _ in range(4):
        sketch.increment("a")

    assert sketch.estimate("a") == 2


def test_invalid_sketch_dimensions_are_rejected() -> None:
    """Every sketch dimension must be positive."""
    with pytest.raises(CacheConfigurationError):
        CountMinSketch(width=0)


def test_every_configured_policy_can_be_created() -> None:
    """Configuration selects an implemented strategy by name."""
    for policy in EvictionPolicyType:
        assert create_eviction_strategy(policy) is not None
