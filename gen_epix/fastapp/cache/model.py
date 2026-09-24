"""Core value objects exchanged between regions, backends and decorators.

The module defines the miss sentinel `NO_VALUE`, the stored envelope
`CachedValue` with its `EntryMetadata`, and the declarative `RegionConfig` that
drives expiry, capacity, stampede protection, resilience and security options
of a `CacheRegion`.
"""

import random
from dataclasses import dataclass, replace
from enum import Enum
from typing import Any, Literal

from gen_epix.fastapp.cache.enum import (
    EvictionPolicyType,
    ExpiryMode,
    FailureMode,
)
from gen_epix.fastapp.cache.exc import CacheConfigurationError


class NoValue(Enum):
    """Encapsulates describing the absence of a cached value.

    A dedicated sentinel keeps a cached `None` distinguishable from a miss. The
    single member is exported as `NO_VALUE` and is falsy.
    """

    NO_VALUE = "NO_VALUE"

    def __bool__(self) -> bool:
        """Return False so that a miss can be tested directly."""
        return False

    def __repr__(self) -> str:
        """Return a short, stable representation for logs and test output."""
        return "NO_VALUE"


NO_VALUE = NoValue.NO_VALUE

CacheReturn = Any | Literal[NoValue.NO_VALUE]
"""Either a cached payload or the `NO_VALUE` miss sentinel."""


@dataclass(slots=True, frozen=True)
class EntryMetadata:
    """Encapsulates describing when and how a payload was cached.

    The metadata travels with the payload so that a shared backend can be read
    by any process without consulting local state. `generation` records the
    namespace version that was current at write time, which lets a version bump
    invalidate an unbounded key set without deleting anything.

    Attributes:
        created_at: Monotonic reading at which the payload was stored.
        stored_at: Wall-clock timestamp at which the payload was stored.
        expires_at: Monotonic reading after which the entry is unusable, or
            None when the entry never hard-expires.
        soft_expires_at: Monotonic reading after which the entry is stale but
            may still be served while a refresh runs, or None when disabled.
        tags: Labels that invalidation may target instead of the key.
        generation: Namespace version in force when the entry was written.
        schema_version: Payload layout version, used to reject entries written
            by an incompatible release.
        weight: Cost of the entry against the capacity budget of a backend.
        is_negative: Whether the payload records a known-absent origin value.
    """

    created_at: float
    stored_at: float = 0.0
    expires_at: float | None = None
    soft_expires_at: float | None = None
    tags: frozenset[str] = frozenset()
    generation: int = 0
    schema_version: int = 1
    weight: int = 1
    is_negative: bool = False

    def age(self, now: float) -> float:
        """Return the seconds elapsed since the entry was written.

        Args:
            now: The current monotonic reading.
        """
        return now - self.created_at

    def is_expired(self, now: float) -> bool:
        """Return whether the entry passed its hard expiry.

        Args:
            now: The current monotonic reading.
        """
        return self.expires_at is not None and now >= self.expires_at

    def is_stale(self, now: float) -> bool:
        """Return whether the entry passed its soft expiry but not its hard one.

        Args:
            now: The current monotonic reading.
        """
        if self.soft_expires_at is None:
            return False
        return now >= self.soft_expires_at and not self.is_expired(now)


@dataclass(slots=True)
class CachedValue:
    """Encapsulates pairing a cached payload with the metadata a region needs to judge it.

    Backends store and return this envelope unchanged; only the region
    interprets expiry, staleness and generation.

    Attributes:
        payload: The value handed back to the caller on a hit.
        metadata: The bookkeeping recorded when the payload was written.
    """

    payload: Any
    metadata: EntryMetadata

    def with_metadata(self, **changes: Any) -> "CachedValue":
        """Return a copy of this envelope with selected metadata fields replaced.

        Args:
            **changes: Field names and values accepted by `EntryMetadata`.
        """
        return CachedValue(self.payload, replace(self.metadata, **changes))


