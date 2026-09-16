# Cache Error Types

> 7 nodes · cohesion 0.29

## Key Concepts

- **CacheError** (8 connections) — `gen_epix/fastapp/cache/exc.py`
- **KeyRejectedError** (6 connections) — `gen_epix/fastapp/cache/exc.py`
- **test_an_admission_policy_can_refuse_a_key()** (5 connections) — `test/fastapp/unit/cache/test_fastapp_cache_region.py`
- **Exception** (1 connections)
- **Error for a cache key refused by the configured admission policy.** (1 connections) — `gen_epix/fastapp/cache/exc.py`
- **Base error for every failure originating in the cache framework.** (1 connections) — `gen_epix/fastapp/cache/exc.py`
- **A key space that untrusted input can influence must stay bounded.** (1 connections) — `test/fastapp/unit/cache/test_fastapp_cache_region.py`

## Relationships

- [Cache Backend Interface](Cache_Backend_Interface.md) (5 shared connections)
- [Cache Error Types](Cache_Error_Types.md) (3 shared connections)
- [Cache Clock & Config Enums](Cache_Clock_&_Config_Enums.md) (2 shared connections)
- [Cache Region](Cache_Region.md) (1 shared connections)

## Source Files

- `gen_epix/fastapp/cache/exc.py`
- `test/fastapp/unit/cache/test_fastapp_cache_region.py`

## Audit Trail

- EXTRACTED: 16 (94%)
- INFERRED: 1 (6%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*