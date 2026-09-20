# Single-Flight Load Collapsing

> 26 nodes · cohesion 0.08

## Key Concepts

- **SingleFlight** (15 connections) — `gen_epix/fastapp/cache/lock.py`
- **_Call** (5 connections) — `gen_epix/fastapp/cache/lock.py`
- **.run()** (4 connections) — `gen_epix/fastapp/cache/lock.py`
- **.run()** (3 connections) — `gen_epix/fastapp/cache/lock.py`
- **.try_start()** (3 connections) — `gen_epix/fastapp/cache/lock.py`
- **test_a_refresh_leader_is_elected_only_once()** (3 connections) — `test/fastapp/unit/cache/test_fastapp_cache_support.py`
- **test_every_waiter_receives_the_failure_of_the_leader()** (3 connections) — `test/fastapp/unit/cache/test_fastapp_cache_support.py`
- **test_single_flight_runs_one_loader_per_key()** (3 connections) — `test/fastapp/unit/cache/test_fastapp_cache_support.py`
- **.is_in_flight()** (2 connections) — `gen_epix/fastapp/cache/lock.py`
- **.__init__()** (2 connections) — `gen_epix/fastapp/cache/lock.py`
- **Any** (2 connections)
- **Return whether a load for `key` is currently running.** (2 connections) — `gen_epix/fastapp/cache/lock.py`
- **.finish()** (2 connections) — `gen_epix/fastapp/cache/lock.py`
- **.__init__()** (2 connections) — `gen_epix/fastapp/cache/lock.py`
- **.is_in_flight()** (2 connections) — `gen_epix/fastapp/cache/lock.py`
- **Encapsulates holding the shared outcome of one in-flight load. Attributes:…** (1 connections) — `gen_epix/fastapp/cache/lock.py`
- **Initialize a _Call instance.** (1 connections) — `gen_epix/fastapp/cache/lock.py`
- **Encapsulates collapsing concurrent loads of the same key into one execution.…** (1 connections) — `gen_epix/fastapp/cache/lock.py`
- **Initialize a SingleFlight instance.** (1 connections) — `gen_epix/fastapp/cache/lock.py`
- **Return the result of `loader`, executing it at most once per key. Args: key:…** (1 connections) — `gen_epix/fastapp/cache/lock.py`
- **Claim leadership for `key` without blocking. A stale-while-revalidate read uses…** (1 connections) — `gen_epix/fastapp/cache/lock.py`
- **Release leadership claimed through `try_start`. Args: key: The cache key whose…** (1 connections) — `gen_epix/fastapp/cache/lock.py`
- **Return the result of awaiting `loader`, running it once per key. Args: key: The…** (1 connections) — `gen_epix/fastapp/cache/lock.py`
- **Different keys must not block each other while one key loads.** (1 connections) — `test/fastapp/unit/cache/test_fastapp_cache_support.py`
- **A failed load must not be retried once per waiting caller.** (1 connections) — `test/fastapp/unit/cache/test_fastapp_cache_support.py`
- *... and 1 more nodes in this community*

## Relationships

- [Cache Backend Interface](Cache_Backend_Interface.md) (5 shared connections)
- [Cache Error Types](Cache_Error_Types.md) (5 shared connections)
- [Cache Region Configuration](Cache_Region_Configuration.md) (1 shared connections)
- [Cache Region](Cache_Region.md) (1 shared connections)

## Source Files

- `gen_epix/fastapp/cache/lock.py`
- `test/fastapp/unit/cache/test_fastapp_cache_support.py`

## Audit Trail

- EXTRACTED: 37 (97%)
- INFERRED: 1 (3%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*