# get_case_abac_from_command

> 49 nodes · cohesion 0.08

## Key Concepts

- **get_case_abac_from_command()** (17 connections) — `gen_epix/casedb/services/case/crud_common.py`
- **is_app_admin_or_above()** (17 connections) — `gen_epix/casedb/services/case/crud_common.py`
- **crud_case_set_data_collection_link.py** (16 connections) — `gen_epix/casedb/services/case/crud_case_set_data_collection_link.py`
- **crud_case_set_member.py** (16 connections) — `gen_epix/casedb/services/case/crud_case_set_member.py`
- **crud_case_identifier.py** (15 connections) — `gen_epix/casedb/services/case/crud_case_identifier.py`
- **case_service_crud_case_identifier()** (13 connections) — `gen_epix/casedb/services/case/crud_case_identifier.py`
- **case_service_crud_case_set_data_collection_link()** (13 connections) — `gen_epix/casedb/services/case/crud_case_set_data_collection_link.py`
- **case_service_crud_case_set_member()** (13 connections) — `gen_epix/casedb/services/case/crud_case_set_member.py`
- **_crud_case_identifier_with_abac()** (10 connections) — `gen_epix/casedb/services/case/crud_case_identifier.py`
- **_crud_case_set_data_collection_link_with_abac()** (10 connections) — `gen_epix/casedb/services/case/crud_case_set_data_collection_link.py`
- **_crud_case_set_data_collection_link_without_abac()** (10 connections) — `gen_epix/casedb/services/case/crud_case_set_data_collection_link.py`
- **_crud_case_set_member_with_abac()** (10 connections) — `gen_epix/casedb/services/case/crud_case_set_member.py`
- **_crud_case_set_member_without_abac()** (10 connections) — `gen_epix/casedb/services/case/crud_case_set_member.py`
- **CaseIdentifierCrudCommand** (9 connections) — `gen_epix/casedb/domain/command/case.py`
- **CaseSetDataCollectionLinkCrudCommand** (9 connections) — `gen_epix/casedb/domain/command/case.py`
- **CaseSetMemberCrudCommand** (9 connections) — `gen_epix/casedb/domain/command/case.py`
- **_crud_case_identifier_without_abac()** (9 connections) — `gen_epix/casedb/services/case/crud_case_identifier.py`
- **.crud_case_set_data_collection_link()** (6 connections) — `gen_epix/casedb/services/case/service.py`
- **.crud_case_set_member()** (6 connections) — `gen_epix/casedb/services/case/service.py`
- **UUID** (4 connections)
- **UUID** (4 connections)
- **UUID** (4 connections)
- **BaseCaseService** (3 connections)
- **CaseIdentifier** (3 connections)
- **BaseCaseService** (3 connections)
- *... and 24 more nodes in this community*

## Relationships

- [BaseCaseService](BaseCaseService.md) (43 shared connections)
- [BaseUnitOfWork](BaseUnitOfWork.md) (12 shared connections)
- [_crud_cascade_delete](_crud_cascade_delete.md) (11 shared connections)
- [CaseService](CaseService.md) (7 shared connections)
- [casedb/domain/command/__init__.py](casedb-domain-command-__init__.py.md) (6 shared connections)
- [BaseCrudTestCase](BaseCrudTestCase.md) (4 shared connections)
- [case_service_crud_case_data_collection_link](case_service_crud_case_data_collection_link.md) (2 shared connections)
- [CaseAbac](CaseAbac.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/domain/command/case.py`
- `gen_epix/casedb/services/case/crud_case_identifier.py`
- `gen_epix/casedb/services/case/crud_case_set_data_collection_link.py`
- `gen_epix/casedb/services/case/crud_case_set_member.py`
- `gen_epix/casedb/services/case/crud_common.py`
- `gen_epix/casedb/services/case/service.py`

## Audit Trail

- EXTRACTED: 168 (94%)
- INFERRED: 10 (6%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*