# Case CRUD Command

> 13 nodes · cohesion 0.27

## Key Concepts

- **case_service_crud_case()** (13 connections) — `gen_epix/casedb/services/case/crud_case.py`
- **CaseCrudCommand** (11 connections) — `gen_epix/casedb/domain/command/case.py`
- **_crud_case_with_abac()** (11 connections) — `gen_epix/casedb/services/case/crud_case.py`
- **_crud_case_without_abac()** (9 connections) — `gen_epix/casedb/services/case/crud_case.py`
- **.crud_case()** (6 connections) — `gen_epix/casedb/services/case/service.py`
- **UUID** (4 connections)
- **BaseCaseService** (3 connections)
- **Case** (3 connections)
- **Manage cases (list/get/create/update/delete) with typed content tied to a…** (1 connections) — `gen_epix/casedb/domain/command/case.py`
- **Handle CRUD operations for Case entities.** (1 connections) — `gen_epix/casedb/services/case/crud_case.py`
- **Case admin command handling, no ABAC applied.** (1 connections) — `gen_epix/casedb/services/case/crud_case.py`
- **Case user command handling, ABAC applied.** (1 connections) — `gen_epix/casedb/services/case/crud_case.py`
- **Handle CRUD operations for Case entities.** (1 connections) — `gen_epix/casedb/services/case/service.py`

## Relationships

- [Casedb Case CRUD Commands](Casedb_Case_CRUD_Commands.md) (14 shared connections)
- [Casedb Domain CRUD Commands](Casedb_Domain_CRUD_Commands.md) (4 shared connections)
- [Casedb Case Service](Casedb_Case_Service.md) (3 shared connections)
- [Commondb Enums & Demo Data](Commondb_Enums_&_Demo_Data.md) (1 shared connections)
- [Case CRUD](Case_CRUD.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/domain/command/case.py`
- `gen_epix/casedb/services/case/crud_case.py`
- `gen_epix/casedb/services/case/service.py`

## Audit Trail

- EXTRACTED: 41 (93%)
- INFERRED: 3 (7%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*