"""Tests for the read, write and expiry behavior of a cache region."""

import asyncio
import random
import threading
import time
from dataclasses import replace
from typing import cast

import pytest

from gen_epix.fastapp.cache.backend.base import CacheBackend
from gen_epix.fastapp.cache.backend.memory import MemoryBackend
from gen_epix.fastapp.cache.clock import ManualClock
from gen_epix.fastapp.cache.enum import (
    CacheOperation,
    FailureMode,
    InvalidationMode,
    InvalidationScope,
)
from gen_epix.fastapp.cache.exc import (
    CacheBackendError,
    CacheConfigurationError,
    CantDeserializeError,
    KeyRejectedError,
)
from gen_epix.fastapp.cache.invalidation import Invalidation, LocalInvalidationBus
from gen_epix.fastapp.cache.lock import InlineRefreshRunner
from gen_epix.fastapp.cache.model import NO_VALUE, CachedValue, RegionConfig
from gen_epix.fastapp.cache.region import CacheRegion, create_layered_region
from gen_epix.fastapp.cache.resilience import FailurePolicy
from gen_epix.fastapp.cache.scope import ContextVarScopeProvider, RequestScope
from gen_epix.fastapp.cache.serializer import DeepCopySerializer, Serializer
from gen_epix.fastapp.cache.stats import RecordingListener
from gen_epix.fastapp.cache.transaction import invalidation_transaction


class BrokenBackend(CacheBackend):
    """Backend that fails every operation, to exercise the failure policy."""

    def get(self, key: str) -> CachedValue:
        """Fail instead of reading.

        Args:
            key: The requested key.

        Returns:
            Never returns.

        Raises:
            CacheBackendError: Always.
        """
        raise CacheBackendError("store unavailable")

    def set(self, key: str, value: CachedValue) -> None:
        """Fail instead of writing.

        Args:
            key: The key to write.
            value: The envelope to store.

        Raises:
            CacheBackendError: Always.
        """
        raise CacheBackendError("store unavailable")

    def delete(self, key: str) -> None:
        """Fail instead of deleting.

        Args:
            key: The key to remove.

        Raises:
            CacheBackendError: Always.
        """
        raise CacheBackendError("store unavailable")

    def clear(self) -> None:
        """Fail instead of clearing.

        Raises:
            CacheBackendError: Always.
        """
        raise CacheBackendError("store unavailable")

    def contains(self, key: str) -> bool:
        """See base method."""
        return False

    def keys(self):  # type: ignore[no-untyped-def]
        """See base method."""
        return iter(())


class UnreadableSerializer(Serializer):
    """Serializer that cannot read back what it wrote."""

    def dumps(self, value: object) -> object:
        """See base method."""
        return value

    def loads(self, stored: object) -> object:
        """Fail instead of reading back a stored payload.

        Args:
            stored: The stored payload.

        Returns:
            Never returns.

        Raises:
            CantDeserializeError: Always.
        """
        raise CantDeserializeError("written by an older release")


def make_region(**config: object) -> tuple[CacheRegion, ManualClock, list[int]]:
    """Build a region with a manual clock and a counting loader."""
    clock = ManualClock()
    settings = {"name": "test", "ttl": 10.0}
    settings.update(config)
    region = CacheRegion(RegionConfig(**settings), clock=clock)  # type: ignore[arg-type]
    return region, clock, []


def test_a_second_read_is_served_from_cache() -> None:
    """The loader runs once for repeated reads of one key."""
    region, _, calls = make_region()

    def load() -> str:
        """Count invocations and return a value."""
        calls.append(1)
        return "value"

    assert region.get_or_create("k", load) == "value"
    assert region.get_or_create("k", load) == "value"
    assert len(calls) == 1


def test_an_expired_entry_is_reloaded() -> None:
    """A hard time to live bounds how stale a served value can be."""
    region, clock, calls = make_region(ttl=10.0)

    def load() -> int:
        """Count invocations and return the invocation number."""
        calls.append(1)
        return len(calls)

    assert region.get_or_create("k", load) == 1
    clock.advance(11)

    assert region.get_or_create("k", load) == 2


def test_a_cached_none_is_distinguishable_from_a_miss() -> None:
    """Negative caching must not be defeated by a falsy payload."""
    region, _, calls = make_region()

    def load() -> None:
        """Count invocations and return an absent result."""
        calls.append(1)
        return None

    assert region.get_or_create("k", load) is None
    assert region.get_or_create("k", load) is None
    assert len(calls) == 1
    assert region.get("k") is None