@dataclass(slots=True)
class RegionConfig:
    """Encapsulates declaring the behavior of a single cache region.

    One configuration object covers expiry, capacity, stampede protection,
    resilience and the security-relevant key composition rules, so that a region
    can be built from a settings file without any imperative wiring.

    Attributes:
        name: Region name, used as the key namespace and in statistics.
        ttl: Hard time to live in seconds, or None for entries that only leave
            through eviction or explicit invalidation.
        soft_ttl: Seconds after which an entry becomes stale and eligible for a
            background refresh while still being served. Must not exceed `ttl`.
        negative_ttl: Time to live applied to known-absent origin values. Falls
            back to `ttl` when None.
        jitter_ratio: Fraction of `ttl` used to randomize expiry so that
            entries written together do not expire together.
        early_refresh_ratio: Fraction of the remaining lifetime within which a
            reader may probabilistically trigger an early refresh.
        max_weight: Capacity budget of the default in-memory backend.
        eviction_policy: Strategy used to choose a victim when full.
        expiry_mode: Whether expiry is measured from write or from last access.
        cache_none: Whether a `None` result from a loader is cached.
        cache_exceptions: Exception types whose instances are cached as
            negative entries instead of propagating on every call.
        failure_mode: Whether backend errors degrade to the loader or surface.
        operation_timeout: Seconds allowed for a single backend call, or None
            to wait indefinitely.
        schema_version: Payload layout version written into every entry.
        key_prefix: String prepended to every backend key.
        scope_parts: Names of scope attributes, such as a tenant or principal
            identifier, that must be present in every key. A region with a
            non-empty value refuses to build a key when a part is missing,
            which prevents cross-principal reuse of cached results.
        enabled: Whether the region caches at all. A disabled region behaves
            like a pass-through, which makes cached and uncached runs
            comparable in tests.
    """

    name: str
    ttl: float | None = None
    soft_ttl: float | None = None
    negative_ttl: float | None = None
    jitter_ratio: float = 0.0
    early_refresh_ratio: float = 0.0
    max_weight: int = 1024
    eviction_policy: EvictionPolicyType = EvictionPolicyType.LRU
    expiry_mode: ExpiryMode = ExpiryMode.AFTER_WRITE
    cache_none: bool = True
    cache_exceptions: tuple[type[BaseException], ...] = ()
    failure_mode: FailureMode = FailureMode.FAIL_OPEN
    operation_timeout: float | None = None
    schema_version: int = 1
    key_prefix: str = ""
    scope_parts: tuple[str, ...] = ()
    enabled: bool = True

    def __post_init__(self) -> None:
        """Reject configurations whose expiry or capacity settings conflict.

        Raises:
            CacheConfigurationError: If a time or ratio is negative, if
                `soft_ttl` exceeds `ttl`, or if `max_weight` is not positive.
        """
        if not self.name:
            raise CacheConfigurationError("A region requires a non-empty name")
        for attribute in ("ttl", "soft_ttl", "negative_ttl", "operation_timeout"):
            value = getattr(self, attribute)
            if value is not None and value <= 0:
                raise CacheConfigurationError(f"{attribute} must be positive")
        for attribute in ("jitter_ratio", "early_refresh_ratio"):
            value = getattr(self, attribute)
            if not 0.0 <= value < 1.0:
                raise CacheConfigurationError(f"{attribute} must be in [0, 1)")
        if self.soft_ttl is not None and self.ttl is not None:
            if self.soft_ttl > self.ttl:
                raise CacheConfigurationError("soft_ttl must not exceed ttl")
        if self.soft_ttl is not None and self.ttl is None:
            raise CacheConfigurationError("soft_ttl requires a ttl")
        if self.max_weight <= 0:
            raise CacheConfigurationError("max_weight must be positive")
        if self.schema_version < 1:
            raise CacheConfigurationError("schema_version must be at least 1")

    def resolve_ttl(
        self,
        override: float | None = None,
        is_negative: bool = False,
    ) -> float | None:
        """Return the hard time to live that applies to one write.

        Args:
            override: A per-call time to live that supersedes the region value.
            is_negative: Whether the value records a known-absent origin value,
                in which case `negative_ttl` applies when configured.

        Returns:
            The time to live in seconds, or None when the entry does not
            hard-expire.
        """
        if override is not None:
            return override
        if is_negative and self.negative_ttl is not None:
            return self.negative_ttl
        return self.ttl

    def apply_jitter(
        self,
        ttl: float | None,
        rng: random.Random | None = None,
    ) -> float | None:
        """Return `ttl` shortened by a random fraction of itself.

        Spreading expiry over a window prevents a batch of entries written in
        one request from expiring simultaneously and stampeding the origin.

        Args:
            ttl: The nominal time to live, or None to leave unchanged.
            rng: Random source, injectable so that tests stay deterministic.

        Returns:
            The jittered time to live, or None when `ttl` is None.
        """
        if ttl is None or self.jitter_ratio == 0.0:
            return ttl
        source = rng if rng is not None else random
        return ttl * (1.0 - source.random() * self.jitter_ratio)
