# Null Mutex Implementation

> 5 nodes · cohesion 0.40

## Key Concepts

- **NullMutex** (6 connections) — `gen_epix/fastapp/cache/lock.py`
- **.acquire()** (1 connections) — `gen_epix/fastapp/cache/lock.py`
- **.locked()** (1 connections) — `gen_epix/fastapp/cache/lock.py`
- **.release()** (1 connections) — `gen_epix/fastapp/cache/lock.py`
- **Encapsulates granting every acquisition immediately. Use this to disable…** (1 connections) — `gen_epix/fastapp/cache/lock.py`

## Relationships

- [Cache Error Types](Cache_Error_Types.md) (1 shared connections)
- [Cache Backend Interface](Cache_Backend_Interface.md) (1 shared connections)

## Source Files

- `gen_epix/fastapp/cache/lock.py`

## Audit Trail

- EXTRACTED: 6 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*