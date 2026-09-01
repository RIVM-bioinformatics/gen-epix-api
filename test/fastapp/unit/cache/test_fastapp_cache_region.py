"""Tests for the read, write and expiry behavior of a cache region."""

import threading
import time

import pytest

from gen_epix.fastapp.cache.backend.base import CacheBackend
from gen_epix.fastapp.cache.clock import ManualClock
from gen_epix.fastapp.cache.enum import CacheOperation, FailureMode
from gen_epix.fastapp.cache.exc import (
    CacheBackendError,
    CacheConfigurationError,
    CantDeserializeError,
    KeyRejectedError,
)
from gen_epix.fastapp.cache.lock import InlineRefreshRunner
from gen_epix.fastapp.cache.model import NO_VALUE, CachedValue, RegionConfig
from gen_epix.fastapp.cache.region import CacheRegion
from gen_epix.fastapp.cache.resilience import FailurePolicy
from gen_epix.fastapp.cache.scope import ContextVarScopeProvider, RequestScope
from gen_epix.fastapp.cache.serializer import DeepCopySerializer, Serializer
from gen_epix.fastapp.cache.stats import RecordingListener


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
