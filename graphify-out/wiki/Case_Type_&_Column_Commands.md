# Case Type & Column Commands

> 98 nodes · cohesion 0.04

## Key Concepts

- **BaseCaseService** (121 connections) — `gen_epix/casedb/services/case/base.py`
- **crud_with_access_filter()** (28 connections) — `gen_epix/casedb/services/case/crud_common.py`
- **get_ref_data_access_from_command()** (22 connections) — `gen_epix/casedb/services/case/crud_common.py`
- **CaseTypeCrudCommand** (20 connections) — `gen_epix/casedb/domain/command/case.py`
- **crud_col.py** (18 connections) — `gen_epix/casedb/services/case/crud_col.py`
- **crud_case_type.py** (15 connections) — `gen_epix/casedb/services/case/crud_case_type.py`
- **crud_case_type_set.py** (15 connections) — `gen_epix/casedb/services/case/crud_case_type_set.py`
- **crud_col_set_member.py** (15 connections) — `gen_epix/casedb/services/case/crud_col_set_member.py`
- **crud_ref_dim.py** (15 connections) — `gen_epix/casedb/services/case/crud_ref_dim.py`
- **crud_case_type_set_member.py** (14 connections) — `gen_epix/casedb/services/case/crud_case_type_set_member.py`
- **crud_col_set.py** (14 connections) — `gen_epix/casedb/services/case/crud_col_set.py`
- **ColCrudCommand** (13 connections) — `gen_epix/casedb/domain/command/case.py`
- **is_refdata_admin_or_above()** (13 connections) — `gen_epix/casedb/services/case/crud_common.py`
- **CaseTypeSetCrudCommand** (11 connections) — `gen_epix/casedb/domain/command/case.py`
- **case_service_crud_case_type()** (10 connections) — `gen_epix/casedb/services/case/crud_case_type.py`
- **_crud_case_type_with_abac()** (10 connections) — `gen_epix/casedb/services/case/crud_case_type.py`
- **_crud_case_type_set_with_abac()** (10 connections) — `gen_epix/casedb/services/case/crud_case_type_set.py`
- **case_service_crud_col()** (10 connections) — `gen_epix/casedb/services/case/crud_col.py`
- **_crud_col_with_abac()** (10 connections) — `gen_epix/casedb/services/case/crud_col.py`
- **_crud_col_set_member_with_abac()** (10 connections) — `gen_epix/casedb/services/case/crud_col_set_member.py`
- **case_service_crud_ref_dim()** (10 connections) — `gen_epix/casedb/services/case/crud_ref_dim.py`
- **_crud_ref_dim_with_abac()** (10 connections) — `gen_epix/casedb/services/case/crud_ref_dim.py`
- **CaseTypeSetMemberCrudCommand** (9 connections) — `gen_epix/casedb/domain/command/case.py`
- **ColSetCrudCommand** (9 connections) — `gen_epix/casedb/domain/command/case.py`
- **ColSetMemberCrudCommand** (9 connections) — `gen_epix/casedb/domain/command/case.py`
- *... and 73 more nodes in this community*

## Relationships

- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (48 shared connections)
- [Case CRUD Service Operations](Case_CRUD_Service_Operations.md) (46 shared connections)
- [SQLAlchemy Case Repository](SQLAlchemy_Case_Repository.md) (30 shared connections)
- [Dimension CRUD Service](Dimension_CRUD_Service.md) (18 shared connections)
- [Sequence File Creation](Sequence_File_Creation.md) (14 shared connections)
- [Case Association Retrieval](Case_Association_Retrieval.md) (10 shared connections)
- [Geographic Region Commands](Geographic_Region_Commands.md) (9 shared connections)
- [Base Case Service Interface](Base_Case_Service_Interface.md) (8 shared connections)
- [Reference Column CRUD](Reference_Column_CRUD.md) (7 shared connections)
- [Case Service Implementation](Case_Service_Implementation.md) (6 shared connections)
- [Case Type Access Tests](Case_Type_Access_Tests.md) (5 shared connections)
- [Case Set CRUD Handling](Case_Set_CRUD_Handling.md) (5 shared connections)

## Source Files

- `gen_epix/casedb/domain/command/case.py`
- `gen_epix/casedb/services/case/base.py`
- `gen_epix/casedb/services/case/crud_case_type.py`
- `gen_epix/casedb/services/case/crud_case_type_set.py`
- `gen_epix/casedb/services/case/crud_case_type_set_member.py`
- `gen_epix/casedb/services/case/crud_col.py`
- `gen_epix/casedb/services/case/crud_col_set.py`
- `gen_epix/casedb/services/case/crud_col_set_member.py`
- `gen_epix/casedb/services/case/crud_common.py`
- `gen_epix/casedb/services/case/crud_ref_dim.py`

## Audit Trail

- EXTRACTED: 350 (78%)
- INFERRED: 98 (22%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*