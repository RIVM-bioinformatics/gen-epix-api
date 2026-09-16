# Context Manager Entry

> 5 nodes · cohesion 0.40

## Key Concepts

- **.__enter__()** (3 connections) — `gen_epix/fastapp/repositories/sa/unit_of_work.py`
- **.__enter__()** (3 connections) — `gen_epix/fastapp/unit_of_work.py`
- **Enter the managed context.** (2 connections) — `gen_epix/fastapp/unit_of_work.py`
- **Self** (1 connections)
- **Self** (1 connections)

## Relationships

- [Database Session Isolation](Database_Session_Isolation.md) (1 shared connections)
- [SQLAlchemy Case Repository](SQLAlchemy_Case_Repository.md) (1 shared connections)

## Source Files

- `gen_epix/fastapp/repositories/sa/unit_of_work.py`
- `gen_epix/fastapp/unit_of_work.py`

## Audit Trail

- EXTRACTED: 6 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*