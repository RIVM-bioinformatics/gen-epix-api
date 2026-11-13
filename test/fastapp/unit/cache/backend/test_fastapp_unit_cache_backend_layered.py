"""Tests for the layered cache backend."""

import pytest

from gen_epix.fastapp.cache.backend.layered import LayeredBackend
from gen_epix.fastapp.cache.backend.memory import MemoryBackend
from gen_epix.fastapp.cache.backend.null import NullBackend
from gen_epix.fastapp.cache.lock import ThreadMutex
from gen_epix.fastapp.cache.model import NO_VALUE, CachedValue, EntryMetadata


@pytest.fixture(name="backend_pair")
def create_backend_pair() -> tuple[LayeredBackend, MemoryBackend, MemoryBackend]:
    """Create a layered backend with two independent in-memory tiers."""
    near = MemoryBackend()
    remote = MemoryBackend()
    return LayeredBackend(near, remote), near, remote


def _cached_value(payload: str) -> CachedValue:
    return CachedValue(payload, EntryMetadata(created_at=0.0))


def test_single_reads_use_near_tier_and_promote_remote_hits(
    backend_pair: tuple[LayeredBackend, MemoryBackend, MemoryBackend],
) -> None:
    """Serve near hits directly and promote remote hits to the near tier."""
    layered, near, remote = backend_pair
    near_value = _cached_value("near")
    remote_value = _cached_value("remote")
    near.set("near-key", near_value)
    remote.set("remote-key", remote_value)

    assert layered.get("near-key") is near_value
    assert layered.get("remote-key") is remote_value
    assert near.get("remote-key") is remote_value
    assert layered.get("missing") is NO_VALUE


def test_batch_reads_preserve_order_duplicates_and_promote_hits(
    backend_pair: tuple[LayeredBackend, MemoryBackend, MemoryBackend],
) -> None:
    """Preserve batch order and duplicates while promoting remote hits."""
    layered, near, remote = backend_pair
    near_value = _cached_value("near")
    remote_value = _cached_value("remote")
    near.set("near-key", near_value)
    remote.set("remote-key", remote_value)

    assert layered.get_multi(
        iter(["remote-key", "near-key", "missing", "remote-key"])
    ) == [remote_value, near_value, NO_VALUE, remote_value]
    assert near.get("remote-key") is remote_value
    assert layered.get_multi(iter([])) == []


def test_reads_do_not_promote_when_promotion_is_disabled() -> None:
    """Leave remote hits out of the near tier when promotion is disabled."""
    near = MemoryBackend()
    remote = MemoryBackend()
    layered = LayeredBackend(near, remote, promote=False)
    value = _cached_value("remote")
    remote.set("key", value)

    assert layered.get("key") is value
    assert layered.get_multi(["key"]) == [value]
    assert near.get("key") is NO_VALUE


def test_writes_and_deletions_update_both_tiers(
    backend_pair: tuple[LayeredBackend, MemoryBackend, MemoryBackend],
) -> None:
    """Apply single and batch writes and deletions to both tiers."""
    layered, near, remote = backend_pair
    first = _cached_value("first")
    second = _cached_value("second")
    layered.set("first-key", first)
    layered.set_multi({"second-key": second})

    for backend in (near, remote):
        assert backend.get("first-key") is first
        assert backend.get("second-key") is second

    layered.delete("first-key")
    layered.delete_multi(iter(["second-key", "absent", "second-key"]))

    for backend in (near, remote):
        assert backend.get("first-key") is NO_VALUE
        assert backend.get("second-key") is NO_VALUE


def test_contains_keys_and_near_invalidation_respect_tier_ownership(
    backend_pair: tuple[LayeredBackend, MemoryBackend, MemoryBackend],
) -> None:
    """Check combined presence and ensure invalidation only removes near data."""
    layered, near, remote = backend_pair
    near.set("near-only", _cached_value("near"))
    remote.set("remote-key", _cached_value("remote"))

    assert layered.contains("near-only")
    assert layered.contains("remote-key")
    assert not layered.contains("missing")
    assert list(layered.keys()) == ["remote-key"]

    layered.invalidate_near("remote-key")

    assert near.get("remote-key") is NO_VALUE
    assert remote.get("remote-key") is not NO_VALUE
    assert layered.get_mutex("key") is not None


def test_clear_near_clear_statistics_and_close(
    backend_pair: tuple[LayeredBackend, MemoryBackend, MemoryBackend],
) -> None:
    """Aggregate tier statistics and delegate near-only and full lifecycle calls."""
    layered, near, remote = backend_pair
    layered.set("key", _cached_value("value"))
    layered.get("key")
    layered.get("missing")

    statistics = layered.statistics()
    assert statistics.hits == 1
    assert statistics.misses == 2
    assert statistics.sets == 2

    layered.clear_near()
    assert near.get("key") is NO_VALUE
    assert remote.get("key") is not NO_VALUE

    layered.clear()
    assert near.get("key") is NO_VALUE
    assert remote.get("key") is NO_VALUE

    near.set("key", _cached_value("near"))
    remote.set("key", _cached_value("remote"))
    layered.close()
    assert near.get("key") is NO_VALUE
    assert remote.get("key") is NO_VALUE


def test_mutex_falls_back_to_the_near_tier() -> None:
    """Return the near mutex when the remote tier does not provide one."""
    near = MemoryBackend()
    remote = NullBackend()
    layered = LayeredBackend(near, remote)

    assert layered.get_mutex("key") is not None


def test_mutex_prefers_the_remote_tier(monkeypatch: pytest.MonkeyPatch) -> None:
    """Return the shared mutex when both tiers provide one."""
    near = MemoryBackend()
    remote = MemoryBackend()
    layered = LayeredBackend(near, remote)
    near_mutex = ThreadMutex()
    remote_mutex = ThreadMutex()
    monkeypatch.setattr(near, "get_mutex", lambda _key: near_mutex)
    monkeypatch.setattr(remote, "get_mutex", lambda _key: remote_mutex)

    assert layered.get_mutex("key") is remote_mutex
