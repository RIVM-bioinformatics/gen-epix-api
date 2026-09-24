# Memory Cache Eviction

> 64 nodes · cohesion 0.03

## Key Concepts

- **EvictionStrategy** (20 connections) — `gen_epix/fastapp/cache/eviction.py`
- **LFUEviction** (14 connections) — `gen_epix/fastapp/cache/eviction.py`
- **LRUEviction** (14 connections) — `gen_epix/fastapp/cache/eviction.py`
- **FIFOEviction** (12 connections) — `gen_epix/fastapp/cache/eviction.py`
- **RandomEviction** (12 connections) — `gen_epix/fastapp/cache/eviction.py`
- **.__init__()** (9 connections) — `gen_epix/fastapp/cache/backend/memory.py`
- **.__init__()** (3 connections) — `gen_epix/fastapp/cache/eviction.py`
- **test_least_frequently_used_entry_is_evicted_first()** (3 connections) — `test/fastapp/unit/cache/test_fastapp_cache_backend.py`
- **test_lru_strategy_forgets_removed_keys()** (3 connections) — `test/fastapp/unit/cache/test_fastapp_cache_backend.py`
- **.admit()** (2 connections) — `gen_epix/fastapp/cache/eviction.py`
- **.clear()** (2 connections) — `gen_epix/fastapp/cache/eviction.py`
- **.keys()** (2 connections) — `gen_epix/fastapp/cache/eviction.py`
- **.record_access()** (2 connections) — `gen_epix/fastapp/cache/eviction.py`
- **.record_removal()** (2 connections) — `gen_epix/fastapp/cache/eviction.py`
- **.record_write()** (2 connections) — `gen_epix/fastapp/cache/eviction.py`
- **.victim()** (2 connections) — `gen_epix/fastapp/cache/eviction.py`
- **.__init__()** (2 connections) — `gen_epix/fastapp/cache/eviction.py`
- **.record_write()** (2 connections) — `gen_epix/fastapp/cache/eviction.py`
- **.__init__()** (2 connections) — `gen_epix/fastapp/cache/eviction.py`
- **.__init__()** (2 connections) — `gen_epix/fastapp/cache/eviction.py`
- **ABC** (2 connections)
- **Initialize an LRUEviction instance.** (2 connections) — `gen_epix/fastapp/cache/eviction.py`
- **Initialize a MemoryBackend instance. Args: max_weight: Total weight the store…** (1 connections) — `gen_epix/fastapp/cache/backend/memory.py`
- **.clear()** (1 connections) — `gen_epix/fastapp/cache/eviction.py`
- **.keys()** (1 connections) — `gen_epix/fastapp/cache/eviction.py`
- *... and 39 more nodes in this community*

## Relationships

- [Cache Backend Interface](Cache_Backend_Interface.md) (19 shared connections)
- [Cache Error Types](Cache_Error_Types.md) (5 shared connections)
- [Cache Clock & Config Enums](Cache_Clock_&_Config_Enums.md) (2 shared connections)
- [In-Memory Cache Backend](In-Memory_Cache_Backend.md) (2 shared connections)
- [Cache Statistics](Cache_Statistics.md) (1 shared connections)
- [Count-Min Sketch](Count-Min_Sketch.md) (1 shared connections)

## Source Files

- `gen_epix/fastapp/cache/backend/memory.py`
- `gen_epix/fastapp/cache/eviction.py`
- `test/fastapp/unit/cache/test_fastapp_cache_backend.py`

## Audit Trail

- EXTRACTED: 93 (99%)
- INFERRED: 1 (1%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*