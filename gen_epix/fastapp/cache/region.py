"""The cache region: the single place where all cache concerns come together.

A `CacheRegion` owns one backend and applies, in order, the request scope, the
key composition rules, the generation, the invalidation cut-offs, expiry,
staleness, stampede protection, negative caching, resilience and
instrumentation. Everything a caller needs is reachable from a region:
`get_or_create` for reads, `cache_on_arguments` for declarative caching, and
`invalidate_keys`, `invalidate_tags`, `bump_generation`, `invalidate` and
`clear` for the five progressively broader ways to remove what is no longer
true.
"""

import random
import time
from collections.abc import Callable, Iterable, Iterator, Mapping, Sequence
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any

from gen_epix.fastapp.cache.backend.base import CacheBackend
from gen_epix.fastapp.cache.backend.layered import LayeredBackend
from gen_epix.fastapp.cache.backend.memory import MemoryBackend
from gen_epix.fastapp.cache.clock import Clock, SystemClock
from gen_epix.fastapp.cache.enum import (
    CacheOperation,
    InvalidationMode,
    InvalidationScope,
    RemovalCause,
)
from gen_epix.fastapp.cache.exc import CantDeserializeError, KeyRejectedError
from gen_epix.fastapp.cache.invalidation import (
    Invalidation,
    InvalidationBus,
    InvalidationStrategy,
)
from gen_epix.fastapp.cache.key import KeySpec, compose_key
from gen_epix.fastapp.cache.lock import (
    AsyncSingleFlight,
    InlineRefreshRunner,
    RefreshRunner,
    SingleFlight,
)
from gen_epix.fastapp.cache.model import (
    NO_VALUE,
    CachedValue,
    EntryMetadata,
    NoValue,
    RegionConfig,
)
from gen_epix.fastapp.cache.resilience import FailurePolicy, TimeoutGuard
from gen_epix.fastapp.cache.scope import NullScopeProvider, RequestScope, ScopeProvider
from gen_epix.fastapp.cache.serializer import IdentitySerializer, Serializer
from gen_epix.fastapp.cache.stats import (
    CacheEvent,
    CacheListener,
    CacheStatistics,
    InMemoryStatsRecorder,
    StatsRecorder,
)
from gen_epix.fastapp.cache.tag import MemoryTagIndex, TagIndex
from gen_epix.fastapp.cache.transaction import enlist
from gen_epix.fastapp.cache.version import MemoryVersionStore, VersionStore

_DISABLED_REGIONS: ContextVar[frozenset[str]] = ContextVar(
    "gen_epix_cache_disabled_regions", default=frozenset()
)


class CachedError:
    """Encapsulates holding an exception that was cached instead of being retried.

    Caching a failure protects an origin that is already struggling, at the
    price of repeating the same error to every caller until the entry expires.
    A region only does this for exception types the configuration lists.

    Attributes:
        exception: The exception raised by the loader.
    """

    __slots__ = ("exception",)

    def __init__(self, exception: BaseException):
        """Initialize a CachedError instance."""
        self.exception = exception


