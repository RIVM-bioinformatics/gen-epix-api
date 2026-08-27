# Transaction Commit/Rollback

> 7 nodes · cohesion 0.29

## Key Concepts

- **.__exit__()** (5 connections) — `gen_epix/fastapp/unit_of_work.py`
- **.commit()** (3 connections) — `gen_epix/fastapp/unit_of_work.py`
- **.rollback()** (3 connections) — `gen_epix/fastapp/unit_of_work.py`
- **Exception** (1 connections)
- **TracebackType** (1 connections)
- **Commit the current transaction. This method should be implemented by subclasses…** (1 connections) — `gen_epix/fastapp/unit_of_work.py`
- **Rollback the current transaction. This method should be implemented by…** (1 connections) — `gen_epix/fastapp/unit_of_work.py`

## Relationships

- [Casedb Case CRUD Commands](Casedb_Case_CRUD_Commands.md) (3 shared connections)

## Source Files

- `gen_epix/fastapp/unit_of_work.py`

## Audit Trail

- EXTRACTED: 9 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*