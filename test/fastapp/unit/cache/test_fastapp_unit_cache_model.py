"""Tests for cache value objects and region configuration."""

import random

import pytest

from gen_epix.fastapp.cache.exc import CacheConfigurationError
from gen_epix.fastapp.cache.model import (
    NO_VALUE,
    CachedValue,
    EntryMetadata,
    RegionConfig,
)


def test_no_value_is_falsy_and_has_stable_representation() -> None:
    """Keep cache misses distinct from cached falsey payloads."""
    assert not NO_VALUE
    assert repr(NO_VALUE) == "NO_VALUE"
    assert NO_VALUE is not None


def test_entry_metadata_expiry_and_staleness_boundaries() -> None:
    """Treat expiry instants as inclusive and stale entries as not expired."""
    metadata = EntryMetadata(
        created_at=10.0,
        expires_at=20.0,
        soft_expires_at=15.0,
    )

    assert metadata.age(13.0) == 3.0
    assert not metadata.is_expired(19.9)
    assert metadata.is_expired(20.0)
    assert not metadata.is_stale(14.9)
    assert metadata.is_stale(15.0)
    assert not metadata.is_stale(20.0)


def test_cached_value_with_metadata_returns_an_independent_envelope() -> None:
    """Replace selected metadata without mutating the original envelope."""
    original = CachedValue("payload", EntryMetadata(created_at=1.0, generation=2))

    updated = original.with_metadata(generation=3)

    assert updated.payload == original.payload
    assert updated.metadata.generation == 3
    assert original.metadata.generation == 2


@pytest.mark.parametrize(
    ("settings", "message"),
    [
        ({"name": ""}, "non-empty name"),
        ({"ttl": 0}, "ttl must be positive"),
        ({"soft_ttl": 1}, "soft_ttl requires a ttl"),
        ({"ttl": 1, "soft_ttl": 2}, "soft_ttl must not exceed ttl"),
        ({"max_weight": 0}, "max_weight must be positive"),
        ({"schema_version": 0}, "schema_version must be at least 1"),
        ({"jitter_ratio": 1}, "jitter_ratio must be in [0, 1)"),
        ({"early_refresh_ratio": -0.1}, "early_refresh_ratio must be in [0, 1)"),
    ],
)
def test_region_config_rejects_invalid_settings(
    settings: dict[str, object], message: str
) -> None:
    """Reject invalid durations, ratios, capacity, and soft expiry settings."""
    config_settings = {"name": "test", **settings}

    with pytest.raises(CacheConfigurationError) as error:
        RegionConfig(**config_settings)  # type: ignore[arg-type]

    assert message in str(error.value)


def test_resolve_ttl_prefers_override_then_negative_ttl() -> None:
    """Select per-write TTLs before negative-value and region defaults."""
    config = RegionConfig(name="test", ttl=20.0, negative_ttl=5.0)

    assert config.resolve_ttl() == 20.0
    assert config.resolve_ttl(is_negative=True) == 5.0
    assert config.resolve_ttl(override=3.0, is_negative=True) == 3.0
    assert RegionConfig(name="unbounded").resolve_ttl() is None


def test_apply_jitter_is_deterministic_and_preserves_unbounded_ttl() -> None:
    """Shorten finite TTLs by the configured random fraction only."""
    config = RegionConfig(name="test", jitter_ratio=0.2)

    assert config.apply_jitter(None, random.Random(0)) is None
    assert config.apply_jitter(10.0, random.Random(0)) == pytest.approx(
        10.0 * (1.0 - random.Random(0).random() * 0.2)
    )