def test_absent_results_are_not_cached_when_configured() -> None:
    """A region may refuse to remember that something was missing."""
    region, _, calls = make_region(cache_none=False)

    def load() -> None:
        """Count invocations and return an absent result."""
        calls.append(1)
        return None

    region.get_or_create("k", load)
    region.get_or_create("k", load)

    assert len(calls) == 2


def test_a_negative_result_can_expire_sooner_than_a_positive_one() -> None:
    """A short negative time to live limits the cost of a wrong absence."""
    region, clock, calls = make_region(ttl=100.0, negative_ttl=5.0)

    def load() -> None:
        """Count invocations and return an absent result."""
        calls.append(1)
        return None

    region.get_or_create("k", load)
    clock.advance(6)
    region.get_or_create("k", load)

    assert len(calls) == 2


def test_should_cache_fn_returns_the_value_without_storing_it() -> None:
    """Conditional caching keeps unwanted results out of the store."""
    region, _, calls = make_region()

    def load() -> int:
        """Count invocations and return the invocation number."""
        calls.append(1)
        return len(calls)

    first = region.get_or_create("k", load, should_cache_fn=lambda value: False)
    second = region.get_or_create("k", load, should_cache_fn=lambda value: False)

    assert (first, second) == (1, 2)


def test_a_configured_exception_is_cached_and_re_raised() -> None:
    """Caching a failure protects an origin that is already struggling."""
    region, _, calls = make_region(cache_exceptions=(ValueError,))

    def load() -> int:
        """Count invocations and always fail.

        Returns:
            Never returns.

        Raises:
            ValueError: Always.
        """
        calls.append(1)
        raise ValueError("origin refused")

    with pytest.raises(ValueError):
        region.get_or_create("k", load)
    with pytest.raises(ValueError):
        region.get_or_create("k", load)

    assert len(calls) == 1


def test_an_unlisted_exception_is_not_cached() -> None:
    """A failure the configuration does not list must be retried."""
    region, _, calls = make_region()

    def load() -> int:
        """Count invocations and always fail.

        Returns:
            Never returns.

        Raises:
            RuntimeError: Always.
        """
        calls.append(1)
        raise RuntimeError("transient")

    for _ in range(2):
        with pytest.raises(RuntimeError):
            region.get_or_create("k", load)

    assert len(calls) == 2


def test_a_stale_entry_is_served_while_it_is_refreshed() -> None:
    """A soft time to live trades bounded staleness for a fast read."""
    clock = ManualClock()
    region = CacheRegion(
        RegionConfig(name="test", ttl=10.0, soft_ttl=5.0),
        clock=clock,
        refresh_runner=InlineRefreshRunner(),
    )
    calls: list[int] = []

    def load() -> int:
        """Count invocations and return the invocation number."""
        calls.append(1)
        return len(calls)

    assert region.get_or_create("k", load) == 1
    clock.advance(6)

    assert region.get_or_create("k", load) == 1
    assert region.get_or_create("k", load) == 2
    assert region.statistics().stale_hits == 1


def test_concurrent_readers_run_the_loader_once() -> None:
    """An expiry must not let every waiting caller hit the origin."""
    region, _, calls = make_region()
    lock = threading.Lock()

    def load() -> str:
        """Record one slow invocation."""
        with lock:
            calls.append(1)
        time.sleep(0.1)
        return "value"

    results: list[str] = []

    def worker() -> None:
        """Read the same key from a worker thread."""
        results.append(region.get_or_create("k", load))

    threads = [threading.Thread(target=worker) for _ in range(4)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=5)

    assert not any(thread.is_alive() for thread in threads)
    assert results == ["value"] * 4
    assert len(calls) == 1


def test_multi_key_reads_load_only_what_is_missing() -> None:
    """A partially warm batch costs one origin call for the remainder."""
    region, _, _ = make_region()
    region.set("a", 1)
    asked: list[list[str]] = []

    def load(keys):  # type: ignore[no-untyped-def]
        """Record the requested keys and produce a value for each."""
        asked.append(list(keys))
        return [10 for _ in keys]

    assert region.get_or_create_multi(["a", "b", "c"], load) == [1, 10, 10]
    assert asked == [["b", "c"]]


