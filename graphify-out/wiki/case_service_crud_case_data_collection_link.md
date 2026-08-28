# case_service_crud_case_data_collection_link

> 14 nodes · cohesion 0.24

## Key Concepts

- **case_service_crud_case_data_collection_link()** (13 connections) — `gen_epix/casedb/services/case/crud_case_data_collection_link.py`
- **_crud_case_data_collection_link_with_abac()** (10 connections) — `gen_epix/casedb/services/case/crud_case_data_collection_link.py`
- **CaseDataCollectionLinkCrudCommand** (9 connections) — `gen_epix/casedb/domain/command/case.py`
- **_crud_case_data_collection_link_without_abac()** (9 connections) — `gen_epix/casedb/services/case/crud_case_data_collection_link.py`
- **.crud_case_data_collection_link()** (6 connections) — `gen_epix/casedb/services/case/service.py`
- **UUID** (4 connections)
- **BaseCaseService** (3 connections)
- **CaseDataCollectionLink** (3 connections)
- **Manage links that associate cases with additional data collections to widen or…** (1 connections) — `gen_epix/casedb/domain/command/case.py`
- **Handle CRUD operations for CaseDataCollectionLink entities.** (1 connections) — `gen_epix/casedb/services/case/crud_case_data_collection_link.py`
- **CaseDataCollectionLink admin command handling.** (1 connections) — `gen_epix/casedb/services/case/crud_case_data_collection_link.py`
- **CaseDataCollectionLink user command handling, ABAC applied.** (1 connections) — `gen_epix/casedb/services/case/crud_case_data_collection_link.py`
- **CaseDataCollectionLink** (1 connections)
- **Handle CRUD operations for CaseDataCollectionLink entities.** (1 connections) — `gen_epix/casedb/services/case/service.py`

## Relationships

- [BaseCaseService](BaseCaseService.md) (10 shared connections)
- [casedb/domain/command/__init__.py](casedb-domain-command-__init__.py.md) (2 shared connections)
- [get_case_abac_from_command](get_case_abac_from_command.md) (2 shared connections)
- [BaseUnitOfWork](BaseUnitOfWork.md) (2 shared connections)
- [CaseService](CaseService.md) (2 shared connections)
- [_crud_cascade_delete](_crud_cascade_delete.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/domain/command/case.py`
- `gen_epix/casedb/services/case/crud_case_data_collection_link.py`
- `gen_epix/casedb/services/case/service.py`

## Audit Trail

- EXTRACTED: 38 (93%)
- INFERRED: 3 (7%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*