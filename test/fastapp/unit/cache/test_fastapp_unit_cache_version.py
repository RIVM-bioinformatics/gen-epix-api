"""Tests for cache namespace generations."""

from gen_epix.fastapp.cache.version import MemoryVersionStore


def test_a_generation_never_moves_backwards() -> None:
    """Adopting an older generation must not make orphaned keys addressable."""
    store = MemoryVersionStore()
    store.bump("cases")
    store.bump("cases")

    store.set("cases", 1)

    assert store.get("cases") == 2