def test_multi_key_reads_load_duplicate_missing_keys_once() -> None:
    """Repeated positions for one key share the same loaded value."""
    region, _, _ = make_region()
    asked: list[list[str]] = []

    def load(keys):  # type: ignore[no-untyped-def]
        asked.append(list(keys))
        return [10 for _ in keys]

    assert region.get_or_create_multi(["a", "a", "b"], load) == [10, 10, 10]
    assert asked == [["a", "b"]]


def test_a_multi_key_loader_must_answer_every_key() -> None:
    """A short answer would misalign payloads with keys."""
    region, _, _ = make_region()

    with pytest.raises(ValueError):
        region.get_or_create_multi(["a", "b"], lambda keys: [1])


def test_a_disabled_region_behaves_as_a_pass_through() -> None:
    """Cached and uncached runs must produce the same results."""
    region, _, calls = make_region()

    def load() -> int:
        """Count invocations and return the invocation number."""
        calls.append(1)
        return len(calls)

    region.get_or_create("k", load)
    with region.disabling():
        assert region.get_or_create("k", load) == 2
        assert region.get("k") is NO_VALUE

    assert region.get_or_create("k", load) == 1


def test_a_backend_failure_degrades_to_the_loader() -> None:
    """A broken cache must cost throughput, not availability."""
    region = CacheRegion(RegionConfig(name="test"), backend=BrokenBackend())
    calls: list[int] = []

    def load() -> str:
        """Count invocations and return a value."""
        calls.append(1)
        return "value"

    assert region.get_or_create("k", load) == "value"
    assert region.get_or_create("k", load) == "value"
    assert len(calls) == 2


def test_a_backend_failure_can_be_configured_to_surface() -> None:
    """A region may prefer to fail rather than silently bypass the cache."""
    region = CacheRegion(
        RegionConfig(name="test", failure_mode=FailureMode.FAIL_CLOSED),
        backend=BrokenBackend(),
        failure_policy=FailurePolicy(mode=FailureMode.FAIL_CLOSED),
    )

    with pytest.raises(CacheBackendError):
        region.get_or_create("k", lambda: "value")


def test_an_unreadable_entry_is_replaced_instead_of_failing() -> None:
    """Entries written by an older release must not break a request."""
    region = CacheRegion(RegionConfig(name="test"), serializer=UnreadableSerializer())
    calls: list[int] = []

    def load() -> str:
        """Count invocations and return a value."""
        calls.append(1)
        return "value"

    assert region.get_or_create("k", load) == "value"
    assert region.get_or_create("k", load) == "value"
    assert len(calls) == 2


def test_a_payload_schema_change_invalidates_existing_entries() -> None:
    """A release that changes the payload layout must not read old entries."""
    clock = ManualClock()
    old = CacheRegion(RegionConfig(name="test", schema_version=1), clock=clock)
    old.set("k", "old value")
    backend = old.backend
    new = CacheRegion(
        RegionConfig(name="test", schema_version=2), backend=backend, clock=clock
    )

    assert new.get("k") is NO_VALUE


def test_a_copying_serializer_isolates_callers_from_the_cache() -> None:
    """A caller that mutates a result must not corrupt the cached value."""
    region = CacheRegion(RegionConfig(name="test"), serializer=DeepCopySerializer())
    region.set("k", {"items": [1]})

    first = region.get("k")
    first["items"].append(2)

    assert region.get("k") == {"items": [1]}


def test_a_required_scope_part_must_be_present() -> None:
    """A missing principal would produce a key shared by every caller."""
    region = CacheRegion(
        RegionConfig(name="test", scope_parts=("tenant",)),
        scope_provider=ContextVarScopeProvider(),
    )

    with pytest.raises(CacheConfigurationError):
        region.get_or_create("k", lambda: "value")


def test_different_principals_do_not_share_an_entry() -> None:
    """Scope parts keep results of different tenants apart."""
    region = CacheRegion(
        RegionConfig(name="test", scope_parts=("tenant",)),
        scope_provider=ContextVarScopeProvider(),
    )

    with ContextVarScopeProvider.bind(tenant="a"):
        region.set("k", "value-a")
    with ContextVarScopeProvider.bind(tenant="b"):
        assert region.get("k") is NO_VALUE
        region.set("k", "value-b")
    with ContextVarScopeProvider.bind(tenant="a"):
        assert region.get("k") == "value-a"


