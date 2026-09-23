# Dimension CRUD Service

> 97 nodes · cohesion 0.04

## Key Concepts

- **crud_dim.py** (31 connections) — `gen_epix/casedb/services/case/crud_dim.py`
- **DimLike** (27 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **case_service_crud_dim()** (22 connections) — `gen_epix/casedb/services/case/crud_dim.py`
- **_set_dim_occurrence()** (16 connections) — `gen_epix/casedb/services/case/crud_dim.py`
- **DimCrudCommand** (15 connections) — `gen_epix/casedb/domain/command/case.py`
- **_crud_create_dim()** (15 connections) — `gen_epix/casedb/services/case/crud_dim.py`
- **TestSetDimOccurrence** (15 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **BaseDimTestCase** (12 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **_crud_dim_with_abac()** (11 connections) — `gen_epix/casedb/services/case/crud_dim.py`
- **_group_dims_by_key()** (11 connections) — `gen_epix/casedb/services/case/crud_dim.py`
- **Dim** (11 connections)
- **_crud_dim_without_abac()** (10 connections) — `gen_epix/casedb/services/case/crud_dim.py`
- **_crud_update_dim()** (9 connections) — `gen_epix/casedb/services/case/crud_dim.py`
- **TestGroupDimsByKey** (9 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **_verify_one_case_date_dim()** (8 connections) — `gen_epix/casedb/services/case/crud_dim.py`
- **TestCrudCreateDimBatch** (8 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **_get_existing_dim()** (7 connections) — `gen_epix/casedb/services/case/crud_dim.py`
- **_load_existing_dims()** (7 connections) — `gen_epix/casedb/services/case/crud_dim.py`
- **_validate_case_date_dim()** (7 connections) — `gen_epix/casedb/services/case/crud_dim.py`
- **scenario_ids** (7 connections)
- **TestAdminCreate** (7 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **TestAbacReadAndWrite** (6 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **.test_large_batch_matches_pre_refactor_set_dim_occurrence()** (6 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **UUID** (5 connections)
- **RefDimLike** (5 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- *... and 72 more nodes in this community*

## Relationships

- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (23 shared connections)
- [Case Type & Column Commands](Case_Type_&_Column_Commands.md) (18 shared connections)
- [SQLAlchemy Case Repository](SQLAlchemy_Case_Repository.md) (10 shared connections)
- [Case CRUD Service Operations](Case_CRUD_Service_Operations.md) (3 shared connections)
- [Base Case Service Interface](Base_Case_Service_Interface.md) (1 shared connections)
- [Case Service Implementation](Case_Service_Implementation.md) (1 shared connections)
- [Geographic Region Commands](Geographic_Region_Commands.md) (1 shared connections)
- [Sequence File Creation](Sequence_File_Creation.md) (1 shared connections)
- [CRUD Test Base](CRUD_Test_Base.md) (1 shared connections)
- [Column & Dimension Enums](Column_&_Dimension_Enums.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/domain/command/case.py`
- `gen_epix/casedb/services/case/crud_dim.py`
- `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`

## Audit Trail

- EXTRACTED: 238 (93%)
- INFERRED: 17 (7%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*