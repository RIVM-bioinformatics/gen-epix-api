# Request Scope Provider

> 43 nodes · cohesion 0.06

## Key Concepts

- **RequestScope** (14 connections) — `gen_epix/fastapp/cache/scope.py`
- **ScopeProvider** (12 connections) — `gen_epix/fastapp/cache/scope.py`
- **scope.py** (11 connections) — `gen_epix/fastapp/cache/scope.py`
- **ContextVarScopeProvider** (9 connections) — `gen_epix/fastapp/cache/scope.py`
- **NullScopeProvider** (8 connections) — `gen_epix/fastapp/cache/scope.py`
- **StaticScopeProvider** (6 connections) — `gen_epix/fastapp/cache/scope.py`
- **test_a_request_scope_gives_read_your_own_writes()** (6 connections) — `test/fastapp/unit/cache/test_fastapp_cache_region.py`
- **test_a_required_scope_part_must_be_present()** (6 connections) — `test/fastapp/unit/cache/test_fastapp_cache_region.py`
- **test_different_principals_do_not_share_an_entry()** (6 connections) — `test/fastapp/unit/cache/test_fastapp_cache_region.py`
- **.activate()** (4 connections) — `gen_epix/fastapp/cache/scope.py`
- **.bind()** (3 connections) — `gen_epix/fastapp/cache/scope.py`
- **Any** (3 connections)
- **.get()** (3 connections) — `gen_epix/fastapp/cache/scope.py`
- **.set()** (3 connections) — `gen_epix/fastapp/cache/scope.py`
- **.render()** (3 connections) — `gen_epix/fastapp/cache/scope.py`
- **.current()** (2 connections) — `gen_epix/fastapp/cache/scope.py`
- **ABC** (2 connections)
- **.clear()** (2 connections) — `gen_epix/fastapp/cache/scope.py`
- **.discard()** (2 connections) — `gen_epix/fastapp/cache/scope.py`
- **.is_active()** (2 connections) — `gen_epix/fastapp/cache/scope.py`
- **.current()** (2 connections) — `gen_epix/fastapp/cache/scope.py`
- **.__init__()** (2 connections) — `gen_epix/fastapp/cache/scope.py`
- **.current()** (1 connections) — `gen_epix/fastapp/cache/scope.py`
- **Request scope and principal partitioning. Two distinct concerns share this…** (1 connections) — `gen_epix/fastapp/cache/scope.py`
- **Bind identity parts for the duration of the block. Nested binds merge into the…** (1 connections) — `gen_epix/fastapp/cache/scope.py`
- *... and 18 more nodes in this community*

## Relationships

- [Cache Backend Interface](Cache_Backend_Interface.md) (11 shared connections)
- [Cache Error Types](Cache_Error_Types.md) (6 shared connections)
- [Cache Region](Cache_Region.md) (5 shared connections)
- [Cache Region Configuration](Cache_Region_Configuration.md) (3 shared connections)
- [Cache Clock & Config Enums](Cache_Clock_&_Config_Enums.md) (3 shared connections)
- [Cache Decorator Tests](Cache_Decorator_Tests.md) (2 shared connections)

## Source Files

- `gen_epix/fastapp/cache/scope.py`
- `test/fastapp/unit/cache/test_fastapp_cache_region.py`

## Audit Trail

- EXTRACTED: 75 (93%)
- INFERRED: 6 (7%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*