def test_an_admission_policy_can_refuse_a_key() -> None:
    """A key space that untrusted input can influence must stay bounded."""
    region = CacheRegion(
        RegionConfig(name="test"), key_admission=lambda key: len(key) < 40
    )

    with pytest.raises(KeyRejectedError):
        region.get_or_create("x" * 100, lambda: "value")


def test_a_request_scope_gives_read_your_own_writes() -> None:
    """Within one request a written value must be visible immediately."""
    region, _, calls = make_region()

    def load() -> int:
        """Count invocations and return the invocation number."""
        calls.append(1)
        return len(calls)

    with RequestScope.activate():
        region.get_or_create("k", load)
        region.get_or_create("k", load)

    assert len(calls) == 1


def test_statistics_report_hits_misses_and_loads() -> None:
    """Instrumentation is what makes a key-schema defect visible."""
    region, _, _ = make_region()
    region.get_or_create("k", lambda: "value")
    region.get_or_create("k", lambda: "value")

    statistics = region.statistics()

    assert (statistics.hits, statistics.misses, statistics.loads) == (1, 1, 1)
    assert statistics.hit_rate == pytest.approx(0.5)


def test_a_listener_observes_writes_and_removals() -> None:
    """A test can assert on events instead of on private state."""
    listener = RecordingListener()
    region = CacheRegion(RegionConfig(name="test"), listener=listener)

    region.set("k", "value")
    region.invalidate_keys("k")

    assert listener.of(CacheOperation.SET)
    assert listener.of(CacheOperation.INVALIDATE)


def test_contradictory_configurations_are_rejected() -> None:
    """A soft expiry after the hard one, or without one, is meaningless."""
    with pytest.raises(CacheConfigurationError):
        RegionConfig(name="test", ttl=5.0, soft_ttl=10.0)
    with pytest.raises(CacheConfigurationError):
        RegionConfig(name="test", soft_ttl=5.0)
    with pytest.raises(CacheConfigurationError):
        RegionConfig(name="", ttl=5.0)
    with pytest.raises(CacheConfigurationError):
        RegionConfig(name="test", jitter_ratio=1.5)


def test_deleting_a_known_key_removes_only_that_entry() -> None:
    """The narrowest invalidation must leave neighbouring keys intact."""
    region = CacheRegion(RegionConfig(name="test"))
    region.set("a", 1)
    region.set("b", 2)

    region.invalidate_keys("a")

    assert region.get("a") is NO_VALUE
    assert region.get("b") == 2


def test_a_tag_invalidates_every_entry_that_declared_it() -> None:
    """A tag removes every entry that declared the changed entity."""
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
    """Generation bumps invalidate an arbitrarily large key set at once."""
    region = CacheRegion(RegionConfig(name="test"))
    for index in range(50):
        region.set(f"k{index}", index)
    before = region.generation

    after = region.bump_generation()

    assert after == before + 1
    assert all(region.get(f"k{index}") is NO_VALUE for index in range(50))


def test_a_hard_region_invalidation_forces_regeneration() -> None:
    """A hard invalidation prevents the old value from being served."""
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
    """Soft invalidation serves stale data while an inline refresh runs."""
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
    """The broadest invalidation removes all entries from one region."""
    region = CacheRegion(RegionConfig(name="test"))
    region.set("a", 1)

    region.clear()

    assert region.get("a") is NO_VALUE


def test_an_invalidation_aimed_at_another_region_is_ignored() -> None:
    """A region ignores invalidation requests addressed elsewhere."""
    region = CacheRegion(RegionConfig(name="test"))
    region.set("a", 1)

    region.apply(Invalidation.for_all(region="other"))

    assert region.get("a") == 1


def test_a_bus_delivers_an_invalidation_to_every_subscribed_region() -> None:
    """Invalidation in one worker reaches other regions sharing the bus."""
    bus = LocalInvalidationBus()
    first = CacheRegion(RegionConfig(name="test"), bus=bus)
    second = CacheRegion(RegionConfig(name="test"), backend=first.backend, bus=bus)
    first.set("k", "value", tags=["case:1"])
    second.set("k", "value", tags=["case:1"])

    second.invalidate_tags("case:1")

    assert first.get("k") is NO_VALUE


