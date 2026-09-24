"""Generic cache management for the application framework.

The package provides a complete, framework-independent cache: declarative
caching of functions, five progressively broader ways to invalidate, stampede
and staleness handling, resilience against a failing store, instrumentation, and
the key-composition rules that keep results of different principals apart. It
contains no application-specific policy; a caller supplies configuration,
regions and dependency declarations.

Composition entry points:

- `CacheManager`, `create_default_manager` and `region_config_from_mapping` build
  and own regions, apply cross-region invalidation, and expose
  `invalidate_dependents`, which is the operation a mutating method should call.
- `CacheRegion`, `RegionConfig` and `create_layered_region` define one caching
  policy and its store.

Reading and writing:

- `CachedFunction`, `AsyncCachedFunction` and `BoundCachedFunction` are the
  callables produced by `CacheRegion.cache_on_arguments`. They expose
  `invalidate`, `invalidate_all`, `set`, `refresh`, `get`, `key` and `original`.
- `NO_VALUE`, `NoValue`, `CachedValue`, `EntryMetadata` and `CachedError`
  describe what is stored, including a cached failure.

Key composition and identity:

- `KeySpec`, `bind_arguments`, `compose_key`, `function_namespace`,
  `arg_key_generator`, `kwarg_key_generator`, `template_key_generator`,
  `sha256_mangle_key` and `length_conditional_mangler` control how arguments
  become keys.
- `ScopeProvider`, `ContextVarScopeProvider`, `StaticScopeProvider`,
  `NullScopeProvider` and `RequestScope` supply per-principal partitioning and
  request-local memoization.

Invalidation:

- `Invalidation`, `InvalidationStrategy`, `InvalidationBus`,
  `LocalInvalidationBus` and `DependencyRegistry` describe, propagate and
  resolve invalidation requests.
- `InvalidationTransaction`, `invalidation_transaction`, `current_transaction`
  and `enlist` defer invalidation until a unit of work commits.
- `TagIndex`, `MemoryTagIndex`, `TagTemplate`, `render_tags`, `VersionStore` and
  `MemoryVersionStore` back tag-based and generational invalidation.

Stores:

- `CacheBackend`, `ProxyBackend`, `MemoryBackend`, `NullBackend`,
  `LayeredBackend` and `RemovalListener` implement and decorate the store
  contract.
- `EvictionStrategy`, `LRUEviction`, `LFUEviction`, `FIFOEviction`,
  `RandomEviction`, `TinyLFUEviction`, `CountMinSketch` and
  `create_eviction_strategy` decide which entry leaves a full store.

Cross-cutting services:

- `Serializer`, `IdentitySerializer`, `DeepCopySerializer`, `JsonSerializer`,
  `PickleSerializer`, `CompressingSerializer`, `SigningSerializer` and
  `EncryptingSerializer` cover copy semantics, compression, integrity and
  encryption.
- `SingleFlight`, `AsyncSingleFlight`, `KeyedMutex`, `Mutex`, `ThreadMutex`,
  `NullMutex`, `RefreshRunner`, `InlineRefreshRunner` and `ThreadRefreshRunner`
  coordinate concurrent loads and background refreshes.
- `FailurePolicy`, `CircuitBreaker` and `TimeoutGuard` bound the cost of a
  failing store.
- `CacheStatistics`, `StatsRecorder`, `InMemoryStatsRecorder`,
  `NullStatsRecorder`, `CacheEvent`, `CacheListener`, `CompositeListener` and
  `RecordingListener` expose what the cache is doing.
- `Clock`, `SystemClock` and `ManualClock` make every expiry decision testable.
- `HttpCachePolicy`, `compute_etag`, `matches_etag`, `SURROGATE_KEY_HEADER` and
  `SURROGATE_CONTROL_HEADER` cover caching at the transport boundary.

Enumerations `CacheOperation`, `RemovalCause`, `EvictionPolicyType`,
`ExpiryMode`, `InvalidationScope`, `InvalidationMode`, `FailureMode` and
`CircuitState` name the configurable choices. The error hierarchy re-exported
here is `CacheError` with `CacheConfigurationError`,
`RegionAlreadyConfiguredError`, `RegionNotConfiguredError`,
`RegionNotFoundError`, `CacheBackendError`, `CacheTimeoutError`,
`CircuitOpenError`, `SerializationError`, `CantDeserializeError` and
`KeyRejectedError`.
"""

