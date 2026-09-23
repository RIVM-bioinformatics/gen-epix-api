# In-Memory Cache Backend

> 39 nodes · cohesion 0.07

## Key Concepts

- **MemoryBackend** (50 connections) — `gen_epix/fastapp/cache/backend/memory.py`
- **ThreadMutex** (10 connections) — `gen_epix/fastapp/cache/lock.py`
- **._remove()** (9 connections) — `gen_epix/fastapp/cache/backend/memory.py`
- **._record()** (7 connections) — `gen_epix/fastapp/cache/backend/memory.py`
- **.get()** (6 connections) — `gen_epix/fastapp/cache/backend/memory.py`
- **._notify()** (6 connections) — `gen_epix/fastapp/cache/backend/memory.py`
- **.set()** (6 connections) — `gen_epix/fastapp/cache/backend/memory.py`
- **._enforce_capacity()** (5 connections) — `gen_epix/fastapp/cache/backend/memory.py`
- **.delete()** (4 connections) — `gen_epix/fastapp/cache/backend/memory.py`
- **.expire()** (4 connections) — `gen_epix/fastapp/cache/backend/memory.py`
- **.get_mutex()** (4 connections) — `gen_epix/fastapp/cache/backend/memory.py`
- **test_a_non_positive_capacity_is_rejected()** (4 connections) — `test/fastapp/unit/cache/test_fastapp_cache_backend.py`
- **.clear()** (3 connections) — `gen_epix/fastapp/cache/backend/memory.py`
- **.close()** (2 connections) — `gen_epix/fastapp/cache/backend/memory.py`
- **.delete_multi()** (2 connections) — `gen_epix/fastapp/cache/backend/memory.py`
- **.keys()** (2 connections) — `gen_epix/fastapp/cache/backend/memory.py`
- **.__len__()** (2 connections) — `gen_epix/fastapp/cache/backend/memory.py`
- **.set_multi()** (2 connections) — `gen_epix/fastapp/cache/backend/memory.py`
- **.weight()** (2 connections) — `gen_epix/fastapp/cache/backend/memory.py`
- **.__init__()** (2 connections) — `gen_epix/fastapp/cache/lock.py`
- **.contains()** (1 connections) — `gen_epix/fastapp/cache/backend/memory.py`
- **See base method. Storing over an existing key reports the previous envelope as…** (1 connections) — `gen_epix/fastapp/cache/backend/memory.py`
- **See base method. The snapshot is taken under the lock, so iteration is safe…** (1 connections) — `gen_epix/fastapp/cache/backend/memory.py`
- **Remove every entry that passed its hard expiry. Lazy expiry only reclaims…** (1 connections) — `gen_epix/fastapp/cache/backend/memory.py`
- **See base method. A process-local store needs no distributed mutex, so a plain…** (1 connections) — `gen_epix/fastapp/cache/backend/memory.py`
- *... and 14 more nodes in this community*

## Relationships

- [Cache Backend Interface](Cache_Backend_Interface.md) (30 shared connections)
- [Cache Statistics](Cache_Statistics.md) (3 shared connections)
- [Cache Clock & Config Enums](Cache_Clock_&_Config_Enums.md) (3 shared connections)
- [Cache Region](Cache_Region.md) (2 shared connections)
- [Cache Error Types](Cache_Error_Types.md) (2 shared connections)
- [Memory Cache Eviction](Memory_Cache_Eviction.md) (2 shared connections)
- [Cache Region Configuration](Cache_Region_Configuration.md) (1 shared connections)

## Source Files

- `gen_epix/fastapp/cache/backend/memory.py`
- `gen_epix/fastapp/cache/lock.py`
- `test/fastapp/unit/cache/test_fastapp_cache_backend.py`

## Audit Trail

- EXTRACTED: 84 (87%)
- INFERRED: 13 (13%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*