def test_bulk_operations_return_metadata_and_support_empty_inputs() -> None:
    """Bulk APIs preserve key ordering and expose stored entry metadata."""
    region, _, _ = make_region()
    region.set_multi({"a": 1, "b": 2})

    assert region.get_multi(iter(["b", "a", "missing"])) == [2, 1, NO_VALUE]
    metadata = region.get_value_metadata("a")
    assert metadata is not None
    assert metadata.metadata.tags == frozenset()
    assert region.get_value_metadata("missing") is None

    region.delete_multi(["a"])
    assert region.get("a") is NO_VALUE
    region.warm({"c": 3})
    assert region.get("c") == 3

    region.set_multi({})
    assert region.invalidate_keys() == 0
    assert region.invalidate_tags() == 0


def test_disabled_region_bypasses_bulk_reads_and_writes() -> None:
    """Disabling applies consistently to direct and bulk cache APIs."""
    region, _, _ = make_region()

    with region.disabling():
        assert region.get_multi(["a", "b"]) == [NO_VALUE, NO_VALUE]
        region.set("a", 1)
        region.set_multi({"b": 2})
        assert region.get_or_create_multi(["c", "d"], lambda keys: [3, 4]) == [3, 4]

    assert region.get_multi(["a", "b"]) == [NO_VALUE, NO_VALUE]
    assert region.get("c") is NO_VALUE


def test_multi_reads_reuse_cached_values_and_respect_cache_predicate() -> None:
    """A fully warm batch skips loading, and rejected outputs are not stored."""
    region, _, _ = make_region()
    region.set("a", 1)
    assert region.get_or_create_multi(["a"], lambda keys: pytest.fail()) == [1]

    calls: list[list[str]] = []

    def load(keys):  # type: ignore[no-untyped-def]
        calls.append(list(keys))
        return [2 for _ in keys]

    assert region.get_or_create_multi(
        ["b", "b"], load, should_cache_fn=lambda value: False
    ) == [2, 2]
    assert calls == [["b"]]
    assert region.get("b") is NO_VALUE


def test_async_reads_cache_values_and_bypass_when_disabled() -> None:
    """Async reads share cached results and disabled reads call the creator."""
    region, _, calls = make_region()

    async def load() -> str:
        calls.append(1)
        return "value"

    async def exercise() -> None:
        assert await region.aget_or_create("key", load) == "value"
        assert await region.aget_or_create("key", load) == "value"
        assert len(calls) == 1

        with region.disabling():
            assert await region.aget_or_create("key", load) == "value"
        assert len(calls) == 2

    asyncio.run(exercise())


def test_concurrent_async_readers_share_one_loader() -> None:
    """Concurrent async misses use one loader execution."""
    region, _, calls = make_region()
    started = asyncio.Event()
    release = asyncio.Event()

    async def load() -> str:
        calls.append(1)
        started.set()
        await release.wait()
        return "value"

    async def exercise() -> None:
        first = asyncio.create_task(region.aget_or_create("key", load))
        await started.wait()
        second = asyncio.create_task(region.aget_or_create("key", load))
        release.set()

        assert await asyncio.gather(first, second) == ["value", "value"]

    asyncio.run(exercise())
    assert len(calls) == 1


def test_async_cached_and_uncached_loader_failures() -> None:
    """Configured async failures are cached while other failures can retry."""
    region, _, cached_calls = make_region(cache_exceptions=(ValueError,))

    async def cached_failure() -> str:
        cached_calls.append(1)
        raise ValueError("cached")

    async def transient_failure() -> str:
        raise RuntimeError("transient")

    async def exercise() -> None:
        for _ in range(2):
            with pytest.raises(ValueError, match="cached"):
                await region.aget_or_create("cached", cached_failure)
        assert len(cached_calls) == 1

        with pytest.raises(RuntimeError, match="transient"):
            await region.aget_or_create("transient", transient_failure)

    asyncio.run(exercise())


def test_async_stale_entry_is_refreshed_inline() -> None:
    """An async read reloads a stale entry instead of returning it as fresh."""
    clock = ManualClock()
    region = CacheRegion(RegionConfig(name="async", ttl=10, soft_ttl=5), clock=clock)
    calls: list[int] = []

    async def load() -> int:
        calls.append(1)
        return len(calls)

    async def exercise() -> None:
        assert await region.aget_or_create("key", load) == 1
        clock.advance(6)
        assert await region.aget_or_create("key", load) == 2

    asyncio.run(exercise())
    assert len(calls) == 2


