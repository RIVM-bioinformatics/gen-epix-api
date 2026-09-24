# `gen_epix.fastapp.cache`

A generic cache framework. It contains no application logic: you supply the
configuration, the regions and the dependency declarations, and it supplies key
composition, expiry, staleness, stampede protection, invalidation, propagation,
resilience and instrumentation.

- [1. Mental model](#1-mental-model)
- [2. Quick start](#2-quick-start)
- [3. Configuring a region](#3-configuring-a-region)
- [4. Reading and writing](#4-reading-and-writing)
- [5. Keys](#5-keys)
- [6. Invalidation](#6-invalidation)
- [7. Transactions](#7-transactions)
- [8. Staleness and stampedes](#8-staleness-and-stampedes)
- [9. Resilience](#9-resilience)
- [10. Observability](#10-observability)
- [11. Testing](#11-testing)
- [12. Worked example: local cache in a service](#12-worked-example-local-cache-in-a-service)
- [13. Worked example: distributed cache with Redis](#13-worked-example-distributed-cache-with-redis)
- [14. HTTP-level caching](#14-http-level-caching)
- [15. Pitfalls](#15-pitfalls)

---

## 1. Mental model

A read through `CacheRegion.get_or_create` passes through these stages, in order:

```
caller
  │
  ├─ region disabled?            → call the loader, cache nothing
  ├─ compose key                 prefix : region : generation : scope : logical key
  ├─ request scope (L0)          per-request memo, read-your-own-writes
  ├─ backend read                through the failure policy (timeout, breaker, fail-open)
  ├─ usable?                     not expired, not hard-invalidated, right schema version
  │     ├─ fresh                 → hit
  │     └─ stale                 → serve old value, schedule one background refresh
  └─ miss                        → single-flight load, store, return
```

Three objects matter:

| Object | Owns |
| --- | --- |
| `CacheManager` | the set of regions, the dependency registry, cross-region operations |
| `CacheRegion` | one caching policy plus its store; all the logic above |
| `CacheBackend` | dumb key → envelope storage, capacity and (where possible) expiry |

Everything else — serializers, clocks, tag indexes, version stores, buses, scope
providers, failure policies — is a collaborator you can replace.

---

## 2. Quick start

```python
from gen_epix.fastapp.cache import CacheManager, RegionConfig

manager = CacheManager()
region = manager.create_region(RegionConfig(name="cases", ttl=300.0, max_weight=5_000))


@region.cache_on_arguments(tags=("case:{case_id}",))
def get_case_summary(case_id: str) -> dict:
    return expensive_query(case_id)


get_case_summary("abc")          # loads
get_case_summary("abc")          # hit

get_case_summary.invalidate("abc")   # drop one entry
get_case_summary.invalidate_all()    # drop every entry of this function
region.invalidate_tags("case:abc")   # drop every entry that declared this tag
```

---

## 3. Configuring a region

`RegionConfig` is a validated dataclass; contradictory settings raise
`CacheConfigurationError` at construction rather than at the first request.

| Field | Meaning | Typical value |
| --- | --- | --- |
| `name` | region name, also the key namespace | `"cases"` |
| `ttl` | hard time to live in seconds | `300.0` |
| `soft_ttl` | after this the entry is stale and refreshed in the background while still being served; must be `<= ttl` | `240.0` |
| `negative_ttl` | separate, shorter TTL for `None` results | `30.0` |
| `jitter_ratio` | randomly shortens each TTL by up to this fraction, so entries written together do not expire together | `0.1` |
| `early_refresh_ratio` | probabilistic refresh inside the last fraction of the lifetime; ignored when `soft_ttl` is set | `0.1` |
| `max_weight` | capacity budget of the default in-memory backend | `10_000` |
| `eviction_policy` | `LRU`, `LFU`, `FIFO`, `RANDOM`, `TINY_LFU` | `LRU` |
| `cache_none` | whether an absent result is remembered | `True` |
| `cache_exceptions` | exception types cached as negative entries instead of retried | `(UpstreamUnavailable,)` |
| `failure_mode` | `FAIL_OPEN` degrades to the loader, `FAIL_CLOSED` surfaces the error | `FAIL_OPEN` |
| `operation_timeout` | seconds allowed per backend call; wires a `TimeoutGuard` into the default failure policy | `0.05` |
| `schema_version` | bump when the payload layout changes; older entries become misses | `1` |
| `key_prefix` | string prepended to every backend key | `"casedb"` |
| `scope_parts` | identity parts that **must** be present in every key | `("tenant", "principal")` |
| `enabled` | `False` turns the region into a pass-through | `True` |

From configuration files:

```python
from gen_epix.fastapp.cache import CacheManager

manager = CacheManager()
manager.configure(
    {
        "cases": {"ttl": 300.0, "max_weight": 5_000, "eviction_policy": "tiny_lfu"},
        "reference_data": {"ttl": 3600.0, "soft_ttl": 3000.0, "jitter_ratio": 0.1},
    }
)
```

Enumerated fields accept their names as strings, so a region can be described
entirely in settings.

### Disabling caching per environment

```python
RegionConfig(name="cases", ttl=300.0, enabled=settings.CACHE_ENABLED)
```

or, for a bounded scope:

```python
with manager.disabling():
    ...  # every region is a pass-through in this block
```

---

## 4. Reading and writing

### Explicit

```python
value = region.get_or_create("case:abc", lambda: load_case("abc"), tags=["case:abc"])

region.set("case:abc", value, ttl=60.0, tags=["case:abc"])
region.get("case:abc")            # NO_VALUE when nothing usable is cached
region.get_value_metadata("case:abc")   # envelope: created_at, tags, generation
region.delete("case:abc")
```

`region.get` returns the `NO_VALUE` sentinel on a miss, which is falsy but is not
`None`, so a cached `None` stays distinguishable from a miss:

```python
from gen_epix.fastapp.cache import NO_VALUE

if region.get(key) is NO_VALUE:
    ...
```

### Declarative

```python
@region.cache_on_arguments(
    ttl=60.0,
    tags=("case:{case_id}", "cases"),
    should_cache_fn=lambda result: result is not None,
    condition=lambda case_id: not case_id.startswith("tmp-"),
)
def get_case(case_id: str) -> dict | None: ...
```

- `should_cache_fn` receives the **result**: return the value but do not store it.
- `condition` receives the **arguments**: bypass the cache entirely for this call.

The decorated callable exposes the inverse operations:

| Call | Effect |
| --- | --- |
| `fn(*args)` | cached call |
| `fn.original(*args)` | bypass the cache in both directions |
| `fn.get(*args)` | read without computing |
| `fn.set(value, *args)` | publish a value without calling the function |
| `fn.refresh(*args)` | recompute and store |
| `fn.invalidate(*args)` | drop one entry |
| `fn.invalidate_all()` | drop every entry of this function |
| `fn.key(*args)` / `fn.tags(*args)` | reproduce the key or tags elsewhere |
| `fn.cache_info()` | region statistics |

It also works on methods; the receiver is excluded from the key, so one entry is
shared by all instances:

```python
class CaseService:
    @region.cache_on_arguments(tags=("case:{case_id}",))
    def get_case(self, case_id: str) -> dict: ...

service.get_case("abc")
service.get_case.invalidate("abc")
```

### Batch

```python
def load_missing(keys: list[str]) -> list[dict]:
    return repository.get_many(keys)          # one origin call for the misses only

results = region.get_or_create_multi(["a", "b", "c"], load_missing)
```

The loader receives only the keys that were not served from cache and must
return one payload per key, in order.

### Async

```python
@region.cache_on_arguments()
async def get_case(case_id: str) -> dict:
    return await client.fetch(case_id)

await get_case("abc")
get_case.invalidate("abc")        # invalidation stays synchronous
```

Concurrent awaits for the same key share one execution of the loader.

---

## 5. Keys

The backend key is composed as:

```
{key_prefix} : {region name} : g{generation} : {scope parts} : {logical key}
```

`KeySpec` controls how call arguments become the logical key:

```python
from gen_epix.fastapp.cache import KeySpec, sha256_mangle_key, length_conditional_mangler

KeySpec()                                   # every parameter, by name (default)
KeySpec(exclude=("unit_of_work", "logger"))  # drop parameters that must not affect a hit
KeySpec(include=("case_id",))                # only these participate
KeySpec(template="case:{case_id}")           # explicit, reproducible from elsewhere
KeySpec(namespace="v2")                      # disambiguate same-named functions
KeySpec(mangler=length_conditional_mangler(200, sha256_mangle_key))  # bound key length
```

Naming a parameter that the function does not declare raises
`CacheConfigurationError`, so a rename cannot silently widen the key.

Prefer `template=` for anything a writer will invalidate by key: it makes the key
reproducible without importing the reader.

### Per-principal partitioning

If a result depends on **who** asked, the identity must be in the key. Declare it
and the region will fail closed when it is missing:

```python
from gen_epix.fastapp.cache import ContextVarScopeProvider, RegionConfig

region = manager.create_region(
    RegionConfig(name="visible_cases", ttl=60.0, scope_parts=("tenant", "principal")),
    scope_provider=ContextVarScopeProvider(),
)

# in middleware, once per request:
with ContextVarScopeProvider.bind(tenant=tenant_id, principal=user_id):
    ...   # every cached call inside is partitioned automatically
```

Calling a scoped region without a bound scope raises `CacheConfigurationError`
rather than producing a key shared by every caller.

### Request-scoped memoization

```python
from gen_epix.fastapp.cache import RequestScope

with RequestScope.activate():
    ...  # repeated reads of one key inside this block hit an in-request memo
```

---

## 6. Invalidation

Five levers, from narrowest to broadest. Pick the narrowest one that the caller
can express without duplicating knowledge it should not have.

| Lever | Call | Cost | Use when |
| --- | --- | --- | --- |
| key | `fn.invalidate(*args)` / `region.invalidate_keys(k)` | O(1) | the writer can reproduce the key |
| tag | `region.invalidate_tags("case:42")` | O(entries with that tag) | the writer knows *what* changed, not *who* cached it |
| dependency | `manager.invalidate_dependents("case", {"case_id": 42})` | as declared | the writer should not know about caches at all |
| generation | `region.bump_generation()` | O(1) | the key space is large or cannot be enumerated |
| region | `region.invalidate(mode)` / `region.clear()` | O(1) / O(region) | everything in the region is suspect |

### Tags

An entry declares labels; a writer names one:

```python
@region.cache_on_arguments(tags=("case:{case_id}", "cases"))
def get_case_summary(case_id: str) -> dict: ...

@region.cache_on_arguments(tags=("case:{case_id}",))
def get_case_timeline(case_id: str) -> list: ...

region.invalidate_tags("case:42")   # both views of case 42 go
region.invalidate_tags("cases")     # every summary goes
```

Every decorated function additionally carries an implicit tag naming itself,
which is what makes `invalidate_all()` work without enumerating keys.

### Declared dependencies — the recommended writer-side API

Readers (or the composition code) declare once what their results depend on. A
writer then names the changed thing and never learns which caches exist:

```python
manager.declare_dependency("case", tags=("case:{case_id}",))
manager.declare_dependency("case", regions=("case_reports",))
manager.declare_dependency("organization", namespaces=("cases",))

# anywhere a case changes:
manager.invalidate_dependents("case", {"case_id": case_id})
```

Adding a new cached reader later requires changing the declaration, not the write
path.

### Generational invalidation

```python
region.bump_generation()
```

Nothing is deleted. The generation embedded in future keys changes, so existing
entries become unaddressable and are reclaimed later by expiry or eviction. This
is the only affordable option against a store whose keys you cannot enumerate.

### Hard vs soft

```python
from gen_epix.fastapp.cache import InvalidationMode

region.invalidate(InvalidationMode.HARD)   # everyone waits for fresh data
region.invalidate(InvalidationMode.SOFT)   # keep serving the old value while it refreshes
```

`SOFT` trades bounded staleness for the absence of a load spike, which matters on
a busy region backed by an expensive origin.

---

## 7. Transactions

Invalidating before the change is committed is a bug in both directions: a
concurrent reader repopulates the cache from uncommitted state, and a rollback
leaves the cache cleared for data that never changed.

```python
with manager.transaction():
    repository.update(case)
    manager.invalidate_dependents("case", {"case_id": case.id})
    # nothing has been invalidated yet
# applied here, on normal exit; discarded if the block raised
```

Identical requests collapse, so a loop over a thousand objects does not replay
one broad invalidation a thousand times.

The transaction is bound to a `ContextVar`, so any region or manager call inside
the block enlists automatically — including calls made by code that knows nothing
about the transaction.

---

## 8. Staleness and stampedes

| Problem | Setting |
| --- | --- |
| every concurrent caller loads on expiry | built in: `SingleFlight` per key, always on |
| expiry pause is visible to users | `soft_ttl` — serve stale, refresh in the background |
| a batch of entries expires simultaneously | `jitter_ratio` |
| concurrent readers all decide to refresh | `early_refresh_ratio` — probabilistic, rises towards expiry |
| a failing origin is hammered | `cache_exceptions` — cache the failure with `negative_ttl` |
| a scan of one-shot keys evicts the hot set | `eviction_policy=TINY_LFU` — frequency-based admission |

Where the background refresh runs is configurable:

```python
from concurrent.futures import ThreadPoolExecutor
from gen_epix.fastapp.cache import InlineRefreshRunner, ThreadRefreshRunner

manager.create_region(config, refresh_runner=ThreadRefreshRunner(ThreadPoolExecutor(4)))
manager.create_region(config, refresh_runner=InlineRefreshRunner())   # tests, single-threaded
```

---

## 9. Resilience

A cache must never make a request fail, or slower than the origin it fronts.

```python
from gen_epix.fastapp.cache import (
    CircuitBreaker, FailureMode, FailurePolicy, RegionConfig, TimeoutGuard,
)

region = manager.create_region(
    RegionConfig(name="cases", ttl=300.0, operation_timeout=0.05),
    failure_policy=FailurePolicy(
        mode=FailureMode.FAIL_OPEN,
        breaker=CircuitBreaker(failure_threshold=5, reset_timeout=30.0),
        guard=TimeoutGuard(0.05),
        on_error=lambda exception: logger.warning("cache degraded: %s", exception),
    ),
)
```

- **Fail-open** (default): a backend error is absorbed, the loader runs, the
  request succeeds.
- **Fail-closed**: the error surfaces, which suits a region where a silent bypass
  would overload the origin.
- The **breaker** stops calling an unreachable store after N consecutive
  failures, admitting one probe per `reset_timeout`.
- Setting `operation_timeout` on the config is enough to get a guard on the
  default policy.
- An entry that the current release cannot deserialize is treated as a miss and
  replaced, so a payload format change never breaks a request.

---

## 10. Observability

```python
statistics = region.statistics()
statistics.hit_rate, statistics.requests, statistics.average_load_seconds
statistics.evictions, statistics.expirations, statistics.invalidations

manager.statistics()          # per region
manager.total_statistics()    # summed
```

Events for a metrics exporter or a tracer:

```python
from gen_epix.fastapp.cache import CacheEvent, CacheListener

class MetricsListener(CacheListener):
    """Forward cache events to the metrics backend."""

    def on_event(self, event: CacheEvent) -> None:
        metrics.increment(f"cache.{event.region}.{event.operation.value.lower()}")

manager = CacheManager(listener=MetricsListener())
```

A listener that raises is skipped; instrumentation never breaks a read.

Alert on hit-rate collapse. It is usually the first symptom of a key-schema
defect, and it is otherwise invisible.

---

## 11. Testing

```python
from gen_epix.fastapp.cache import CacheRegion, ManualClock, RegionConfig, RecordingListener

clock = ManualClock()
region = CacheRegion(RegionConfig(name="test", ttl=10.0), clock=clock)

region.get_or_create("k", loader)
clock.advance(11)                 # no sleeping
region.get_or_create("k", loader) # reloads
```

- `ManualClock` controls every expiry decision.
- `RecordingListener` lets a test assert that an invalidation happened instead of
  inspecting private state.
- `with region.disabling():` or `with manager.disabling():` proves that a result
  is identical with and without caching — the strongest guard against a stale
  read shipping to production.
- `NullBackend` gives the same effect through configuration.

---

## 12. Worked example: local cache in a service

A process-local cache with everything on: bounded capacity, jittered TTL,
stale-while-revalidate, tags, and dependency-driven invalidation.

```python
"""Composition of a process-local cache for a read-heavy service."""

from concurrent.futures import ThreadPoolExecutor

from gen_epix.fastapp.cache import (
    CacheManager,
    EvictionPolicyType,
    KeySpec,
    RegionConfig,
    ThreadRefreshRunner,
)

manager = CacheManager()

reference_region = manager.create_region(
    RegionConfig(
        name="reference_data",
        ttl=3600.0,
        soft_ttl=3000.0,      # refresh in the background from 50 minutes on
        jitter_ratio=0.1,     # spread expiry over the last 6 minutes
        max_weight=10_000,
        eviction_policy=EvictionPolicyType.TINY_LFU,
    ),
    refresh_runner=ThreadRefreshRunner(ThreadPoolExecutor(2)),
)

case_region = manager.create_region(
    RegionConfig(
        name="cases",
        ttl=120.0,
        negative_ttl=15.0,    # remember an absent case only briefly
        max_weight=50_000,
    )
)

manager.declare_dependency("case", tags=("case:{case_id}",))
manager.declare_dependency("concept_set", regions=("reference_data",))


class CaseReadService:
    """Read side of the case domain, with its expensive reads cached."""

    def __init__(self, repository):
        self._repository = repository

    @case_region.cache_on_arguments(
        key_spec=KeySpec(template="summary:{case_id}"),
        tags=("case:{case_id}",),
    )
    def get_summary(self, case_id: str) -> dict | None:
        return self._repository.get_summary(case_id)

    @case_region.cache_on_arguments(
        key_spec=KeySpec(template="timeline:{case_id}"),
        tags=("case:{case_id}",),
    )
    def get_timeline(self, case_id: str) -> list[dict]:
        return self._repository.get_timeline(case_id)


class CaseWriteService:
    """Write side, which never learns which caches hold derived results."""

    def __init__(self, repository, unit_of_work):
        self._repository = repository
        self._unit_of_work = unit_of_work

    def update_case(self, case) -> None:
        with manager.transaction():           # invalidation deferred to commit
            with self._unit_of_work:
                self._repository.update(case)
            manager.invalidate_dependents("case", {"case_id": case.id})
```

`get_summary` and `get_timeline` are two independent entries, keyed by explicit
templates, both tagged `case:<id>`. `update_case` names only `"case"`. Adding a
third cached view later requires no change to `CaseWriteService`.

---

## 13. Worked example: distributed cache with Redis

Redis is **not** a dependency of this package and no Redis backend ships with it.
What follows is a complete, working implementation you can copy into your
composition layer. It is deliberately explicit about what a shared store changes.

### 13.1 What must be replaced

| Collaborator | Process-local | Shared |
| --- | --- | --- |
| backend | `MemoryBackend` | `RedisBackend` (below), optionally behind `LayeredBackend` |
| serializer | `IdentitySerializer` | a **bytes** serializer: `JsonSerializer`, or `SigningSerializer(PickleSerializer(), secret)` |
| clock | `SystemClock` (monotonic) | a wall-clock, so timestamps are comparable across processes |
| tag index | `MemoryTagIndex` | `RedisTagIndex` (below) |
| version store | `MemoryVersionStore` | `RedisVersionStore` (below) |
| bus | none | `RedisInvalidationBus` (below), required if you use an L1 tier |

> **Clock.** `EntryMetadata.created_at` and `expires_at` come from
> `Clock.monotonic()`. `time.monotonic()` is process-local and meaningless in
> another process, so a shared region must use a clock whose `monotonic()`
> returns wall-clock time. The trade-off is that a wall-clock step (NTP) can
> shift expiry; keep a native Redis TTL as the backstop, as the backend below
> does.

> **Serializer.** Never store bare pickle in a shared store. Either use
> `JsonSerializer`, or wrap pickle in `SigningSerializer` so that an attacker who
> can write to Redis cannot achieve code execution on read. Use
> `EncryptingSerializer` for personal data.

### 13.2 A Redis backend

```python
"""Redis-backed cache store."""

import pickle
import time
from collections.abc import Iterable, Iterator, Mapping

from redis import Redis
from redis.exceptions import RedisError

from gen_epix.fastapp.cache import (
    NO_VALUE,
    CacheBackend,
    CacheBackendError,
    CachedValue,
    NoValue,
)


class WallClock:
    """Report wall-clock time for both readings.

    A shared store needs timestamps that another process can interpret, which
    `time.monotonic` cannot provide.
    """

    def monotonic(self) -> float:
        """Return the current wall-clock time in seconds."""
        return time.time()

    def time(self) -> float:
        """Return the current wall-clock time in seconds."""
        return time.time()


class RedisBackend(CacheBackend):
    """Store cache envelopes in Redis.

    The envelope, not just the payload, is serialized, because the metadata that
    drives expiry and generation checks must travel with the value. A native
    Redis expiry is set alongside the metadata so that abandoned keys are
    reclaimed even if no process ever reads them again.
    """

    def __init__(
        self,
        client: Redis,
        clock: WallClock,
        prefix: str = "cache:",
        name: str = "redis",
    ):
        """Initialize a RedisBackend instance."""
        super().__init__(name)
        self._client = client
        self._clock = clock
        self._prefix = prefix

    def _redis_key(self, key: str) -> str:
        """Return the namespaced Redis key for a composed cache key."""
        return self._prefix + key

    def _expiry_seconds(self, value: CachedValue) -> int | None:
        """Return the native Redis expiry for an envelope, if it has one."""
        if value.metadata.expires_at is None:
            return None
        # One extra second so Redis never expires an entry the region still trusts.
        return max(1, int(value.metadata.expires_at - self._clock.monotonic()) + 1)

    def get(self, key: str) -> CachedValue | NoValue:
        """See base method."""
        try:
            raw = self._client.get(self._redis_key(key))
        except RedisError as exception:
            raise CacheBackendError(str(exception)) from exception
        if raw is None:
            return NO_VALUE
        try:
            return pickle.loads(raw)
        except Exception:
            # An unreadable envelope is a miss, not a failed request.
            return NO_VALUE

    def get_multi(self, keys: Iterable[str]) -> list[CachedValue | NoValue]:
        """See base method."""
        ordered = [self._redis_key(key) for key in keys]
        if not ordered:
            return []
        try:
            raws = self._client.mget(ordered)
        except RedisError as exception:
            raise CacheBackendError(str(exception)) from exception
        results: list[CachedValue | NoValue] = []
        for raw in raws:
            if raw is None:
                results.append(NO_VALUE)
                continue
            try:
                results.append(pickle.loads(raw))
            except Exception:
                results.append(NO_VALUE)
        return results

    def set(self, key: str, value: CachedValue) -> None:
        """See base method."""
        try:
            self._client.set(
                self._redis_key(key),
                pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL),
                ex=self._expiry_seconds(value),
            )
        except RedisError as exception:
            raise CacheBackendError(str(exception)) from exception

    def set_multi(self, mapping: Mapping[str, CachedValue]) -> None:
        """See base method."""
        try:
            pipeline = self._client.pipeline(transaction=False)
            for key, value in mapping.items():
                pipeline.set(
                    self._redis_key(key),
                    pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL),
                    ex=self._expiry_seconds(value),
                )
            pipeline.execute()
        except RedisError as exception:
            raise CacheBackendError(str(exception)) from exception

    def delete(self, key: str) -> None:
        """See base method."""
        try:
            self._client.delete(self._redis_key(key))
        except RedisError as exception:
            raise CacheBackendError(str(exception)) from exception

    def delete_multi(self, keys: Iterable[str]) -> None:
        """See base method."""
        ordered = [self._redis_key(key) for key in keys]
        if not ordered:
            return
        try:
            self._client.delete(*ordered)
        except RedisError as exception:
            raise CacheBackendError(str(exception)) from exception

    def clear(self) -> None:
        """See base method.

        Only keys carrying this backend's prefix are removed, so the region
        cannot flush an unrelated Redis database.
        """
        try:
            for redis_key in self._client.scan_iter(match=self._prefix + "*", count=500):
                self._client.delete(redis_key)
        except RedisError as exception:
            raise CacheBackendError(str(exception)) from exception

    def contains(self, key: str) -> bool:
        """See base method."""
        try:
            return bool(self._client.exists(self._redis_key(key)))
        except RedisError as exception:
            raise CacheBackendError(str(exception)) from exception

    def keys(self) -> Iterator[str]:
        """See base method.

        This scans the keyspace and must not be used on a request path.
        """
        offset = len(self._prefix)
        for redis_key in self._client.scan_iter(match=self._prefix + "*", count=500):
            yield redis_key.decode("utf-8")[offset:]
```

A distributed mutex, so that regeneration is coordinated across processes rather
than per process:

```python
class RedisMutex:
    """Adapt a Redis lock to the `Mutex` protocol."""

    def __init__(self, lock):
        """Initialize a RedisMutex instance."""
        self._lock = lock

    def acquire(self, wait: bool = True) -> bool:
        """See base method."""
        return bool(self._lock.acquire(blocking=wait))

    def release(self) -> None:
        """See base method."""
        self._lock.release()

    def locked(self) -> bool:
        """See base method."""
        return bool(self._lock.locked())


# Add to RedisBackend:
#
#     def get_mutex(self, key: str) -> RedisMutex:
#         """See base method."""
#         return RedisMutex(
#             self._client.lock(f"{self._prefix}lock:{key}", timeout=30, blocking_timeout=5)
#         )
```

### 13.3 A Redis tag index

`MemoryTagIndex` only knows the entries the current process wrote. For shared
tags, keep the index in Redis:

```python
"""Redis-backed tag index."""

from collections.abc import Iterable

from redis import Redis

from gen_epix.fastapp.cache import TagIndex


class RedisTagIndex(TagIndex):
    """Map tags to keys using Redis sets.

    Two sets are maintained per association so that removing a key does not
    require scanning every tag.
    """

    def __init__(self, client: Redis, prefix: str = "cache:tag:"):
        """Initialize a RedisTagIndex instance."""
        self._client = client
        self._prefix = prefix

    def _tag_key(self, tag: str) -> str:
        """Return the Redis key of the set holding the keys of one tag."""
        return f"{self._prefix}t:{tag}"

    def _key_key(self, key: str) -> str:
        """Return the Redis key of the set holding the tags of one cache key."""
        return f"{self._prefix}k:{key}"

    def _members(self, redis_key: str) -> set[str]:
        """Return a Redis set as decoded strings."""
        return {item.decode("utf-8") for item in self._client.smembers(redis_key)}

    def add(self, key: str, tags: Iterable[str]) -> None:
        """See base method."""
        new_tags = set(tags)
        previous = self._members(self._key_key(key))
        pipeline = self._client.pipeline(transaction=False)
        for tag in previous - new_tags:
            pipeline.srem(self._tag_key(tag), key)
        pipeline.delete(self._key_key(key))
        if new_tags:
            pipeline.sadd(self._key_key(key), *new_tags)
            for tag in new_tags:
                pipeline.sadd(self._tag_key(tag), key)
        pipeline.execute()

    def keys_for(self, tag: str) -> set[str]:
        """See base method."""
        return self._members(self._tag_key(tag))

    def discard_key(self, key: str) -> None:
        """See base method."""
        tags = self._members(self._key_key(key))
        pipeline = self._client.pipeline(transaction=False)
        for tag in tags:
            pipeline.srem(self._tag_key(tag), key)
        pipeline.delete(self._key_key(key))
        pipeline.execute()

    def pop_tag(self, tag: str) -> set[str]:
        """See base method."""
        keys = self.keys_for(tag)
        pipeline = self._client.pipeline(transaction=False)
        for key in keys:
            pipeline.srem(self._key_key(key), tag)
        pipeline.delete(self._tag_key(tag))
        pipeline.execute()
        return keys

    def clear(self) -> None:
        """See base method."""
        for redis_key in self._client.scan_iter(match=self._prefix + "*", count=500):
            self._client.delete(redis_key)

    def tags(self) -> set[str]:
        """See base method."""
        offset = len(self._prefix) + 2
        return {
            redis_key.decode("utf-8")[offset:]
            for redis_key in self._client.scan_iter(
                match=self._prefix + "t:*", count=500
            )
        }
```

### 13.4 A Redis version store

The generation must be shared, otherwise a bump in one worker does not orphan the
keys another worker wrote:

```python
"""Redis-backed generation store."""

from redis import Redis

from gen_epix.fastapp.cache import VersionStore


class RedisVersionStore(VersionStore):
    """Hold namespace generations in Redis counters."""

    def __init__(self, client: Redis, prefix: str = "cache:gen:"):
        """Initialize a RedisVersionStore instance."""
        self._client = client
        self._prefix = prefix

    def get(self, namespace: str) -> int:
        """See base method."""
        value = self._client.get(self._prefix + namespace)
        return int(value) if value is not None else 0

    def bump(self, namespace: str) -> int:
        """See base method."""
        return int(self._client.incr(self._prefix + namespace))

    def set(self, namespace: str, version: int) -> None:
        """See base method."""
        # A Lua compare-and-set keeps the generation monotonic under races.
        self._client.eval(
            "local c = tonumber(redis.call('GET', KEYS[1]) or '0') "
            "if tonumber(ARGV[1]) > c then redis.call('SET', KEYS[1], ARGV[1]) end",
            1,
            self._prefix + namespace,
            version,
        )

    def reset(self, namespace: str | None = None) -> None:
        """See base method."""
        if namespace is None:
            for redis_key in self._client.scan_iter(match=self._prefix + "*"):
                self._client.delete(redis_key)
        else:
            self._client.delete(self._prefix + namespace)

    def snapshot(self) -> dict[str, int]:
        """See base method."""
        offset = len(self._prefix)
        return {
            redis_key.decode("utf-8")[offset:]: self.get(
                redis_key.decode("utf-8")[offset:]
            )
            for redis_key in self._client.scan_iter(match=self._prefix + "*")
        }
```

Note that `get` costs a round trip and every key composition calls it. If that
matters, cache the generation locally for a second or two and accept the
corresponding invalidation delay.

### 13.5 A Redis invalidation bus

Required as soon as any process holds a local tier. Delivery is deduplicated by
message identifier, so the publisher's own echo and any at-least-once redelivery
are harmless.

```python
"""Redis pub/sub propagation of invalidation requests."""

import dataclasses
import json
import threading

from redis import Redis

from gen_epix.fastapp.cache import (
    Invalidation,
    InvalidationBus,
    InvalidationMode,
    InvalidationScope,
    LocalInvalidationBus,
)


def _encode(invalidation: Invalidation) -> str:
    """Return the wire form of an invalidation request."""
    return json.dumps(
        {
            "scope": invalidation.scope.value,
            "mode": invalidation.mode.value,
            "region": invalidation.region,
            "keys": sorted(invalidation.keys),
            "tags": sorted(invalidation.tags),
            "namespace": invalidation.namespace,
            "generation": invalidation.generation,
            "origin": invalidation.origin,
            "message_id": invalidation.message_id,
        }
    )


def _decode(raw: bytes) -> Invalidation:
    """Return the invalidation request carried by a message."""
    payload = json.loads(raw)
    return Invalidation(
        scope=InvalidationScope(payload["scope"]),
        mode=InvalidationMode(payload["mode"]),
        region=payload["region"],
        keys=frozenset(payload["keys"]),
        tags=frozenset(payload["tags"]),
        namespace=payload["namespace"],
        generation=payload["generation"],
        origin=payload["origin"],
        message_id=payload["message_id"],
    )


class RedisInvalidationBus(InvalidationBus):
    """Broadcast invalidation requests over a Redis channel.

    Requests published here are applied locally first, so a caller never waits
    for the round trip, and then broadcast. Inbound messages are handed to the
    same local bus, whose message-identifier history makes repeated delivery a
    no-op.
    """

    def __init__(self, client: Redis, channel: str = "cache:invalidation"):
        """Initialize a RedisInvalidationBus instance."""
        self._client = client
        self._channel = channel
        self._local = LocalInvalidationBus()
        self._pubsub = client.pubsub(ignore_subscribe_messages=True)
        self._thread: threading.Thread | None = None
        self._stopping = threading.Event()

    @property
    def origin(self) -> str:
        """Return the identifier stamped on requests published here."""
        return self._local.origin

    def start(self) -> None:
        """Begin consuming inbound messages on a daemon thread."""
        self._pubsub.subscribe(self._channel)
        self._thread = threading.Thread(target=self._consume, daemon=True)
        self._thread.start()

    def _consume(self) -> None:
        """Apply inbound messages until the bus is closed."""
        while not self._stopping.is_set():
            message = self._pubsub.get_message(timeout=1.0)
            if message is None or message.get("type") != "message":
                continue
            try:
                self._local.deliver(_decode(message["data"]))
            except Exception:  # noqa: BLE001 - a bad message must not stop the loop
                continue

    def publish(self, invalidation: Invalidation) -> None:
        """See base method."""
        stamped = (
            invalidation
            if invalidation.origin is not None
            else dataclasses.replace(invalidation, origin=self.origin)
        )
        self._local.deliver(stamped)
        self._client.publish(self._channel, _encode(stamped))

    def subscribe(self, handler) -> None:
        """See base method."""
        self._local.subscribe(handler)

    def close(self) -> None:
        """See base method."""
        self._stopping.set()
        if self._thread is not None:
            self._thread.join(timeout=2)
        self._pubsub.close()
        self._local.close()
```

### 13.6 Putting it together

Two shapes. Choose based on whether you can tolerate the staleness window that a
local tier introduces.

**A. Shared only** — every read is a Redis round trip, every process sees the
same data immediately. No bus is strictly required.

```python
from redis import Redis

from gen_epix.fastapp.cache import (
    CacheManager,
    JsonSerializer,
    RegionConfig,
)

client = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
clock = WallClock()

manager = CacheManager(clock=clock, version_store=RedisVersionStore(client))

region = manager.create_region(
    RegionConfig(
        name="cases",
        ttl=300.0,
        key_prefix=settings.APP_NAME,     # keep environments apart in one Redis
        operation_timeout=0.05,           # never slower than the origin
        schema_version=1,
    ),
    backend=RedisBackend(client, clock, prefix=f"{settings.APP_NAME}:cache:"),
    serializer=JsonSerializer(),
    tag_index=RedisTagIndex(client, prefix=f"{settings.APP_NAME}:cache:tag:"),
)
```

**B. Near cache over Redis** — most reads never leave the process; a bus keeps
the local tiers coherent. This is the configuration that needs the bus, and the
one where forgetting it produces the classic "invalidation only worked on one
worker" bug.

```python
from gen_epix.fastapp.cache import (
    CacheManager,
    LayeredBackend,
    MemoryBackend,
    PickleSerializer,
    RegionConfig,
    SigningSerializer,
)

client = Redis.from_url(settings.REDIS_URL)
clock = WallClock()

bus = RedisInvalidationBus(client, channel=f"{settings.APP_NAME}:cache:invalidation")
bus.start()

manager = CacheManager(clock=clock, bus=bus, version_store=RedisVersionStore(client))

remote = RedisBackend(client, clock, prefix=f"{settings.APP_NAME}:cache:")
near = MemoryBackend(max_weight=5_000, clock=clock, name="cases-near")

region = manager.create_region(
    RegionConfig(
        name="cases",
        ttl=300.0,
        soft_ttl=240.0,
        jitter_ratio=0.1,
        operation_timeout=0.05,
    ),
    backend=LayeredBackend(near=near, remote=remote, name="cases-layered"),
    serializer=SigningSerializer(PickleSerializer(), settings.CACHE_SIGNING_SECRET),
    tag_index=RedisTagIndex(client, prefix=f"{settings.APP_NAME}:cache:tag:"),
)

manager.declare_dependency("case", tags=("case:{case_id}",))
```

Regions created through a manager that has a bus subscribe to it automatically,
so this now holds:

```python
# worker 1
manager.invalidate_dependents("case", {"case_id": "abc"})

# worker 2, 3, 4 …  drop their near copies within one pub/sub hop
```

Shut down cleanly so the consumer thread and the Redis connections are released:

```python
manager.close()   # closes every region, its backend, and the bus
```

### 13.7 Operational notes

- **Key prefix per environment and per release.** `key_prefix` plus
  `schema_version` prevent a staging worker and a production worker, or two
  releases with different payload shapes, from reading each other's entries.
- **`maxmemory-policy`.** Set it to `allkeys-lru` or `volatile-lru` on the Redis
  instance. Generational invalidation deliberately orphans keys and relies on
  eviction to reclaim them.
- **Do not enumerate.** `keys()` and `clear()` scan. Invalidate by tag or by
  generation on a hot path.
- **Timeouts.** Set `operation_timeout` and a client `socket_timeout`. A cache
  that blocks is worse than no cache.
- **A `LayeredBackend` is only as coherent as its bus.** If the bus is down,
  near copies live until their TTL. Keep `ttl` short enough that this is an
  acceptable worst case.

---

## 14. HTTP-level caching

`HttpCachePolicy` is transport-agnostic: it produces headers and evaluates
conditional requests without importing a web framework. Reusing the region tags
as surrogate keys keeps the value cache and the edge cache invalidated together.

```python
from gen_epix.fastapp.cache import HttpCachePolicy, compute_etag

policy = HttpCachePolicy(
    max_age=60,
    private=True,                  # per-principal responses must not be shared
    vary=("Accept", "Authorization"),
    stale_while_revalidate=30,
    stale_if_error=600,
)

body = serialize(result)
etag = compute_etag(body)

if policy.is_not_modified(request.headers, etag):
    return Response(status_code=304, headers=policy.response_headers(etag))

return Response(
    content=body,
    headers=policy.response_headers(etag, surrogate_keys=[f"case:{case_id}"]),
)
```

---

## 15. Pitfalls

1. **Authorization-dependent results without `scope_parts`.** If the value
   differs per principal, the principal belongs in the key — or cache below the
   authorization filter, never above it. This is the leakage bug that matters.
2. **A near cache without a bus.** Invalidation appears to work in development
   with one worker and silently fails in production with several.
3. **`IdentitySerializer` with mutable results.** Callers share the cached
   object; one caller mutating it corrupts every later hit. Use
   `DeepCopySerializer` if callers cannot be trusted to treat results as
   immutable.
4. **Bare pickle in a shared store.** Anyone who can write to Redis gets code
   execution on read. Sign it, or use JSON.
5. **Invalidating inside an open transaction.** Use `manager.transaction()`.
6. **Unbounded key cardinality.** Per-user × per-filter × per-page keys blow the
   budget and make targeted invalidation impossible. Narrow the key with a
   `KeySpec` template and set `key_admission` where untrusted input reaches it.
7. **Monotonic timestamps in a shared store.** Use a wall-clock `Clock` for any
   region backed by a shared backend.
8. **Scattered explicit evictions.** Every `invalidate_keys` call in a writer is
   a duplicated key formula. Prefer tags, and prefer
   `manager.invalidate_dependents` over tags.
