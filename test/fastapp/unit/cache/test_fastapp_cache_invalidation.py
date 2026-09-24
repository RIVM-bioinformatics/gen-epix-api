"""Tests for invalidation: keys, tags, generations, propagation and transactions."""

import pytest

from gen_epix.fastapp.cache.clock import ManualClock
from gen_epix.fastapp.cache.enum import InvalidationMode
from gen_epix.fastapp.cache.exc import CacheConfigurationError, RegionNotFoundError
from gen_epix.fastapp.cache.invalidation import (
    DependencyRegistry,
    Invalidation,
    InvalidationStrategy,
    LocalInvalidationBus,
)
from gen_epix.fastapp.cache.lock import InlineRefreshRunner
from gen_epix.fastapp.cache.manager import CacheManager, region_config_from_mapping
from gen_epix.fastapp.cache.model import NO_VALUE, RegionConfig
from gen_epix.fastapp.cache.region import CacheRegion
from gen_epix.fastapp.cache.tag import MemoryTagIndex, TagTemplate, render_tags
from gen_epix.fastapp.cache.transaction import invalidation_transaction
from gen_epix.fastapp.cache.version import MemoryVersionStore


def test_deleting_a_known_key_removes_only_that_entry() -> None:
    """The narrowest form of invalidation must not touch its neighbours."""
    region = CacheRegion(RegionConfig(name="test"))
    region.set("a", 1)
    region.set("b", 2)

    region.invalidate_keys("a")

    assert region.get("a") is NO_VALUE
    assert region.get("b") == 2


def test_a_tag_invalidates_every_entry_that_declared_it() -> None:
    """A writer names the changed thing; readers declared that name."""
    region = CacheRegion(RegionConfig(name="test"))
    region.set("summary", "s", tags=["case:1"])
    region.set("detail", "d", tags=["case:1"])
    region.set("other", "o", tags=["case:2"])

    removed = region.invalidate_tags("case:1")

    assert removed == 1
    assert region.get("summary") is NO_VALUE
    assert region.get("detail") is NO_VALUE
    assert region.get("other") == "o"


def test_bumping_the_generation_orphans_every_key_at_once() -> None:
    """Constant-time invalidation is the only affordable option at scale."""
    region = CacheRegion(RegionConfig(name="test"))
    for index in range(50):
        region.set(f"k{index}", index)
    before = region.generation

    after = region.bump_generation()

    assert after == before + 1
    assert all(region.get(f"k{index}") is NO_VALUE for index in range(50))


def test_a_hard_region_invalidation_forces_regeneration() -> None:
    """Nothing written before the cut-off may be served."""
    clock = ManualClock()
    region = CacheRegion(RegionConfig(name="test", ttl=100.0), clock=clock)
    calls: list[int] = []

    def load() -> int:
        """Count invocations and return the invocation number."""
        calls.append(1)
        return len(calls)

    assert region.get_or_create("k", load) == 1
    clock.advance(1)
    region.invalidate(InvalidationMode.HARD)

    assert region.get_or_create("k", load) == 2


def test_a_soft_region_invalidation_serves_the_old_value_once_more() -> None:
    """Soft invalidation avoids a load spike at the cost of one stale read."""
    clock = ManualClock()
    region = CacheRegion(
        RegionConfig(name="test", ttl=100.0),
        clock=clock,
        refresh_runner=InlineRefreshRunner(),
    )
    calls: list[int] = []

    def load() -> int:
        """Count invocations and return the invocation number."""
        calls.append(1)
        return len(calls)

    assert region.get_or_create("k", load) == 1
    clock.advance(1)
    region.invalidate(InvalidationMode.SOFT)

    assert region.get_or_create("k", load) == 1
    assert region.get_or_create("k", load) == 2


def test_clearing_a_region_removes_everything_in_it() -> None:
    """The broadest form of invalidation is always available."""
    region = CacheRegion(RegionConfig(name="test"))
    region.set("a", 1)

    region.clear()

    assert region.get("a") is NO_VALUE


def test_an_invalidation_aimed_at_another_region_is_ignored() -> None:
    """A cross-region request must not clear an unrelated cache."""
    region = CacheRegion(RegionConfig(name="test"))
    region.set("a", 1)

    region.apply(Invalidation.for_all(region="other"))

    assert region.get("a") == 1