def test_transaction_defers_key_invalidation_until_commit() -> None:
    """An ambient invalidation transaction leaves entries visible until commit."""
    region, _, _ = make_region()
    region.set("key", "before")

    with invalidation_transaction(region.apply):
        region.invalidate_keys("key")
        assert region.get("key") == "before"

    assert region.get("key") is NO_VALUE


def test_namespace_generation_can_be_applied_explicitly() -> None:
    """A remote namespace invalidation may set a known generation value."""
    region, _, _ = make_region()

    region.apply(Invalidation.for_namespace(region.name, generation=42))

    assert region.generation == 42


def test_region_reports_evictions_and_can_reset_and_close() -> None:
    """Lifecycle helpers expose eviction statistics and remain callable."""
    region = CacheRegion(RegionConfig(name="small", max_weight=1))
    region.set("a", 1)
    region.set("b", 2)

    assert region.statistics().evictions == 1
    region.reset_statistics()
    assert region.statistics().evictions == 0
    region.close()


def test_listener_errors_do_not_break_cache_writes() -> None:
    """Instrumentation failures are isolated from cache behavior."""

    class BrokenListener:
        def on_event(self, event) -> None:  # type: ignore[no-untyped-def]
            raise RuntimeError("listener unavailable")

    region = CacheRegion(RegionConfig(name="test"), listener=BrokenListener())
    region.set("key", "value")

    assert region.get("key") == "value"


def test_refresh_failure_keeps_serving_the_stale_value() -> None:
    """A failed inline refresh does not prevent returning the stale entry."""
    clock = ManualClock()
    region = CacheRegion(
        RegionConfig(name="test", ttl=10, soft_ttl=5),
        clock=clock,
        refresh_runner=InlineRefreshRunner(),
    )
    region.set("key", "stale")
    clock.advance(6)

    def fail() -> str:
        raise RuntimeError("origin unavailable")

    assert region.get_or_create("key", fail) == "stale"
    assert region.statistics().load_failures == 1


def test_layered_region_reads_through_to_its_remote_backend() -> None:
    """The factory wires a local near tier over the supplied remote backend."""
    remote = MemoryBackend(name="remote")
    region = create_layered_region(
        RegionConfig(name="layered", max_weight=2), remote, near_max_weight=1
    )

    region.set("key", "value")

    assert region.get("key") == "value"


def test_bulk_write_skips_none_values_when_negative_caching_is_disabled() -> None:
    """Bulk writes honor the region's negative-caching setting."""
    region = CacheRegion(RegionConfig(name="no-negative", cache_none=False))

    region.set_multi({"missing": None})

    assert region.get("missing") is NO_VALUE


def test_async_request_scope_returns_its_memoized_value() -> None:
    """The active request scope short-circuits repeated async cache reads."""
    region, _, calls = make_region()

    async def load() -> str:
        calls.append(1)
        return "value"

    async def exercise() -> None:
        with RequestScope.activate():
            assert await region.aget_or_create("key", load) == "value"
            assert await region.aget_or_create("key", load) == "value"

    asyncio.run(exercise())
    assert len(calls) == 1


def test_cache_on_arguments_decorates_and_reuses_results() -> None:
    """The region decorator caches calls under generated argument keys."""
    region, _, calls = make_region()

    @region.cache_on_arguments()
    def load(key: str) -> str:
        calls.append(1)
        return key.upper()

    assert load("alpha") == "ALPHA"
    assert load("alpha") == "ALPHA"
    assert calls == [1]


def test_multi_read_backend_failure_returns_misses_in_fail_open_mode() -> None:
    """A fail-open backend error produces one miss marker per requested key."""
    region = CacheRegion(RegionConfig(name="broken"), backend=BrokenBackend())

    assert region.get_multi(["a", "b"]) == [NO_VALUE, NO_VALUE]


def test_direct_read_discards_an_unreadable_entry() -> None:
    """A direct read treats an obsolete serialized value as a cache miss."""
    region = CacheRegion(
        RegionConfig(name="unreadable"), serializer=UnreadableSerializer()
    )
    region.set("key", "old")

    assert region.get("key") is NO_VALUE


def test_delete_removes_a_single_key() -> None:
    region, _, _ = make_region()
    region.set("key", "value")

    region.delete("key")

    assert region.get("key") is NO_VALUE


