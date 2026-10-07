"""Tests for the non-caching backend."""

from gen_epix.fastapp.cache.backend.null import NullBackend
from gen_epix.fastapp.cache.model import NO_VALUE, CachedValue, EntryMetadata


def test_the_null_backend_never_stores_anything() -> None:
    """A null backend remains a pass-through for every operation."""
    backend = NullBackend()
    value = CachedValue(1, EntryMetadata(created_at=0.0))

    backend.set("a", value)

    assert backend.get("a") is NO_VALUE
    assert not backend.contains("a")
    assert list(backend.keys()) == []
    assert backend.get_multi(["a", "b"]) == [NO_VALUE, NO_VALUE]