# Cache Region

> 95 nodes · cohesion 0.04

## Key Concepts

- **CacheRegion** (130 connections) — `gen_epix/fastapp/cache/region.py`
- **Any** (20 connections)
- **._emit()** (12 connections) — `gen_epix/fastapp/cache/region.py`
- **._load()** (12 connections) — `gen_epix/fastapp/cache/region.py`
- **.get_or_create()** (11 connections) — `gen_epix/fastapp/cache/region.py`
- **.aget_or_create()** (10 connections) — `gen_epix/fastapp/cache/region.py`
- **.compose_key()** (10 connections) — `gen_epix/fastapp/cache/region.py`
- **._decode()** (10 connections) — `gen_epix/fastapp/cache/region.py`
- **._dispatch()** (10 connections) — `gen_epix/fastapp/cache/region.py`
- **.get()** (10 connections) — `gen_epix/fastapp/cache/region.py`
- **.get_multi()** (9 connections) — `gen_epix/fastapp/cache/region.py`
- **create_layered_region()** (9 connections) — `gen_epix/fastapp/cache/region.py`
- **._is_usable()** (8 connections) — `gen_epix/fastapp/cache/region.py`
- **._read()** (8 connections) — `gen_epix/fastapp/cache/region.py`
- **._store()** (8 connections) — `gen_epix/fastapp/cache/region.py`
- **._envelope()** (7 connections) — `gen_epix/fastapp/cache/region.py`
- **.invalidate_keys()** (7 connections) — `gen_epix/fastapp/cache/region.py`
- **.set_multi()** (7 connections) — `gen_epix/fastapp/cache/region.py`
- **._unwrap()** (7 connections) — `gen_epix/fastapp/cache/region.py`
- **CachedError** (6 connections) — `gen_epix/fastapp/cache/region.py`
- **.get_or_create_multi()** (6 connections) — `gen_epix/fastapp/cache/region.py`
- **._is_refresh_due()** (6 connections) — `gen_epix/fastapp/cache/region.py`
- **._schedule_refresh()** (6 connections) — `gen_epix/fastapp/cache/region.py`
- **.apply()** (5 connections) — `gen_epix/fastapp/cache/region.py`
- **.cache_on_arguments()** (5 connections) — `gen_epix/fastapp/cache/region.py`
- *... and 70 more nodes in this community*

## Relationships

- [Cache Clock & Config Enums](Cache_Clock_&_Config_Enums.md) (35 shared connections)
- [Cache Backend Interface](Cache_Backend_Interface.md) (35 shared connections)
- [Cache Decorator Tests](Cache_Decorator_Tests.md) (20 shared connections)
- [Cache Error Types](Cache_Error_Types.md) (8 shared connections)
- [Cache Region Configuration](Cache_Region_Configuration.md) (7 shared connections)
- [Request Scope Provider](Request_Scope_Provider.md) (5 shared connections)
- [Cache Statistics](Cache_Statistics.md) (4 shared connections)
- [Manual Clock Test Helpers](Manual_Clock_Test_Helpers.md) (3 shared connections)
- [Cache Decorator & Key Generation](Cache_Decorator_&_Key_Generation.md) (3 shared connections)
- [Cache Tag Index](Cache_Tag_Index.md) (2 shared connections)
- [In-Memory Cache Backend](In-Memory_Cache_Backend.md) (2 shared connections)
- [Single-Flight Load Collapsing](Single-Flight_Load_Collapsing.md) (1 shared connections)

## Source Files

- `gen_epix/fastapp/cache/manager.py`
- `gen_epix/fastapp/cache/region.py`
- `test/fastapp/unit/cache/test_fastapp_cache_region.py`

## Audit Trail

- EXTRACTED: 237 (80%)
- INFERRED: 58 (20%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*