def test_the_invalidation_strategy_separates_hard_from_soft_cut_offs() -> None:
    """Readers must be able to tell 'wait' apart from 'serve while refreshing'."""
    clock = ManualClock()
    strategy = InvalidationStrategy(clock)
    written_at = clock.monotonic()
    clock.advance(1)

    strategy.invalidate(InvalidationMode.SOFT)

    assert strategy.is_soft_invalidated(written_at)
    assert not strategy.is_hard_invalidated(written_at)
    strategy.invalidate(InvalidationMode.HARD)
    assert strategy.is_hard_invalidated(written_at)
    assert not strategy.is_soft_invalidated(written_at)


def test_a_published_request_carries_the_origin_of_the_bus() -> None:
    """A transport needs the origin to recognize the echo of its own message."""
    bus = LocalInvalidationBus(origin="worker-1")
    received: list[Invalidation] = []
    bus.subscribe(received.append)

    bus.publish(Invalidation.for_tags(["case:1"]))

    assert received[0].origin == "worker-1"


def test_a_forwarded_request_keeps_the_origin_it_arrived_with() -> None:
    """Re-publishing must not disguise where a request came from."""
    bus = LocalInvalidationBus(origin="worker-1")
    received: list[Invalidation] = []
    bus.subscribe(received.append)
    inbound = Invalidation.for_tags(["case:1"], origin="worker-2")

    bus.publish(inbound)

    assert received[0].origin == "worker-2"
    assert received[0].message_id == inbound.message_id


def test_a_repeated_invalidation_message_is_applied_once() -> None:
    """At-least-once transports redeliver, and that must be harmless."""
    bus = LocalInvalidationBus()
    received: list[Invalidation] = []
    bus.subscribe(received.append)
    message = Invalidation.for_tags(["case:1"])

    assert bus.deliver(message) is True
    assert bus.deliver(message) is False

    assert len(received) == 1


def test_a_failing_subscriber_does_not_block_the_others() -> None:
    """One broken cache tier must not keep the rest stale."""
    bus = LocalInvalidationBus()
    received: list[Invalidation] = []

    def explode(invalidation: Invalidation) -> None:
        """Subscriber that always fails.

        Args:
            invalidation: The delivered request.

        Raises:
            RuntimeError: Always, to simulate a defective subscriber.
        """
        raise RuntimeError("subscriber defect")

    bus.subscribe(explode)
    bus.subscribe(received.append)

    bus.publish(Invalidation.for_all())

    assert len(received) == 1


def test_a_bus_delivers_an_invalidation_to_every_subscribed_region() -> None:
    """A deletion in one worker must not leave another serving stale data."""
    bus = LocalInvalidationBus()
    first = CacheRegion(RegionConfig(name="test"), bus=bus)
    second = CacheRegion(RegionConfig(name="test"), backend=first.backend, bus=bus)
    first.set("k", "value", tags=["case:1"])
    second.set("k", "value", tags=["case:1"])

    second.invalidate_tags("case:1")

    assert first.get("k") is NO_VALUE


def test_declared_dependencies_translate_a_change_into_invalidations() -> None:
    """A writer names the changed thing and never learns which caches exist."""
    registry = DependencyRegistry()
    registry.declare("case", tags=("case:{case_id}",))
    registry.declare("case", regions=("reports",))

    invalidations = registry.resolve("case", {"case_id": 7})

    assert {"case:7"} in [invalidation.tags for invalidation in invalidations]
    assert "reports" in [invalidation.region for invalidation in invalidations]
    assert registry.resolve("unknown") == []


def test_invalidating_a_dependency_reaches_the_caches_that_declared_it() -> None:
    """This is the operation a mutating method is expected to call."""
    manager = CacheManager()
    region = manager.create_region(RegionConfig(name="cases"))
    manager.declare_dependency("case", tags=("case:{case_id}",))
    region.set("summary", "s", tags=["case:7"])

    dispatched = manager.invalidate_dependents("case", {"case_id": 7})

    assert dispatched == 1
    assert region.get("summary") is NO_VALUE


def test_invalidation_is_deferred_until_the_unit_of_work_commits() -> None:
    """A concurrent reader must not repopulate from uncommitted state."""
    manager = CacheManager()
    region = manager.create_region(RegionConfig(name="cases"))
    region.set("k", "value", tags=["case:1"])

    with manager.transaction() as transaction:
        region.invalidate_tags("case:1")
        assert region.get("k") == "value"
        assert len(transaction.pending) == 1

    assert region.get("k") is NO_VALUE


def test_a_rolled_back_unit_of_work_leaves_the_cache_untouched() -> None:
    """Invalidating for a change that never happened wastes the cache."""
    manager = CacheManager()
    region = manager.create_region(RegionConfig(name="cases"))
    region.set("k", "value", tags=["case:1"])

    def failing_unit_of_work() -> None:
        """Invalidate and then fail.

        Raises:
            RuntimeError: Always, to simulate a failed unit of work.
        """
        region.invalidate_tags("case:1")
        raise RuntimeError("unit of work failed")

    with pytest.raises(RuntimeError):
        with manager.transaction():
            failing_unit_of_work()

    assert region.get("k") == "value"


