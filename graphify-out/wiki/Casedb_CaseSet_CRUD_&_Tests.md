# Casedb CaseSet CRUD & Tests

> 141 nodes · cohesion 0.02

## Key Concepts

- **CrudOperation** (127 connections) — `gen_epix/fastapp/enum.py`
- **mock_compat.py** (46 connections) — `test/util/mock_compat.py`
- **BaseCrudTestCase** (25 connections) — `test/casedb/unit/services/case/base.py`
- **case_service_crud_case_set()** (23 connections) — `gen_epix/casedb/services/case/crud_case_set.py`
- **test_casedb_crud_common.py** (22 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_common.py`
- **crud_case_set.py** (21 connections) — `gen_epix/casedb/services/case/crud_case_set.py`
- **case_service_crud_ref_col()** (19 connections) — `gen_epix/casedb/services/case/crud_ref_col.py`
- **unit/services/case/base.py** (18 connections) — `test/casedb/unit/services/case/base.py`
- **test_retrieve_complete_case_type.py** (18 connections) — `test/casedb/unit/services/case/retrieve_case/test_retrieve_complete_case_type.py`
- **test_casedb_crud_case_set.py** (17 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_case_set.py`
- **test_casedb_crud_ref_col.py** (15 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_ref_col.py`
- **TestCrudWithAccessFilter** (14 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_common.py`
- **DummyCmd** (13 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_common.py`
- **_crud_case_set_with_abac()** (11 connections) — `gen_epix/casedb/services/case/crud_case_set.py`
- **TestCommandCategoryChecks** (11 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_common.py`
- **CaseSetCrudCommand** (10 connections) — `gen_epix/casedb/domain/command/case.py`
- **test_organization.py** (10 connections) — `test/commondb/unit/services/test_organization.py`
- **_crud_case_set_without_abac()** (9 connections) — `gen_epix/casedb/services/case/crud_case_set.py`
- **TestRoleChecks** (9 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_common.py`
- **_validate_case_set_deletion()** (8 connections) — `gen_epix/casedb/services/case/crud_case_set.py`
- **TestRefColCreateAndUpdate** (8 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_ref_col.py`
- **scenario_ids** (7 connections)
- **TestReadOperations** (7 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_case_set.py`
- **.create_ref_col()** (7 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_ref_col.py`
- **TestRefColReadAndDelete** (7 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_ref_col.py`
- *... and 116 more nodes in this community*

## Relationships

- [Casedb Case CRUD Commands](Casedb_Case_CRUD_Commands.md) (49 shared connections)
- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (29 shared connections)
- [Commondb Enums & Demo Data](Commondb_Enums_&_Demo_Data.md) (20 shared connections)
- [Casedb ABAC & Filter Logic](Casedb_ABAC_&_Filter_Logic.md) (13 shared connections)
- [Case Domain Enums](Case_Domain_Enums.md) (11 shared connections)
- [Upload/ETL Result Model](Upload-ETL_Result_Model.md) (8 shared connections)
- [Casedb Domain CRUD Commands](Casedb_Domain_CRUD_Commands.md) (7 shared connections)
- [Casedb Domain Enums & Policy](Casedb_Domain_Enums_&_Policy.md) (7 shared connections)
- [Dim CRUD Service Tests](Dim_CRUD_Service_Tests.md) (5 shared connections)
- [Casedb Case Service](Casedb_Case_Service.md) (4 shared connections)
- [CRUD Endpoint Generation Helpers](CRUD_Endpoint_Generation_Helpers.md) (4 shared connections)
- [RBAC/ABAC Policy Implementations](RBAC-ABAC_Policy_Implementations.md) (4 shared connections)

## Source Files

- `gen_epix/casedb/domain/command/case.py`
- `gen_epix/casedb/services/case/crud_case_set.py`
- `gen_epix/casedb/services/case/crud_ref_col.py`
- `gen_epix/casedb/services/case/service.py`
- `gen_epix/fastapp/enum.py`
- `test/casedb/unit/services/case/base.py`
- `test/casedb/unit/services/case/crud/test_casedb_crud_case_set.py`
- `test/casedb/unit/services/case/crud/test_casedb_crud_common.py`
- `test/casedb/unit/services/case/crud/test_casedb_crud_ref_col.py`
- `test/casedb/unit/services/case/retrieve_case/test_retrieve_complete_case_type.py`
- `test/commondb/unit/services/test_organization.py`
- `test/util/mock_compat.py`

## Audit Trail

- EXTRACTED: 492 (99%)
- INFERRED: 7 (1%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*