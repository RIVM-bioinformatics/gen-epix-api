# Cache Region Configuration

> 38 nodes · cohesion 0.06

## Key Concepts

- **.__init__()** (29 connections) — `gen_epix/fastapp/cache/region.py`
- **MemoryVersionStore** (18 connections) — `gen_epix/fastapp/cache/version.py`
- **VersionStore** (16 connections) — `gen_epix/fastapp/cache/version.py`
- **RefreshRunner** (8 connections) — `gen_epix/fastapp/cache/lock.py`
- **version.py** (8 connections) — `gen_epix/fastapp/cache/version.py`
- **._create_backend()** (5 connections) — `gen_epix/fastapp/cache/region.py`
- **._create_failure_policy()** (5 connections) — `gen_epix/fastapp/cache/region.py`
- **test_a_generation_never_moves_backwards()** (3 connections) — `test/fastapp/unit/cache/test_fastapp_cache_invalidation.py`
- **Protocol** (2 connections)
- **.submit()** (2 connections) — `gen_epix/fastapp/cache/lock.py`
- **Random** (2 connections)
- **.__init__()** (2 connections) — `gen_epix/fastapp/cache/version.py`
- **ABC** (2 connections)
- **.bump()** (2 connections) — `gen_epix/fastapp/cache/version.py`
- **.get()** (2 connections) — `gen_epix/fastapp/cache/version.py`
- **.reset()** (2 connections) — `gen_epix/fastapp/cache/version.py`
- **.set()** (2 connections) — `gen_epix/fastapp/cache/version.py`
- **.snapshot()** (2 connections) — `gen_epix/fastapp/cache/version.py`
- **Encapsulates deciding where the refresh of a stale entry executes.** (1 connections) — `gen_epix/fastapp/cache/lock.py`
- **Schedule `work` for execution. Args: work: A callable that refreshes one cache…** (1 connections) — `gen_epix/fastapp/cache/lock.py`
- **Initialize a CacheRegion instance. Args: config: The declarative policy of this…** (1 connections) — `gen_epix/fastapp/cache/region.py`
- **Return the default failure policy implied by the configuration. A configured…** (1 connections) — `gen_epix/fastapp/cache/region.py`
- **Return the default in-memory backend wired to the tag index.** (1 connections) — `gen_epix/fastapp/cache/region.py`
- **.bump()** (1 connections) — `gen_epix/fastapp/cache/version.py`
- **.get()** (1 connections) — `gen_epix/fastapp/cache/version.py`
- *... and 13 more nodes in this community*

## Relationships

- [Cache Clock & Config Enums](Cache_Clock_&_Config_Enums.md) (16 shared connections)
- [Cache Backend Interface](Cache_Backend_Interface.md) (12 shared connections)
- [Cache Error Types](Cache_Error_Types.md) (7 shared connections)
- [Cache Region](Cache_Region.md) (7 shared connections)
- [Request Scope Provider](Request_Scope_Provider.md) (3 shared connections)
- [Cache Tag Index](Cache_Tag_Index.md) (2 shared connections)
- [Cache Statistics](Cache_Statistics.md) (2 shared connections)
- [In-Memory Cache Backend](In-Memory_Cache_Backend.md) (1 shared connections)
- [Manual Clock Test Helpers](Manual_Clock_Test_Helpers.md) (1 shared connections)
- [Single-Flight Load Collapsing](Single-Flight_Load_Collapsing.md) (1 shared connections)

## Source Files

- `gen_epix/fastapp/cache/lock.py`
- `gen_epix/fastapp/cache/region.py`
- `gen_epix/fastapp/cache/version.py`
- `test/fastapp/unit/cache/test_fastapp_cache_invalidation.py`

## Audit Trail

- EXTRACTED: 87 (95%)
- INFERRED: 5 (5%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*