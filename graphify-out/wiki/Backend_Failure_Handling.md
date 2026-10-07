# Backend Failure Handling

> 6 nodes · cohesion 0.40

## Key Concepts

- **._handle()** (5 connections) — `gen_epix/fastapp/cache/resilience.py`
- **.run()** (4 connections) — `gen_epix/fastapp/cache/resilience.py`
- **_T** (3 connections)
- **BaseException** (2 connections)
- **Run a backend operation under the configured protections. The breaker is…** (1 connections) — `gen_epix/fastapp/cache/resilience.py`
- **Absorb or re-raise a failure according to the configured mode. Args: exception:…** (1 connections) — `gen_epix/fastapp/cache/resilience.py`

## Relationships

- [Cache Backend Interface](Cache_Backend_Interface.md) (2 shared connections)
- [Cache Error Types](Cache_Error_Types.md) (1 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (1 shared connections)

## Source Files

- `gen_epix/fastapp/cache/resilience.py`

## Audit Trail

- EXTRACTED: 10 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*