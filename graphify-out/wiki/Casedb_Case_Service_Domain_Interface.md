# Casedb Case Service Domain Interface

> 100 nodes

## Key Concepts

- **BaseCaseService** (45 connections) — `gen_epix/casedb/domain/service/case.py`
- **UUID** (25 connections)
- **CrudCommand** (21 connections)
- **case_service_crud_case()** (13 connections) — `gen_epix/casedb/services/case/crud_case.py`
- **CaseCrudCommand** (11 connections) — `gen_epix/casedb/domain/command/case.py`
- **_crud_case_with_abac()** (11 connections) — `gen_epix/casedb/services/case/crud_case.py`
- **CaseTypeSetCategoryCrudCommand** (9 connections) — `gen_epix/casedb/domain/command/case.py`
- **_crud_case_without_abac()** (9 connections) — `gen_epix/casedb/services/case/crud_case.py`
- **CaseSetCategoryCrudCommand** (7 connections) — `gen_epix/casedb/domain/command/case.py`
- **CaseSetStatusCrudCommand** (7 connections) — `gen_epix/casedb/domain/command/case.py`
- **GeneticDistanceProtocolCrudCommand** (7 connections) — `gen_epix/casedb/domain/command/case.py`
- **.crud_case()** (6 connections) — `gen_epix/casedb/services/case/service.py`
- **.crud_case()** (5 connections) — `gen_epix/casedb/domain/service/case.py`
- **.crud_case_data_collection_link()** (5 connections) — `gen_epix/casedb/domain/service/case.py`
- **.crud_case_identifier()** (5 connections) — `gen_epix/casedb/domain/service/case.py`
- **.crud_case_set()** (5 connections) — `gen_epix/casedb/domain/service/case.py`
- **.crud_case_set_category()** (5 connections) — `gen_epix/casedb/domain/service/case.py`
- **.crud_case_set_data_collection_link()** (5 connections) — `gen_epix/casedb/domain/service/case.py`
- **.crud_case_set_member()** (5 connections) — `gen_epix/casedb/domain/service/case.py`
- **.crud_case_set_status()** (5 connections) — `gen_epix/casedb/domain/service/case.py`
- **.crud_case_type()** (5 connections) — `gen_epix/casedb/domain/service/case.py`
- **.crud_case_type_set()** (5 connections) — `gen_epix/casedb/domain/service/case.py`
- **.crud_case_type_set_category()** (5 connections) — `gen_epix/casedb/domain/service/case.py`
- **.crud_case_type_set_member()** (5 connections) — `gen_epix/casedb/domain/service/case.py`
- **.crud_col()** (5 connections) — `gen_epix/casedb/domain/service/case.py`
- *... and 75 more nodes in this community*

## Relationships

- [Casedb Case Service Implementation](Casedb_Case_Service_Implementation.md) (15 shared connections)
- [casedb/domain/command/__init__.py](casedb-domain-command-__init__.py.md) (14 shared connections)
- [_crud_cascade_delete](_crud_cascade_delete.md) (12 shared connections)
- [get_case_abac_from_command](get_case_abac_from_command.md) (8 shared connections)
- [CaseService](CaseService.md) (7 shared connections)
- [TestcasedbEdgeCasesRefDataAccess](TestcasedbEdgeCasesRefDataAccess.md) (4 shared connections)
- [casedb/domain/enum.py](casedb-domain-enum.py.md) (4 shared connections)
- [commondb/domain/enum.py](commondb-domain-enum.py.md) (2 shared connections)
- [Command](Command.md) (2 shared connections)
- [case_service_create_file_for_read_set_or_seq](case_service_create_file_for_read_set_or_seq.md) (2 shared connections)
- [case_service_crud_case_data_collection_link](case_service_crud_case_data_collection_link.md) (2 shared connections)
- [BaseCrudTestCase](BaseCrudTestCase.md) (2 shared connections)

## Source Files

- `gen_epix/casedb/domain/command/case.py`
- `gen_epix/casedb/domain/service/case.py`
- `gen_epix/casedb/services/case/crud_case.py`
- `gen_epix/casedb/services/case/service.py`

## Audit Trail

- EXTRACTED: 226 (98%)
- INFERRED: 4 (2%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*