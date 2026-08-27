# Dim CRUD Command

> 21 nodes · cohesion 0.24

## Key Concepts

- **crud_dim.py** (30 connections) — `gen_epix/casedb/services/case/crud_dim.py`
- **_crud_create_dim()** (16 connections) — `gen_epix/casedb/services/case/crud_dim.py`
- **DimCrudCommand** (15 connections) — `gen_epix/casedb/domain/command/case.py`
- **_crud_dim_with_abac()** (12 connections) — `gen_epix/casedb/services/case/crud_dim.py`
- **_crud_dim_without_abac()** (11 connections) — `gen_epix/casedb/services/case/crud_dim.py`
- **Dim** (11 connections)
- **_crud_update_dim()** (10 connections) — `gen_epix/casedb/services/case/crud_dim.py`
- **BaseCaseService** (9 connections)
- **_verify_one_case_date_dim()** (9 connections) — `gen_epix/casedb/services/case/crud_dim.py`
- **_get_existing_dim()** (7 connections) — `gen_epix/casedb/services/case/crud_dim.py`
- **_load_existing_dims()** (7 connections) — `gen_epix/casedb/services/case/crud_dim.py`
- **_validate_case_date_dim()** (7 connections) — `gen_epix/casedb/services/case/crud_dim.py`
- **UUID** (5 connections)
- **Manage dimensions that group case-type columns (e.g., demographics, sample,…** (1 connections) — `gen_epix/casedb/domain/command/case.py`
- **Method to ensure only one case_date_dim per CaseType. If another is found, set…** (1 connections) — `gen_epix/casedb/services/case/crud_dim.py`
- **# TODO: Remove method _set_dim_occurrence and refactor/remove the corresponding…** (1 connections) — `gen_epix/casedb/services/case/crud_dim.py`
- **Apply validation logic for Dim updates: - Check if the linked RefDim may not be…** (1 connections) — `gen_epix/casedb/services/case/crud_dim.py`
- **# TODO: Implement is_geo_dim field in Dim** (1 connections) — `gen_epix/casedb/services/case/crud_dim.py`
- **Dim user command handling, ABAC applied.** (1 connections) — `gen_epix/casedb/services/case/crud_dim.py`
- **Dim admin command handling, no ABAC applied.** (1 connections) — `gen_epix/casedb/services/case/crud_dim.py`
- **Apply validation logic for Dim creation: - Check if other Dims for the same…** (1 connections) — `gen_epix/casedb/services/case/crud_dim.py`

## Relationships

- [Casedb Case CRUD Commands](Casedb_Case_CRUD_Commands.md) (31 shared connections)
- [Dim CRUD Service Tests](Dim_CRUD_Service_Tests.md) (8 shared connections)
- [Casedb Domain CRUD Commands](Casedb_Domain_CRUD_Commands.md) (4 shared connections)
- [Dim Grouping Utility Tests](Dim_Grouping_Utility_Tests.md) (4 shared connections)
- [Dim Batch Creation Tests](Dim_Batch_Creation_Tests.md) (3 shared connections)
- [Casedb Dim CRUD](Casedb_Dim_CRUD.md) (2 shared connections)
- [Case Service CRUD](Case_Service_CRUD.md) (1 shared connections)
- [Dim CRUD](Dim_CRUD.md) (1 shared connections)
- [Casedb CaseSet CRUD & Tests](Casedb_CaseSet_CRUD_&_Tests.md) (1 shared connections)
- [Case Domain Enums](Case_Domain_Enums.md) (1 shared connections)
- [Case Data Serialization](Case_Data_Serialization.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/domain/command/case.py`
- `gen_epix/casedb/services/case/crud_dim.py`

## Audit Trail

- EXTRACTED: 99 (93%)
- INFERRED: 8 (7%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*