class CacheRegion:
    """Encapsulates applying one coherent caching policy to a named group of entries.

    A region is created with a `RegionConfig` and, optionally, replacements for
    each collaborator. It is safe for concurrent use. All keys handed to the
    public methods are logical: the region prepends the configured prefix, its
    own name, the current generation and the required scope parts before the
    backend sees them, so two regions and two principals never collide.

    Reads never fail because of the cache. A backend error is routed through the
    failure policy, which by default degrades to the loader. A stored value that
    the current release cannot deserialize is treated as a miss and replaced.

    Attributes:
        config: The declarative policy of this region.
        backend: The store holding the entries.
        clock: Time source used for every expiry decision.
        dependency_key: Namespace under which the generation is tracked.
    """

    def __init__(
        self,
        config: RegionConfig,
        backend: CacheBackend | None = None,
        serializer: Serializer | None = None,
        clock: Clock | None = None,
        scope_provider: ScopeProvider | None = None,
        version_store: VersionStore | None = None,
        tag_index: TagIndex | None = None,
        stats_recorder: StatsRecorder | None = None,
        listener: CacheListener | None = None,
        failure_policy: FailurePolicy | None = None,
        refresh_runner: RefreshRunner | None = None,
        bus: InvalidationBus | None = None,
        weigher: Callable[[Any], int] | None = None,
        key_admission: Callable[[str], bool] | None = None,
        rng: random.Random | None = None,
    ):
        """Initialize a CacheRegion instance.

        Args:
            config: The declarative policy of this region.
            backend: The store to use. When omitted, a `MemoryBackend` sized and
                configured from `config` is created and wired to keep the tag
                index in step with evictions.
            serializer: Conversion applied to payloads. Defaults to storing live
                references, which is fastest but shares mutable objects with
                callers.
            clock: Time source, injectable for deterministic tests.
            scope_provider: Source of the identity parts required by
                `config.scope_parts`.
            version_store: Holder of the region generation.
            tag_index: Index translating tags into keys.
            stats_recorder: Counter sink. Defaults to an in-memory recorder.
            listener: Observer of cache events.
            failure_policy: Behavior on backend errors. Defaults to fail-open.
            refresh_runner: Where a background refresh of a stale entry runs.
                Defaults to running it on the calling thread.
            bus: Propagates invalidation to other processes. When supplied, the
                region subscribes so that requests from elsewhere are applied.
            weigher: Capacity cost of a payload. Defaults to one per entry.
            key_admission: Predicate that may refuse a composed key, bounding a
                key space that untrusted input can influence.
            rng: Random source for jitter and probabilistic refresh.
        """
        self.config = config
        self.clock = clock if clock is not None else SystemClock()
        self._serializer = (
            serializer if serializer is not None else IdentitySerializer()
        )
        self._scope = (
            scope_provider if scope_provider is not None else NullScopeProvider()
        )
        self._versions = (
            version_store if version_store is not None else (MemoryVersionStore())
        )
        self._tags = tag_index if tag_index is not None else MemoryTagIndex()
        self._stats = (
            stats_recorder if stats_recorder is not None else (InMemoryStatsRecorder())
        )
        self._listener = listener
        self._failures = (
            failure_policy
            if failure_policy is not None
            else self._create_failure_policy()
        )
        self._refresh_runner = (
            refresh_runner if refresh_runner is not None else (InlineRefreshRunner())
        )
        self._weigher = weigher if weigher is not None else (lambda _: 1)
        self._key_admission = key_admission
        self._rng = rng if rng is not None else random.Random()
        self._single_flight = SingleFlight()
        self._async_single_flight = AsyncSingleFlight()
        self._invalidation = InvalidationStrategy(self.clock)
        self._request_scope = RequestScope()
        self.backend = backend if backend is not None else self._create_backend()
        self.dependency_key = config.name
        self._bus = bus
        if bus is not None:
            bus.subscribe(self.apply)

    @property
    def name(self) -> str:
        """Return the region name."""
        return self.config.name

    @property
    def enabled(self) -> bool:
        """Return whether the region currently caches.

        A region is disabled either permanently by configuration or temporarily
        inside a `disabling` block, which is scoped to the calling context and
        therefore safe in concurrent tests.
        """
        return self.config.enabled and self.name not in _DISABLED_REGIONS.get()

    @property
    def generation(self) -> int:
        """Return the generation currently embedded in every key."""
        return self._versions.get(self.dependency_key)

    def compose_key(self, key: str) -> str:
        """Return the backend key for a logical key.

        Args:
            key: The logical key, typically produced by a key generator.

        Returns:
            The key as the backend sees it, including prefix, region name,
            generation and required scope parts.

        Raises:
            CacheConfigurationError: If a required scope part is missing.
            KeyRejectedError: If the admission policy refuses the key.
        """
        composed = compose_key(
            (
                self.config.key_prefix,
                self.name,
                f"g{self.generation}",
                self._scope.render(self.config.scope_parts),
                key,
            )
        )
        if self._key_admission is not None and not self._key_admission(composed):
            raise KeyRejectedError(f"Cache key refused by admission policy: {key}")
        return composed

    def get(self, key: str, ignore_expiration: bool = False) -> Any | NoValue:
        """Return a cached payload without consulting a loader.

        Args:
            key: The logical key.
            ignore_expiration: Whether to return a value that passed its expiry
                or an invalidation cut-off. This is a diagnostic escape hatch.

        Returns:
            The payload, or `NO_VALUE` when nothing usable is cached.
        """
        if not self.enabled:
            return NO_VALUE
        composed = self.compose_key(key)
        entry = self._read(composed)
        if entry is None:
            self._emit(CacheOperation.GET, composed)
            return NO_VALUE
        if not ignore_expiration and not self._is_usable(entry):
            return NO_VALUE
        payload = self._decode(composed, entry)
        if payload is NO_VALUE:
            return NO_VALUE
        return self._unwrap(payload)

    def get_value_metadata(self, key: str) -> CachedValue | None:
        """Return the stored envelope for `key`, expiry included.

        The envelope exposes the creation time, tags and generation, which is
        what a diagnostic endpoint or a test needs to explain a cache decision.

        Args:
            key: The logical key.

        Returns:
            The envelope, or None when the key is absent.
        """
        entry = self._read(self.compose_key(key))
        return entry

    def get_multi(self, keys: Iterable[str]) -> list[Any | NoValue]:
        """Return several cached payloads in one backend round trip.

        Args:
            keys: The logical keys.

        Returns:
            One payload per key, using `NO_VALUE` where nothing usable exists.
        """
        ordered = list(keys)
        if not self.enabled:
            return [NO_VALUE for _ in ordered]
        composed = [self.compose_key(key) for key in ordered]
        fallback: list[CachedValue | NoValue] = [NO_VALUE for _ in composed]
        entries = self._failures.run(
            lambda: self.backend.get_multi(composed),
            fallback,
        )
        results: list[Any | NoValue] = []
        for backend_key, entry in zip(composed, entries, strict=True):
            if isinstance(entry, NoValue) or not self._is_usable(entry):
                self._stats.record("misses")
                results.append(NO_VALUE)
                continue
            payload = self._decode(backend_key, entry)
            if payload is NO_VALUE:
                results.append(NO_VALUE)
                continue
            self._stats.record("hits")
            results.append(self._unwrap(payload))
        return results

    def set(
        self,
        key: str,
        value: Any,
        ttl: float | None = None,
        tags: Iterable[str] = (),
    ) -> None:
        """Store a payload, replacing any previous entry.

        Writing in place instead of deleting removes the miss window that a
        delete would open, which matters for entries that are read constantly.

        Args:
            key: The logical key.
            value: The payload to store.
            ttl: Time to live overriding the region default.
            tags: Labels that later invalidations may target.
        """
        if not self.enabled:
            return
        composed = self.compose_key(key)
        self._write(composed, value, ttl, frozenset(tags))

    def set_multi(
        self,
        mapping: Mapping[str, Any],
        ttl: float | None = None,
    ) -> None:
        """Store several payloads in one backend round trip.

        Args:
            mapping: Logical keys and the payloads to store.
            ttl: Time to live overriding the region default.
        """
        if not self.enabled or not mapping:
            return
        envelopes: dict[str, CachedValue] = {}
        for key, value in mapping.items():
            composed = self.compose_key(key)
            envelope = self._envelope(value, ttl, frozenset())
            if envelope is not None:
                envelopes[composed] = envelope
        if envelopes:
            self._failures.run(lambda: self.backend.set_multi(envelopes), None)
            self._stats.record("sets", len(envelopes))

    def delete(self, key: str) -> None:
        """Remove one logical key.

        Args:
            key: The logical key.
        """
        self.invalidate_keys(key)

    def delete_multi(self, keys: Iterable[str]) -> None:
        """Remove several logical keys.

        Args:
            keys: The logical keys.
        """
        self.invalidate_keys(*keys)

    def get_or_create(
        self,
        key: str,
        creator: Callable[[], Any],
        ttl: float | None = None,
        tags: Iterable[str] = (),
        should_cache_fn: Callable[[Any], bool] | None = None,
    ) -> Any:
        """Return the cached payload for `key`, loading it when necessary.

        The method is the read path of the region and applies, in order: the
        request scope, the backend read, the usability checks, stale handling
        with a background refresh, and a single-flight load. Concurrent callers
        for the same key run the loader once; the others wait and receive the
        same outcome, so an expiry cannot stampede the origin.

        When the entry is stale rather than expired, the previous payload is
        returned immediately and a refresh is scheduled, which keeps the read
        fast at the cost of bounded staleness.

        Args:
            key: The logical key.
            creator: Callable producing the payload on a miss. It runs outside
                every cache lock.
            ttl: Time to live overriding the region default.
            tags: Labels attached to the stored entry.
            should_cache_fn: Predicate receiving the produced payload. When it
                returns False the payload is returned but not stored, which is
                how conditional caching of large or partial results is expressed.

        Returns:
            The cached or freshly produced payload.

        Raises:
            Exception: Whatever `creator` raised. When the configuration lists
                the exception type, the failure is cached and re-raised on later
                calls until it expires.
        """
        if not self.enabled:
            return creator()
        composed = self.compose_key(key)
        memoized = self._request_scope.get(composed, NO_VALUE)
        if memoized is not NO_VALUE:
            self._stats.record("hits")
            return self._unwrap(memoized)
        tag_set = frozenset(tags)
        entry = self._read(composed)
        if entry is not None and self._is_usable(entry):
            payload = self._decode(composed, entry)
            if payload is not NO_VALUE:
                if self._is_refresh_due(entry.metadata):
                    self._stats.record("stale_hits")
                    self._schedule_refresh(
                        composed, creator, ttl, tag_set, should_cache_fn
                    )
                else:
                    self._stats.record("hits")
                self._request_scope.set(composed, payload)
                return self._unwrap(payload)
        self._stats.record("misses")
        return self._unwrap(
            self._single_flight.run(
                composed,
                lambda: self._load(composed, creator, ttl, tag_set, should_cache_fn),
            )
        )

    async def aget_or_create(
        self,
        key: str,
        creator: Callable[[], Any],
        ttl: float | None = None,
        tags: Iterable[str] = (),
        should_cache_fn: Callable[[Any], bool] | None = None,
    ) -> Any:
        """Return the cached payload for `key`, awaiting a coroutine loader.

        The awaited counterpart of `get_or_create`. Concurrent awaits for the
        same key share one execution of `creator`; different keys proceed
        independently. Stale entries are refreshed inline on the event loop
        rather than on a worker thread, so a slow loader delays only the tasks
        already waiting for that key.

        Args:
            key: The logical key.
            creator: Callable returning an awaitable that produces the payload.
            ttl: Time to live overriding the region default.
            tags: Labels attached to the stored entry.
            should_cache_fn: Predicate deciding whether to store the payload.

        Returns:
            The cached or freshly produced payload.

        Raises:
            Exception: Whatever the awaited loader raised.
        """
        if not self.enabled:
            return await creator()
        composed = self.compose_key(key)
        memoized = self._request_scope.get(composed, NO_VALUE)
        if memoized is not NO_VALUE:
            self._stats.record("hits")
            return self._unwrap(memoized)
        tag_set = frozenset(tags)
        entry = self._read(composed)
        if entry is not None and self._is_usable(entry):
            payload = self._decode(composed, entry)
            if payload is not NO_VALUE and not self._is_refresh_due(entry.metadata):
                self._stats.record("hits")
                self._request_scope.set(composed, payload)
                return self._unwrap(payload)
        self._stats.record("misses")

        async def load() -> Any:
            """Await the loader and store the outcome.

            Returns:
                The payload produced by the awaited loader.

            Raises:
                Exception: Whatever the awaited loader raised.
            """
            started = time.monotonic()
            try:
                value = await creator()
            except self.config.cache_exceptions as exception:
                self._stats.record("load_failures")
                self._store(composed, CachedError(exception), ttl, tag_set, True)
                raise
            except Exception:
                self._stats.record("load_failures")
                raise
            self._stats.record("loads")
            self._stats.record("load_seconds", time.monotonic() - started)
            if should_cache_fn is None or should_cache_fn(value):
                self._store(composed, value, ttl, tag_set, value is None)
            self._request_scope.set(composed, value)
            return value

        return self._unwrap(await self._async_single_flight.run(composed, load))

    def get_or_create_multi(
        self,
        keys: Sequence[str],
        creator: Callable[[Sequence[str]], Sequence[Any]],
        ttl: float | None = None,
        should_cache_fn: Callable[[Any], bool] | None = None,
    ) -> list[Any]:
        """Return payloads for several keys, loading only the missing ones.

        The loader receives exactly the logical keys that were not served from
        cache and must return one payload per key, in the same order. This turns
        a partially warm batch into a single origin call instead of one call per
        miss.

        Args:
            keys: The logical keys.
            creator: Callable receiving the missing keys and returning their
                payloads in order.
            ttl: Time to live overriding the region default.
            should_cache_fn: Predicate deciding whether to store each payload.

        Returns:
            One payload per requested key, in the requested order.

        Raises:
            ValueError: If `creator` returned a different number of payloads
                than the number of keys it was asked for.
        """
        ordered = list(keys)
        if not self.enabled:
            produced = list(creator(ordered))
            _check_multi_result(ordered, produced)
            return produced
        cached = self.get_multi(ordered)
        missing = [
            key for key, value in zip(ordered, cached, strict=True) if value is NO_VALUE
        ]
        if not missing:
            return list(cached)
        produced = list(creator(missing))
        _check_multi_result(missing, produced)
        self._stats.record("loads", len(produced))
        to_store = {
            key: value
            for key, value in zip(missing, produced, strict=True)
            if should_cache_fn is None or should_cache_fn(value)
        }
        if to_store:
            self.set_multi(to_store, ttl)
        by_key = dict(zip(missing, produced, strict=True))
        return [
            by_key[key] if value is NO_VALUE else value
            for key, value in zip(ordered, cached, strict=True)
        ]

    def cache_on_arguments(
        self,
        key_spec: KeySpec | None = None,
        ttl: float | None = None,
        tags: Iterable[str] = (),
        should_cache_fn: Callable[[Any], bool] | None = None,
        condition: Callable[..., bool] | None = None,
    ) -> Callable[[Callable[..., Any]], Any]:
        """Return a decorator that caches the results of a function.

        The decorated function keeps its signature and gains the handles that
        make invalidation from elsewhere possible: `invalidate`, `set`,
        `refresh`, `get`, `key` and `original`. A coroutine function receives the
        awaitable variant.

        Args:
            key_spec: How keys are composed from the arguments. Defaults to
                keying on every parameter by name.
            ttl: Time to live overriding the region default.
            tags: Constant tags or templates over parameter names, such as
                ``"case:{case_id}"``, attached to every stored entry.
            should_cache_fn: Predicate receiving the result, deciding storage.
            condition: Predicate receiving the call arguments. When it returns
                False the cache is bypassed entirely for that call.

        Returns:
            A decorator producing a `CachedFunction` or `AsyncCachedFunction`.
        """
        from gen_epix.fastapp.cache.decorator import make_cached_function

        def decorate(fn: Callable[..., Any]) -> Any:
            """Wrap one function in a cached callable."""
            return make_cached_function(
                region=self,
                fn=fn,
                key_spec=key_spec or KeySpec(),
                ttl=ttl,
                tags=tuple(tags),
                should_cache_fn=should_cache_fn,
                condition=condition,
            )

        return decorate

    def invalidate_keys(self, *keys: str) -> int:
        """Remove specific logical keys.

        This is the narrowest and cheapest form of invalidation, but it requires
        the caller to reproduce the exact key. Prefer tags when the caller is not
        the same code that wrote the entry.

        Args:
            *keys: The logical keys to remove.

        Returns:
            The number of keys submitted for removal.
        """
        if not keys:
            return 0
        composed = frozenset(self.compose_key(key) for key in keys)
        self._dispatch(Invalidation.for_keys(composed, region=self.name))
        return len(composed)

    def invalidate_tags(
        self,
        *tags: str,
        mode: InvalidationMode = InvalidationMode.HARD,
    ) -> int:
        """Remove every entry carrying any of the given tags.

        Tags are the mechanism that lets a writer invalidate readers it does not
        know. The writer names the thing that changed; the readers declared that
        name when they cached.

        Args:
            *tags: The tags to invalidate.
            mode: Whether readers must wait for fresh data.

        Returns:
            The number of tags submitted for removal.
        """
        if not tags:
            return 0
        self._dispatch(
            Invalidation.for_tags(frozenset(tags), region=self.name, mode=mode)
        )
        return len(tags)

    def bump_generation(self) -> int:
        """Make every currently cached entry unreachable in constant time.

        Nothing is deleted: the generation embedded in future keys changes, so
        existing entries can no longer be addressed and are reclaimed later by
        expiry or eviction. This is the only affordable way to invalidate a very
        large or unenumerable key space.

        Returns:
            The new generation.
        """
        self._dispatch(Invalidation.for_namespace(self.dependency_key))
        return self.generation

    def invalidate(self, mode: InvalidationMode = InvalidationMode.HARD) -> None:
        """Mark everything written before now as invalid, without deleting it.

        A hard invalidation makes readers regenerate. A soft one lets them serve
        the previous value while one reader refreshes, which avoids a load spike
        on a busy region.

        Args:
            mode: Whether stale values may still be served.
        """
        self._dispatch(
            Invalidation(
                scope=InvalidationScope.REGION,
                region=self.name,
                mode=mode,
            )
        )

    def clear(self) -> None:
        """Delete every entry in this region."""
        self._dispatch(Invalidation.for_all(region=self.name))

    def apply(self, invalidation: Invalidation) -> None:
        """Apply an invalidation request that targets this region.

        The manager and the invalidation bus both call this, so a request made
        in another process takes effect here exactly as if it had been made
        locally. Requests aimed at a different region are ignored.

        Args:
            invalidation: The request to apply.
        """
        if invalidation.region not in (None, self.name):
            return
        match invalidation.scope:
            case InvalidationScope.KEY:
                self._failures.run(
                    lambda: self.backend.delete_multi(invalidation.keys), None
                )
                for key in invalidation.keys:
                    self._tags.discard_key(key)
                    self._request_scope.discard(key)
                self._stats.record("invalidations", len(invalidation.keys))
            case InvalidationScope.TAG:
                removed: set[str] = set()
                for tag in invalidation.tags:
                    removed |= self._tags.pop_tag(tag)
                if removed:
                    self._failures.run(lambda: self.backend.delete_multi(removed), None)
                    for key in removed:
                        self._request_scope.discard(key)
                self._stats.record("invalidations", len(removed))
            case InvalidationScope.NAMESPACE:
                namespace = invalidation.namespace or self.dependency_key
                if invalidation.generation is not None:
                    self._versions.set(namespace, invalidation.generation)
                else:
                    self._versions.bump(namespace)
                self._tags.clear()
                self._request_scope.clear()
                self._stats.record("invalidations")
            case InvalidationScope.REGION:
                self._invalidation.invalidate(invalidation.mode)
                self._request_scope.clear()
                self._stats.record("invalidations")
            case InvalidationScope.ALL:
                self._failures.run(self.backend.clear, None)
                self._tags.clear()
                self._request_scope.clear()
                self._stats.record("invalidations")
        self._emit(CacheOperation.INVALIDATE, detail=invalidation)

    @contextmanager
    def disabling(self) -> Iterator["CacheRegion"]:
        """Bypass this region for the duration of the block.

        The region behaves as a pass-through inside the block, which is how a
        test proves that a result is identical with and without caching, and how
        a caller forces a read through to the origin.

        Yields:
            This region, for convenience.
        """
        token = _DISABLED_REGIONS.set(_DISABLED_REGIONS.get() | {self.name})
        try:
            yield self
        finally:
            _DISABLED_REGIONS.reset(token)

    def warm(self, mapping: Mapping[str, Any], ttl: float | None = None) -> None:
        """Populate the region before the first request arrives.

        Args:
            mapping: Logical keys and the payloads to store.
            ttl: Time to live overriding the region default.
        """
        self.set_multi(mapping, ttl)

    def statistics(self) -> CacheStatistics:
        """Return the counters observed by this region."""
        return self._stats.snapshot()

    def reset_statistics(self) -> None:
        """Set the counters of this region back to zero."""
        self._stats.reset()

    def close(self) -> None:
        """Release the resources held by the region and its backend."""
        self.backend.close()

    def _create_failure_policy(self) -> FailurePolicy:
        """Return the default failure policy implied by the configuration.

        A configured operation timeout is only effective when something bounds
        each backend call, so the policy is given a guard whenever the
        configuration declares one.
        """
        guard = (
            TimeoutGuard(self.config.operation_timeout)
            if self.config.operation_timeout is not None
            else None
        )
        return FailurePolicy(mode=self.config.failure_mode, guard=guard)

    def _create_backend(self) -> CacheBackend:
        """Return the default in-memory backend wired to the tag index."""
        return MemoryBackend(
            max_weight=self.config.max_weight,
            eviction=self.config.eviction_policy,
            clock=self.clock,
            removal_listener=self._on_removal,
            name=f"{self.config.name}-memory",
        )

    def _on_removal(
        self,
        key: str,
        value: CachedValue,
        cause: RemovalCause,
    ) -> None:
        """Keep the tag index and statistics in step with backend removals.

        Args:
            key: The removed backend key.
            value: The removed envelope.
            cause: Why the entry left.
        """
        if cause is not RemovalCause.REPLACED:
            self._tags.discard_key(key)
        if cause is RemovalCause.SIZE:
            self._stats.record("evictions")
        elif cause is RemovalCause.EXPIRED:
            self._stats.record("expirations")
        self._emit(CacheOperation.DELETE, key, cause)

    def _read(self, composed: str) -> CachedValue | None:
        """Read one envelope through the failure policy.

        Args:
            composed: The backend key.

        Returns:
            The envelope, or None on a miss or an absorbed backend error.
        """
        fallback: CachedValue | NoValue = NO_VALUE
        entry = self._failures.run(lambda: self.backend.get(composed), fallback)
        return None if isinstance(entry, NoValue) else entry

    def _is_usable(self, entry: CachedValue) -> bool:
        """Return whether an envelope may be served.

        An entry is unusable when it expired, when it predates a hard
        invalidation cut-off, or when it was written under a different payload
        schema.

        Args:
            entry: The envelope read from the backend.
        """
        now = self.clock.monotonic()
        if entry.metadata.is_expired(now):
            return False
        if entry.metadata.schema_version != self.config.schema_version:
            return False
        return not self._invalidation.is_hard_invalidated(entry.metadata.created_at)

    def _is_refresh_due(self, metadata: EntryMetadata) -> bool:
        """Return whether a usable entry should be refreshed in the background.

        A soft time to live makes the decision deterministic once the entry is
        stale. Without one, `early_refresh_ratio` makes it probabilistic and the
        probability rises as the hard expiry approaches, so that concurrent
        readers do not all decide to refresh at the same moment.

        Args:
            metadata: The metadata of the entry being served.
        """
        now = self.clock.monotonic()
        if self._invalidation.is_soft_invalidated(metadata.created_at):
            return True
        if metadata.soft_expires_at is None or now < metadata.soft_expires_at:
            return False
        if self.config.soft_ttl is not None or metadata.expires_at is None:
            return True
        window = metadata.expires_at - metadata.soft_expires_at
        if window <= 0:
            return True
        progress = (now - metadata.soft_expires_at) / window
        return self._rng.random() < progress

    def _schedule_refresh(
        self,
        composed: str,
        creator: Callable[[], Any],
        ttl: float | None,
        tags: frozenset[str],
        should_cache_fn: Callable[[Any], bool] | None,
    ) -> None:
        """Refresh a stale entry without making the current caller wait.

        Only one refresh per key is started; a second reader that arrives while
        one is running simply keeps serving the stale value.

        Args:
            composed: The backend key.
            creator: Callable producing the fresh payload.
            ttl: Time to live overriding the region default.
            tags: Labels attached to the refreshed entry.
            should_cache_fn: Predicate deciding whether to store the payload.
        """
        if not self._single_flight.try_start(composed):
            return

        def refresh() -> None:
            """Run the loader and replace the stale entry, absorbing failures."""
            try:
                self._load(composed, creator, ttl, tags, should_cache_fn)
            except Exception:  # noqa: BLE001 - a stale value is still being served
                pass
            finally:
                self._single_flight.finish(composed)

        self._emit(CacheOperation.REFRESH, composed)
        self._refresh_runner.submit(refresh)

    def _load(
        self,
        composed: str,
        creator: Callable[[], Any],
        ttl: float | None,
        tags: frozenset[str],
        should_cache_fn: Callable[[Any], bool] | None,
    ) -> Any:
        """Run the loader once and store its outcome.

        The cache is re-read first, because a caller that waited on the single
        flight of a different key, or that lost a race, may find the value
        already present and can skip the origin entirely.

        Args:
            composed: The backend key.
            creator: Callable producing the payload.
            ttl: Time to live overriding the region default.
            tags: Labels attached to the stored entry.
            should_cache_fn: Predicate deciding whether to store the payload.

        Returns:
            The produced payload.

        Raises:
            Exception: Whatever `creator` raised. A cacheable exception type is
                stored as a negative entry before being re-raised.
        """
        entry = self._read(composed)
        if entry is not None and self._is_usable(entry):
            payload = self._decode(composed, entry)
            if payload is not NO_VALUE and not self._is_refresh_due(entry.metadata):
                return payload
        started = time.monotonic()
        try:
            value = creator()
        except self.config.cache_exceptions as exception:
            self._stats.record("load_failures")
            self._store(composed, CachedError(exception), ttl, tags, True)
            raise
        except Exception:
            self._stats.record("load_failures")
            raise
        self._stats.record("loads")
        self._stats.record("load_seconds", time.monotonic() - started)
        if should_cache_fn is None or should_cache_fn(value):
            self._store(composed, value, ttl, tags, value is None)
        self._request_scope.set(composed, value)
        self._emit(CacheOperation.LOAD, composed)
        return value

    def _write(
        self,
        composed: str,
        value: Any,
        ttl: float | None,
        tags: frozenset[str],
    ) -> None:
        """Store a payload under an already composed key.

        Args:
            composed: The backend key.
            value: The payload to store.
            ttl: Time to live overriding the region default.
            tags: Labels attached to the stored entry.
        """
        self._store(composed, value, ttl, tags, value is None)
        self._request_scope.set(composed, value)

    def _store(
        self,
        composed: str,
        value: Any,
        ttl: float | None,
        tags: frozenset[str],
        is_negative: bool,
    ) -> None:
        """Write one envelope, honoring the negative-caching configuration.

        Args:
            composed: The backend key.
            value: The payload, possibly a `CachedError`.
            ttl: Time to live overriding the region default.
            tags: Labels attached to the stored entry.
            is_negative: Whether the payload records an absent or failed result.
        """
        envelope = self._envelope(value, ttl, tags, is_negative)
        if envelope is None:
            return
        self._failures.run(lambda: self.backend.set(composed, envelope), None)
        if tags:
            self._tags.add(composed, tags)
        self._stats.record("sets")
        self._emit(CacheOperation.SET, composed)

    def _envelope(
        self,
        value: Any,
        ttl: float | None,
        tags: frozenset[str],
        is_negative: bool = False,
    ) -> CachedValue | None:
        """Build the envelope for a payload, or None when it must not be cached.

        Args:
            value: The payload to wrap.
            ttl: Time to live overriding the region default.
            tags: Labels attached to the entry.
            is_negative: Whether the payload records an absent or failed result.

        Returns:
            The envelope, or None when the configuration forbids caching a
            `None` result.
        """
        if value is None and not self.config.cache_none:
            return None
        effective_ttl = self.config.apply_jitter(
            self.config.resolve_ttl(ttl, is_negative), self._rng
        )
        now = self.clock.monotonic()
        expires_at = None if effective_ttl is None else now + effective_ttl
        soft_expires_at = self._soft_expiry(now, effective_ttl)
        metadata = EntryMetadata(
            created_at=now,
            stored_at=self.clock.time(),
            expires_at=expires_at,
            soft_expires_at=soft_expires_at,
            tags=tags,
            generation=self.generation,
            schema_version=self.config.schema_version,
            weight=max(1, self._weigher(value)),
            is_negative=is_negative,
        )
        return CachedValue(self._serializer.dumps(value), metadata)

    def _soft_expiry(self, now: float, ttl: float | None) -> float | None:
        """Return the moment at which an entry becomes eligible for refresh.

        Args:
            now: The write time.
            ttl: The effective hard time to live, if any.

        Returns:
            The soft expiry, or None when neither a soft time to live nor an
            early refresh ratio is configured.
        """
        if self.config.soft_ttl is not None:
            return now + self.config.soft_ttl
        if ttl is not None and self.config.early_refresh_ratio > 0:
            return now + ttl * (1.0 - self.config.early_refresh_ratio)
        return None

    def _decode(self, composed: str, entry: CachedValue) -> Any | NoValue:
        """Return the payload of an envelope, discarding unreadable entries.

        Args:
            composed: The backend key, used to drop an unreadable entry.
            entry: The envelope read from the backend.

        Returns:
            The payload, or `NO_VALUE` when the entry could not be read and was
            therefore removed so that the next call regenerates it.
        """
        try:
            return self._serializer.loads(entry.payload)
        except CantDeserializeError:
            self._failures.run(lambda: self.backend.delete(composed), None)
            self._tags.discard_key(composed)
            self._stats.record("misses")
            return NO_VALUE

    def _unwrap(self, payload: Any) -> Any:
        """Return a payload, re-raising a cached exception.

        Args:
            payload: The decoded payload.

        Returns:
            The payload itself when it is not a recorded failure.

        Raises:
            BaseException: The exception recorded by a previous failed load.
        """
        if isinstance(payload, CachedError):
            raise payload.exception
        return payload

    def _dispatch(self, invalidation: Invalidation) -> None:
        """Route an invalidation request to the transaction, bus or region.

        An open invalidation transaction takes precedence, so nothing is
        invalidated before the surrounding unit of work commits. Otherwise the
        request goes to the bus when one is configured, which delivers it back
        to this region as well as to every other process.

        Args:
            invalidation: The request to route.
        """
        if enlist(invalidation):
            return
        if self._bus is not None:
            self._bus.publish(invalidation)
            return
        self.apply(invalidation)

    def _emit(
        self,
        operation: CacheOperation,
        key: str | None = None,
        cause: RemovalCause | None = None,
        detail: Any = None,
    ) -> None:
        """Notify the listener, absorbing its failures.

        Args:
            operation: The operation that occurred.
            key: The backend key involved, when there is one.
            cause: Why an entry was removed, for removal events.
            detail: Extra context such as the invalidation request.
        """
        if self._listener is None:
            return
        try:
            self._listener.on_event(
                CacheEvent(self.name, operation, key, cause, detail)
            )
        except Exception:  # noqa: BLE001 - instrumentation must not break reads
            return