def test_identical_requests_collapse_inside_a_transaction() -> None:
    """A loop over many objects must not replay one broad invalidation."""
    applied: list[Invalidation] = []

    with invalidation_transaction(applied.append) as transaction:
        for _ in range(5):
            transaction.add(Invalidation.for_tags(["case"]))

    assert len(applied) == 1


def test_namespace_bumps_with_different_generations_are_both_kept() -> None:
    """Collapsing them would make receivers adopt a generation behind the origin."""
    applied: list[Invalidation] = []

    with invalidation_transaction(applied.append) as transaction:
        transaction.add(Invalidation.for_namespace("cases", generation=5))
        transaction.add(Invalidation.for_namespace("cases", generation=6))

    assert [invalidation.generation for invalidation in applied] == [5, 6]


def test_a_closed_transaction_refuses_further_requests() -> None:
    """Silently dropping a late request would leave a stale cache."""
    with invalidation_transaction(lambda invalidation: None) as transaction:
        pass

    with pytest.raises(RuntimeError):
        transaction.add(Invalidation.for_all())


def test_tag_templates_render_from_call_arguments() -> None:
    """Tags must be reproducible by a writer that never made the call."""
    assert TagTemplate("case:{case_id}").render({"case_id": 3}) == "case:3"
    assert render_tags(("case", "case:{case_id}"), {"case_id": 3}) == frozenset(
        {"case", "case:3"}
    )


def test_the_tag_index_keeps_both_directions_consistent() -> None:
    """Removing a key must not leave it reachable through a tag."""
    index = MemoryTagIndex()
    index.add("k", ["a", "b"])

    index.discard_key("k")

    assert index.keys_for("a") == set()
    assert index.tags() == set()


def test_retagging_a_key_drops_its_previous_tags() -> None:
    """A rewritten entry must not be invalidated by a tag it no longer has."""
    index = MemoryTagIndex()
    index.add("k", ["old"])

    index.add("k", ["new"])

    assert index.keys_for("old") == set()
    assert index.keys_for("new") == {"k"}


def test_a_generation_never_moves_backwards() -> None:
    """Adopting a remote generation must not make orphans addressable again."""
    store = MemoryVersionStore()
    store.bump("cases")
    store.bump("cases")

    store.set("cases", 1)

    assert store.get("cases") == 2


def test_the_manager_reports_and_resets_statistics_per_region() -> None:
    """Aggregated counters are what reveal a collapsing hit rate."""
    manager = CacheManager()
    region = manager.create_region(RegionConfig(name="cases"))
    region.get_or_create("k", lambda: 1)
    region.get_or_create("k", lambda: 1)

    assert manager.statistics()["cases"].hits == 1
    assert manager.total_statistics().hits == 1
    manager.reset_statistics()
    assert manager.total_statistics().hits == 0


def test_an_unknown_region_is_reported_rather_than_created() -> None:
    """A typo in a region name must not silently produce a new cache."""
    manager = CacheManager()

    with pytest.raises(RegionNotFoundError):
        manager.get_region("missing")


def test_regions_can_be_described_entirely_in_configuration() -> None:
    """Enumerated fields accept their names so settings files suffice."""
    config = region_config_from_mapping(
        "cases",
        {"ttl": 30.0, "eviction_policy": "tiny_lfu", "failure_mode": "fail_closed"},
    )

    assert config.ttl == 30.0
    assert config.eviction_policy.name == "TINY_LFU"
    assert config.failure_mode.name == "FAIL_CLOSED"


def test_a_scope_part_string_is_refused_rather_than_split() -> None:
    """`tuple("tenant")` would produce one scope part per character."""
    with pytest.raises(CacheConfigurationError):
        region_config_from_mapping("cases", {"scope_parts": "tenant"})
    with pytest.raises(CacheConfigurationError):
        region_config_from_mapping("cases", {"scope_parts": ["tenant", ""]})

    config = region_config_from_mapping("cases", {"scope_parts": ["tenant"]})

    assert config.scope_parts == ("tenant",)


def test_disabling_the_manager_bypasses_every_region() -> None:
    """Running a suite uncached is the strongest guard against stale reads."""
    manager = CacheManager()
    region = manager.create_region(RegionConfig(name="cases"))
    region.set("k", "value")

    with manager.disabling():
        assert region.get("k") is NO_VALUE

    assert region.get("k") == "value"
