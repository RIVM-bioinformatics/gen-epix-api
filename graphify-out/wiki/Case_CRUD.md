# Case CRUD

> 5 nodes · cohesion 0.40

## Key Concepts

- **.crud_case()** (5 connections) — `gen_epix/casedb/domain/service/case.py`
- **.retrieve_cases_by_id()** (4 connections) — `gen_epix/casedb/domain/service/case.py`
- **Case** (2 connections)
- **Handle CRUD operations for Case entities.** (1 connections) — `gen_epix/casedb/domain/service/case.py`
- **Retrieve cases by their IDs.** (1 connections) — `gen_epix/casedb/domain/service/case.py`

## Relationships

- [Case Service CRUD](Case_Service_CRUD.md) (3 shared connections)
- [Case CRUD Command](Case_CRUD_Command.md) (1 shared connections)
- [Casedb Domain CRUD Commands](Casedb_Domain_CRUD_Commands.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/domain/service/case.py`

## Audit Trail

- EXTRACTED: 9 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*