from gen_epix.fastapp.cache.backend import (
    CacheBackend,
    LayeredBackend,
    MemoryBackend,
    NullBackend,
    ProxyBackend,
    RemovalListener,
)
from gen_epix.fastapp.cache.clock import Clock, ManualClock, SystemClock
from gen_epix.fastapp.cache.decorator import (
    AsyncCachedFunction,
    BoundCachedFunction,
    CachedFunction,
)
from gen_epix.fastapp.cache.enum import (
    CacheOperation,
    CircuitState,
    EvictionPolicyType,
    ExpiryMode,
    FailureMode,
    InvalidationMode,
    InvalidationScope,
    RemovalCause,
)
from gen_epix.fastapp.cache.eviction import (
    CountMinSketch,
    EvictionStrategy,
    FIFOEviction,
    LFUEviction,
    LRUEviction,
    RandomEviction,
    TinyLFUEviction,
    create_eviction_strategy,
)
from gen_epix.fastapp.cache.exc import (
    CacheBackendError,
    CacheConfigurationError,
    CacheError,
    CacheTimeoutError,
    CantDeserializeError,
    CircuitOpenError,
    KeyRejectedError,
    RegionAlreadyConfiguredError,
    RegionNotConfiguredError,
    RegionNotFoundError,
    SerializationError,
)
from gen_epix.fastapp.cache.http import (
    SURROGATE_CONTROL_HEADER,
    SURROGATE_KEY_HEADER,
    HttpCachePolicy,
    compute_etag,
    matches_etag,
)
from gen_epix.fastapp.cache.invalidation import (
    DependencyRegistry,
    Invalidation,
    InvalidationBus,
    InvalidationStrategy,
    LocalInvalidationBus,
)
from gen_epix.fastapp.cache.key import (
    KeySpec,
    arg_key_generator,
    bind_arguments,
    compose_key,
    function_namespace,
    kwarg_key_generator,
    length_conditional_mangler,
    sha256_mangle_key,
    template_key_generator,
)
from gen_epix.fastapp.cache.lock import (
    AsyncSingleFlight,
    InlineRefreshRunner,
    KeyedMutex,
    Mutex,
    NullMutex,
    RefreshRunner,
    SingleFlight,
    ThreadMutex,
    ThreadRefreshRunner,
)
from gen_epix.fastapp.cache.manager import (
    CacheManager,
    create_default_manager,
    region_config_from_mapping,
)
from gen_epix.fastapp.cache.model import (
    NO_VALUE,
    CachedValue,
    EntryMetadata,
    NoValue,
    RegionConfig,
)
from gen_epix.fastapp.cache.region import (
    CachedError,
    CacheRegion,
    create_layered_region,
)
from gen_epix.fastapp.cache.resilience import (
    CircuitBreaker,
    FailurePolicy,
    TimeoutGuard,
)
from gen_epix.fastapp.cache.scope import (
    ContextVarScopeProvider,
    NullScopeProvider,
    RequestScope,
    ScopeProvider,
    StaticScopeProvider,
)
from gen_epix.fastapp.cache.serializer import (
    CompressingSerializer,
    DeepCopySerializer,
    EncryptingSerializer,
    IdentitySerializer,
    JsonSerializer,
    PickleSerializer,
    Serializer,
    SigningSerializer,
)
from gen_epix.fastapp.cache.stats import (
    CacheEvent,
    CacheListener,
    CacheStatistics,
    CompositeListener,
    InMemoryStatsRecorder,
    NullStatsRecorder,
    RecordingListener,
    StatsRecorder,
)
from gen_epix.fastapp.cache.tag import (
    MemoryTagIndex,
    TagIndex,
    TagTemplate,
    render_tags,
)
from gen_epix.fastapp.cache.transaction import (
    InvalidationTransaction,
    current_transaction,
    enlist,
    invalidation_transaction,
)
from gen_epix.fastapp.cache.version import MemoryVersionStore, VersionStore

__all__ = [
    "NO_VALUE",
    "SURROGATE_CONTROL_HEADER",
    "SURROGATE_KEY_HEADER",
    "AsyncCachedFunction",
    "AsyncSingleFlight",
    "BoundCachedFunction",
    "CacheBackend",
    "CacheBackendError",
    "CacheConfigurationError",
    "CacheError",
    "CacheEvent",
    "CacheListener",
    "CacheManager",
    "CacheOperation",
    "CacheRegion",
    "CacheStatistics",
    "CacheTimeoutError",
    "CachedError",
    "CachedFunction",
    "CachedValue",
    "CantDeserializeError",
    "CircuitBreaker",
    "CircuitOpenError",
    "CircuitState",
    "Clock",
    "CompositeListener",
    "CompressingSerializer",
    "ContextVarScopeProvider",
    "CountMinSketch",
    "DeepCopySerializer",
    "DependencyRegistry",
    "EncryptingSerializer",
    "EntryMetadata",
    "EvictionPolicyType",
    "EvictionStrategy",
    "ExpiryMode",
    "FIFOEviction",
    "FailureMode",
    "FailurePolicy",
    "HttpCachePolicy",
    "IdentitySerializer",
    "InMemoryStatsRecorder",
    "InlineRefreshRunner",
    "Invalidation",
    "InvalidationBus",
    "InvalidationMode",
    "InvalidationScope",
    "InvalidationStrategy",
    "InvalidationTransaction",
    "JsonSerializer",
    "KeyRejectedError",
    "KeySpec",
    "KeyedMutex",
    "LFUEviction",
    "LRUEviction",
    "LayeredBackend",
    "LocalInvalidationBus",
    "ManualClock",
    "MemoryBackend",
    "MemoryTagIndex",
    "MemoryVersionStore",
    "Mutex",
    "NoValue",
    "NullBackend",
    "NullMutex",
    "NullScopeProvider",
    "NullStatsRecorder",
    "PickleSerializer",
    "ProxyBackend",
    "RandomEviction",
    "RecordingListener",
    "RefreshRunner",
    "RegionAlreadyConfiguredError",
    "RegionConfig",
    "RegionNotConfiguredError",
    "RegionNotFoundError",
    "RemovalCause",
    "RemovalListener",
    "RequestScope",
    "ScopeProvider",
    "SerializationError",
    "Serializer",
    "SigningSerializer",
    "SingleFlight",
    "StaticScopeProvider",
    "StatsRecorder",
    "SystemClock",
    "TagIndex",
    "TagTemplate",
    "ThreadMutex",
    "ThreadRefreshRunner",
    "TimeoutGuard",
    "TinyLFUEviction",
    "VersionStore",
    "arg_key_generator",
    "bind_arguments",
    "compose_key",
    "compute_etag",
    "create_default_manager",
    "create_eviction_strategy",
    "create_layered_region",
    "current_transaction",
    "enlist",
    "function_namespace",
    "invalidation_transaction",
    "kwarg_key_generator",
    "length_conditional_mangler",
    "matches_etag",
    "region_config_from_mapping",
    "render_tags",
    "sha256_mangle_key",
    "template_key_generator",
]
