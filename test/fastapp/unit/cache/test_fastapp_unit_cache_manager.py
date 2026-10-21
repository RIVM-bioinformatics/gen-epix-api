"""Tests for cache manager orchestration and configuration."""

import pytest

from gen_epix.fastapp.cache.exc import CacheConfigurationError, RegionNotFoundError
from gen_epix.fastapp.cache.manager import CacheManager, region_config_from_mapping
from gen_epix.fastapp.cache.model import NO_VALUE, RegionConfig


def test_invalidating_a_dependency_reaches_the_caches_that_declared_it() -> None:
    """A mutating method invalidates readers through declared dependencies."""
    manager = CacheManager()
    region = manager.create_region(RegionConfig(name="cases"))
    manager.declare_dependency("case", tags=("case:{case_id}",))
    region.set("summary", "s", tags=["case:7"])

    dispatched = manager.invalidate_dependents("case", {"case_id": 7})

    assert dispatched == 1
    assert region.get("summary") is NO_VALUE


def test_invalidation_is_deferred_until_the_unit_of_work_commits() -> None:
    """Readers must not repopulate the cache from uncommitted state."""
    manager = CacheManager()
    region = manager.create_region(RegionConfig(name="cases"))
    region.set("k", "value", tags=["case:1"])

    with manager.transaction() as transaction:
        region.invalidate_tags("case:1")
        assert region.get("k") == "value"
        assert len(transaction.pending) == 1

    assert region.get("k") is NO_VALUE


def test_a_rolled_back_unit_of_work_leaves_the_cache_untouched() -> None:
    """A failed write must not invalidate data that is still correct."""
    manager = CacheManager()
    region = manager.create_region(RegionConfig(name="cases"))
    region.set("k", "value", tags=["case:1"])

    def failing_unit_of_work() -> None:
        """Invalidate and then simulate a failed unit of work."""
        region.invalidate_tags("case:1")
        raise RuntimeError("unit of work failed")

    with pytest.raises(RuntimeError):
        with manager.transaction():
            failing_unit_of_work()

    assert region.get("k") == "value"


def test_the_manager_reports_and_resets_statistics_per_region() -> None:
    """Aggregated counters are available before and after reset."""
    manager = CacheManager()
    region = manager.create_region(RegionConfig(name="cases"))
    region.get_or_create("k", lambda: 1)
    region.get_or_create("k", lambda: 1)

    assert manager.statistics()["cases"].hits == 1
    assert manager.total_statistics().hits == 1
    manager.reset_statistics()
    assert manager.total_statistics().hits == 0


def test_an_unknown_region_is_reported_rather_than_created() -> None:
    """A misspelled region name must not silently create a cache."""
    manager = CacheManager()

    with pytest.raises(RegionNotFoundError):
        manager.get_region("missing")


def test_regions_can_be_described_entirely_in_configuration() -> None:
    """String enum values let settings files configure a region."""
    config = region_config_from_mapping(
        "cases",
        {"ttl": 30.0, "eviction_policy": "tiny_lfu", "failure_mode": "fail_closed"},
    )

    assert config.ttl == 30.0
    assert config.eviction_policy.name == "TINY_LFU"
    assert config.failure_mode.name == "FAIL_CLOSED"


def test_a_scope_part_string_is_refused_rather_than_split() -> None:
    """A bare string must not become one scope part per character."""
    with pytest.raises(CacheConfigurationError):
        region_config_from_mapping("cases", {"scope_parts": "tenant"})
    with pytest.raises(CacheConfigurationError):
        region_config_from_mapping("cases", {"scope_parts": ["tenant", ""]})

    config = region_config_from_mapping("cases", {"scope_parts": ["tenant"]})

    assert config.scope_parts == ("tenant",)


def test_disabling_the_manager_bypasses_every_region() -> None:
    """A disabled manager preserves behavior while bypassing cached values."""
    manager = CacheManager()
    region = manager.create_region(RegionConfig(name="cases"))
    region.set("k", "value")

    with manager.disabling():
        assert region.get("k") is NO_VALUE

    assert region.get("k") == "value"
