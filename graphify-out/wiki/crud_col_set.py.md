# crud_col_set.py

> 16 nodes · cohesion 0.22

## Key Concepts

- **crud_col_set.py** (14 connections) — `gen_epix/casedb/services/case/crud_col_set.py`
- **case_service_crud_col_set()** (11 connections) — `gen_epix/casedb/services/case/crud_col_set.py`
- **_crud_col_set_with_abac()** (10 connections) — `gen_epix/casedb/services/case/crud_col_set.py`
- **ColSetCrudCommand** (9 connections) — `gen_epix/casedb/domain/command/case.py`
- **_crud_col_set_without_abac()** (9 connections) — `gen_epix/casedb/services/case/crud_col_set.py`
- **.crud_col_set()** (6 connections) — `gen_epix/casedb/services/case/service.py`
- **UUID** (4 connections)
- **BaseCaseService** (3 connections)
- **ColSet** (3 connections)
- **Manage column sets used for read/write scopes and default column groupings.** (1 connections) — `gen_epix/casedb/domain/command/case.py`
- **CRUD operations for ColSet entities.** (1 connections) — `gen_epix/casedb/services/case/crud_col_set.py`
- **Handle CRUD operations for ColSet entities.** (1 connections) — `gen_epix/casedb/services/case/crud_col_set.py`
- **ColSet admin command handling, no ABAC applied.** (1 connections) — `gen_epix/casedb/services/case/crud_col_set.py`
- **ColSet user command handling, ABAC applied.** (1 connections) — `gen_epix/casedb/services/case/crud_col_set.py`
- **ColSet** (1 connections)
- **Handle CRUD operations for ColSet entities.** (1 connections) — `gen_epix/casedb/services/case/service.py`

## Relationships

- [BaseCaseService](BaseCaseService.md) (10 shared connections)
- [_crud_cascade_delete](_crud_cascade_delete.md) (6 shared connections)
- [BaseUnitOfWork](BaseUnitOfWork.md) (4 shared connections)
- [casedb/domain/command/__init__.py](casedb-domain-command-__init__.py.md) (2 shared connections)
- [CaseService](CaseService.md) (2 shared connections)

## Source Files

- `gen_epix/casedb/domain/command/case.py`
- `gen_epix/casedb/services/case/crud_col_set.py`
- `gen_epix/casedb/services/case/service.py`

## Audit Trail

- EXTRACTED: 47 (94%)
- INFERRED: 3 (6%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*