def _check_multi_result(keys: Sequence[str], values: Sequence[Any]) -> None:
    """Verify that a multi-key loader returned one payload per key.

    Args:
        keys: The keys the loader was asked for.
        values: The payloads it returned.

    Raises:
        ValueError: If the counts differ, which would silently misalign
            payloads with keys.
    """
    if len(keys) != len(values):
        raise ValueError(f"Loader returned {len(values)} values for {len(keys)} keys")


def create_layered_region(
    config: RegionConfig,
    remote: CacheBackend,
    near_max_weight: int | None = None,
    **kwargs: Any,
) -> CacheRegion:
    """Build a region whose backend is a near tier over a shared store.

    Args:
        config: The declarative policy of the region.
        remote: The shared store forming the second tier.
        near_max_weight: Capacity of the near tier, defaulting to the capacity
            declared in `config`.
        **kwargs: Further collaborators forwarded to `CacheRegion`.

    Returns:
        A region reading from a local tier and falling back to `remote`.
    """
    near = MemoryBackend(
        max_weight=near_max_weight or config.max_weight,
        eviction=config.eviction_policy,
        name=f"{config.name}-near",
    )
    backend = LayeredBackend(near=near, remote=remote, name=f"{config.name}-layered")
    return CacheRegion(config, backend=backend, **kwargs)
