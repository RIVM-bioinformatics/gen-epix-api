# Cache Error Types

> 178 nodes · cohesion 0.02

## Key Concepts

- **cache/__init__.py** (129 connections) — `gen_epix/fastapp/cache/__init__.py`
- **test_fastapp_cache_support.py** (62 connections) — `test/fastapp/unit/cache/test_fastapp_cache_support.py`
- **Serializer** (21 connections) — `gen_epix/fastapp/cache/serializer.py`
- **CircuitBreaker** (20 connections) — `gen_epix/fastapp/cache/resilience.py`
- **Any** (18 connections)
- **serializer.py** (16 connections) — `gen_epix/fastapp/cache/serializer.py`
- **TimeoutGuard** (15 connections) — `gen_epix/fastapp/cache/resilience.py`
- **JsonSerializer** (14 connections) — `gen_epix/fastapp/cache/serializer.py`
- **CircuitState** (12 connections) — `gen_epix/fastapp/cache/enum.py`
- **IdentitySerializer** (12 connections) — `gen_epix/fastapp/cache/serializer.py`
- **SigningSerializer** (12 connections) — `gen_epix/fastapp/cache/serializer.py`
- **CantDeserializeError** (11 connections) — `gen_epix/fastapp/cache/exc.py`
- **HttpCachePolicy** (11 connections) — `gen_epix/fastapp/cache/http.py`
- **KeyedMutex** (10 connections) — `gen_epix/fastapp/cache/lock.py`
- **CompressingSerializer** (10 connections) — `gen_epix/fastapp/cache/serializer.py`
- **DeepCopySerializer** (10 connections) — `gen_epix/fastapp/cache/serializer.py`
- **SerializationError** (9 connections) — `gen_epix/fastapp/cache/exc.py`
- **PickleSerializer** (9 connections) — `gen_epix/fastapp/cache/serializer.py`
- **EncryptingSerializer** (7 connections) — `gen_epix/fastapp/cache/serializer.py`
- **CacheTimeoutError** (6 connections) — `gen_epix/fastapp/cache/exc.py`
- **http.py** (6 connections) — `gen_epix/fastapp/cache/http.py`
- **compute_etag()** (6 connections) — `gen_epix/fastapp/cache/http.py`
- **matches_etag()** (6 connections) — `gen_epix/fastapp/cache/http.py`
- **.__init__()** (6 connections) — `gen_epix/fastapp/cache/resilience.py`
- **_as_bytes()** (6 connections) — `gen_epix/fastapp/cache/serializer.py`
- *... and 153 more nodes in this community*

## Relationships

- [Cache Backend Interface](Cache_Backend_Interface.md) (66 shared connections)
- [Cache Clock & Config Enums](Cache_Clock_&_Config_Enums.md) (31 shared connections)
- [Cache Decorator & Key Generation](Cache_Decorator_&_Key_Generation.md) (11 shared connections)
- [Cache Region Configuration](Cache_Region_Configuration.md) (7 shared connections)
- [Manual Clock Test Helpers](Manual_Clock_Test_Helpers.md) (7 shared connections)
- [Cache Region](Cache_Region.md) (7 shared connections)
- [Request Scope Provider](Request_Scope_Provider.md) (6 shared connections)
- [Memory Cache Eviction](Memory_Cache_Eviction.md) (5 shared connections)
- [Single-Flight Load Collapsing](Single-Flight_Load_Collapsing.md) (5 shared connections)
- [Cache Statistics](Cache_Statistics.md) (4 shared connections)
- [Cache Decorator Tests](Cache_Decorator_Tests.md) (3 shared connections)
- [Cache Error Types](Cache_Error_Types.md) (3 shared connections)

## Source Files

- `gen_epix/fastapp/cache/__init__.py`
- `gen_epix/fastapp/cache/enum.py`
- `gen_epix/fastapp/cache/exc.py`
- `gen_epix/fastapp/cache/http.py`
- `gen_epix/fastapp/cache/lock.py`
- `gen_epix/fastapp/cache/resilience.py`
- `gen_epix/fastapp/cache/serializer.py`
- `test/fastapp/unit/cache/test_fastapp_cache_support.py`

## Audit Trail

- EXTRACTED: 445 (96%)
- INFERRED: 17 (4%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*