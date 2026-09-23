# Manual Clock Test Helpers

> 19 nodes · cohesion 0.11

## Key Concepts

- **ManualClock** (25 connections) — `gen_epix/fastapp/cache/clock.py`
- **InlineRefreshRunner** (11 connections) — `gen_epix/fastapp/cache/lock.py`
- **test_a_stale_entry_is_served_while_it_is_refreshed()** (7 connections) — `test/fastapp/unit/cache/test_fastapp_cache_region.py`
- **test_a_payload_schema_change_invalidates_existing_entries()** (5 connections) — `test/fastapp/unit/cache/test_fastapp_cache_region.py`
- **test_a_manual_clock_only_moves_forward()** (3 connections) — `test/fastapp/unit/cache/test_fastapp_cache_support.py`
- **.advance()** (2 connections) — `gen_epix/fastapp/cache/clock.py`
- **.__init__()** (2 connections) — `gen_epix/fastapp/cache/clock.py`
- **.set()** (2 connections) — `gen_epix/fastapp/cache/clock.py`
- **.monotonic()** (1 connections) — `gen_epix/fastapp/cache/clock.py`
- **.time()** (1 connections) — `gen_epix/fastapp/cache/clock.py`
- **Encapsulates advancing only when a test tells it to. Both readings start at…** (1 connections) — `gen_epix/fastapp/cache/clock.py`
- **Initialize a ManualClock instance.** (1 connections) — `gen_epix/fastapp/cache/clock.py`
- **Move the clock forward and return the new reading. Args: seconds: A non-…** (1 connections) — `gen_epix/fastapp/cache/clock.py`
- **Set both readings to an absolute value. Args: value: The new reading. Raises:…** (1 connections) — `gen_epix/fastapp/cache/clock.py`
- **.submit()** (1 connections) — `gen_epix/fastapp/cache/lock.py`
- **Encapsulates refreshing stale entries on the calling thread. This makes a stale…** (1 connections) — `gen_epix/fastapp/cache/lock.py`
- **A soft time to live trades bounded staleness for a fast read.** (1 connections) — `test/fastapp/unit/cache/test_fastapp_cache_region.py`
- **A release that changes the payload layout must not read old entries.** (1 connections) — `test/fastapp/unit/cache/test_fastapp_cache_region.py`
- **Time going backwards would resurrect expired entries.** (1 connections) — `test/fastapp/unit/cache/test_fastapp_cache_support.py`

## Relationships

- [Cache Backend Interface](Cache_Backend_Interface.md) (11 shared connections)
- [Cache Clock & Config Enums](Cache_Clock_&_Config_Enums.md) (8 shared connections)
- [Cache Error Types](Cache_Error_Types.md) (7 shared connections)
- [Cache Region](Cache_Region.md) (3 shared connections)
- [Cache Decorator Tests](Cache_Decorator_Tests.md) (2 shared connections)
- [Cache Region Configuration](Cache_Region_Configuration.md) (1 shared connections)

## Source Files

- `gen_epix/fastapp/cache/clock.py`
- `gen_epix/fastapp/cache/lock.py`
- `test/fastapp/unit/cache/test_fastapp_cache_region.py`
- `test/fastapp/unit/cache/test_fastapp_cache_support.py`

## Audit Trail

- EXTRACTED: 48 (96%)
- INFERRED: 2 (4%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*