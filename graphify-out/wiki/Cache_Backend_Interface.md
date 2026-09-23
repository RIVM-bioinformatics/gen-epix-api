# Cache Backend Interface

> 225 nodes · cohesion 0.02

## Key Concepts

- **region.py** (69 connections) — `gen_epix/fastapp/cache/region.py`
- **test_fastapp_cache_region.py** (58 connections) — `test/fastapp/unit/cache/test_fastapp_cache_region.py`
- **CachedValue** (48 connections) — `gen_epix/fastapp/cache/model.py`
- **CacheBackend** (40 connections) — `gen_epix/fastapp/cache/backend/base.py`
- **test_fastapp_cache_backend.py** (39 connections) — `test/fastapp/unit/cache/test_fastapp_cache_backend.py`
- **NoValue** (29 connections) — `gen_epix/fastapp/cache/model.py`
- **cache/exc.py** (28 connections) — `gen_epix/fastapp/cache/exc.py`
- **LayeredBackend** (26 connections) — `gen_epix/fastapp/cache/backend/layered.py`
- **memory.py** (26 connections) — `gen_epix/fastapp/cache/backend/memory.py`
- **ProxyBackend** (24 connections) — `gen_epix/fastapp/cache/backend/base.py`
- **cache/enum.py** (23 connections) — `gen_epix/fastapp/cache/enum.py`
- **cache/model.py** (23 connections) — `gen_epix/fastapp/cache/model.py`
- **RemovalCause** (21 connections) — `gen_epix/fastapp/cache/enum.py`
- **stats.py** (21 connections) — `gen_epix/fastapp/cache/stats.py`
- **NullBackend** (19 connections) — `gen_epix/fastapp/cache/backend/null.py`
- **lock.py** (19 connections) — `gen_epix/fastapp/cache/lock.py`
- **Mutex** (18 connections) — `gen_epix/fastapp/cache/lock.py`
- **backend/base.py** (17 connections) — `gen_epix/fastapp/cache/backend/base.py`
- **eviction.py** (17 connections) — `gen_epix/fastapp/cache/eviction.py`
- **CacheBackendError** (17 connections) — `gen_epix/fastapp/cache/exc.py`
- **FailurePolicy** (17 connections) — `gen_epix/fastapp/cache/resilience.py`
- **FailureMode** (16 connections) — `gen_epix/fastapp/cache/enum.py`
- **EvictionPolicyType** (15 connections) — `gen_epix/fastapp/cache/enum.py`
- **create_eviction_strategy()** (15 connections) — `gen_epix/fastapp/cache/eviction.py`
- **resilience.py** (15 connections) — `gen_epix/fastapp/cache/resilience.py`
- *... and 200 more nodes in this community*

## Relationships

- [Cache Error Types](Cache_Error_Types.md) (71 shared connections)
- [Cache Clock & Config Enums](Cache_Clock_&_Config_Enums.md) (54 shared connections)
- [Cache Region](Cache_Region.md) (35 shared connections)
- [In-Memory Cache Backend](In-Memory_Cache_Backend.md) (30 shared connections)
- [Memory Cache Eviction](Memory_Cache_Eviction.md) (19 shared connections)
- [Cache Decorator Tests](Cache_Decorator_Tests.md) (19 shared connections)
- [Cache Statistics](Cache_Statistics.md) (18 shared connections)
- [Cache Region Configuration](Cache_Region_Configuration.md) (12 shared connections)
- [Manual Clock Test Helpers](Manual_Clock_Test_Helpers.md) (11 shared connections)
- [Request Scope Provider](Request_Scope_Provider.md) (11 shared connections)
- [Count-Min Sketch](Count-Min_Sketch.md) (9 shared connections)
- [Cache Decorator & Key Generation](Cache_Decorator_&_Key_Generation.md) (7 shared connections)

## Source Files

- `gen_epix/fastapp/cache/backend/__init__.py`
- `gen_epix/fastapp/cache/backend/base.py`
- `gen_epix/fastapp/cache/backend/layered.py`
- `gen_epix/fastapp/cache/backend/memory.py`
- `gen_epix/fastapp/cache/backend/null.py`
- `gen_epix/fastapp/cache/clock.py`
- `gen_epix/fastapp/cache/enum.py`
- `gen_epix/fastapp/cache/eviction.py`
- `gen_epix/fastapp/cache/exc.py`
- `gen_epix/fastapp/cache/lock.py`
- `gen_epix/fastapp/cache/model.py`
- `gen_epix/fastapp/cache/region.py`
- `gen_epix/fastapp/cache/resilience.py`
- `gen_epix/fastapp/cache/stats.py`
- `test/fastapp/unit/cache/test_fastapp_cache_backend.py`
- `test/fastapp/unit/cache/test_fastapp_cache_region.py`
- `test/fastapp/unit/cache/test_fastapp_cache_support.py`

## Audit Trail

- EXTRACTED: 684 (92%)
- INFERRED: 57 (8%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*