def test_async_predicate_can_skip_storing_a_result() -> None:
    """A rejected async result is returned but not persisted."""
    region, _, _ = make_region()

    async def load() -> str:
        return "uncached"

    async def exercise() -> None:
        assert (
            await region.aget_or_create(
                "key", load, should_cache_fn=lambda value: False
            )
            == "uncached"
        )

    asyncio.run(exercise())
    assert region.get("key") is NO_VALUE


def test_empty_tag_match_and_all_scope_invalidation_are_safe() -> None:
    """No-match tags are no-ops, and an all-scope request clears entries."""
    region, _, _ = make_region()
    region.set("key", "value")

    region.apply(Invalidation.for_tags(["absent"], region=region.name))
    assert region.get("key") == "value"

    region.apply(Invalidation.for_all(region=region.name))
    assert region.get("key") is NO_VALUE


def test_refresh_is_scheduled_only_once_while_a_refresh_is_pending() -> None:
    """Repeated stale reads do not queue duplicate refresh work."""

    class QueuedRefreshRunner:
        def __init__(self) -> None:
            self.pending = []

        def submit(self, callback) -> None:  # type: ignore[no-untyped-def]
            self.pending.append(callback)

    clock = ManualClock()
    runner = QueuedRefreshRunner()
    region = CacheRegion(
        RegionConfig(name="queued", ttl=10, soft_ttl=5),
        clock=clock,
        refresh_runner=runner,
    )
    region.set("key", "stale")
    clock.advance(6)

    assert region.get_or_create("key", lambda: "fresh") == "stale"
    assert region.get_or_create("key", lambda: "fresh") == "stale"
    assert len(runner.pending) == 1

    runner.pending[0]()
    assert region.get("key") == "fresh"


def test_probabilistic_refresh_uses_early_ttl_window() -> None:
    """The early refresh decision stays false then turns true near expiry."""
    clock = ManualClock()
    region = CacheRegion(
        RegionConfig(name="early", ttl=10, early_refresh_ratio=0.5),
        clock=clock,
        rng=random.Random(0),
    )
    region.set("key", "value")
    envelope = region.get_value_metadata("key")
    assert envelope is not None

    clock.advance(4)
    assert not region._is_refresh_due(envelope.metadata)
    clock.advance(5)
    assert not region._is_refresh_due(envelope.metadata)
    clock.advance(0.9)
    assert region._is_refresh_due(envelope.metadata)


def test_load_uses_an_entry_written_before_the_loader_starts() -> None:
    """A concurrent cache fill makes the in-flight loader unnecessary."""
    region, _, _ = make_region()
    region.set("key", "already stored")

    result = region._load(
        region.compose_key("key"),
        lambda: pytest.fail("loader should not run"),
        None,
        frozenset(),
        None,
    )

    assert result == "already stored"


def test_multi_read_treats_an_unreadable_entry_as_a_miss() -> None:
    region = CacheRegion(
        RegionConfig(name="batch-unreadable"), serializer=UnreadableSerializer()
    )
    region.set("key", "old")

    assert region.get_multi(["key"]) == [NO_VALUE]


def test_usability_rejects_expired_and_incompatible_entries() -> None:
    region, clock, _ = make_region(schema_version=2)
    region.set("key", "value")
    envelope = region.get_value_metadata("key")
    assert envelope is not None

    incompatible = CachedValue(
        envelope.payload,
        replace(envelope.metadata, schema_version=1),
    )
    assert not region._is_usable(incompatible)
    clock.advance(11)
    assert not region._is_usable(envelope)


def test_zero_width_early_refresh_window_is_due_at_expiry() -> None:
    clock = ManualClock()
    region = CacheRegion(
        RegionConfig(name="zero-window", ttl=10, early_refresh_ratio=0.5),
        clock=clock,
    )
    region.set("key", "value")
    envelope = region.get_value_metadata("key")
    assert envelope is not None
    zero_width_metadata = replace(
        envelope.metadata, soft_expires_at=envelope.metadata.expires_at
    )
    clock.advance(10)

    assert region._is_refresh_due(zero_width_metadata)


def test_unknown_invalidation_scope_leaves_entries_untouched() -> None:
    region, _, _ = make_region()
    region.set("key", "value")

    region.apply(
        Invalidation(scope=cast(InvalidationScope, "UNKNOWN"), region=region.name)
    )

    assert region.get("key") == "value"
