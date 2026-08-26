# Dim CRUD Service Tests

> 24 nodes · cohesion 0.15

## Key Concepts

- **case_service_crud_dim()** (25 connections) — `gen_epix/casedb/services/case/crud_dim.py`
- **test_casedb_crud_dim.py** (23 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **BaseDimTestCase** (12 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **scenario_ids** (7 connections)
- **TestAdminCreate** (7 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **TestAbacReadAndWrite** (6 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **RefDimLike** (5 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **.test_create_sets_occurrence_and_returns_service_crud()** (5 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **TestPreconditions** (5 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **.test_create_case_date_with_non_time_dim_raises()** (4 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **.test_create_sets_occurrence_max_plus_one_and_unsets_other_case_date()** (4 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **UUID** (3 connections)
- **.__init__()** (3 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **.test_create_case_date_with_missing_dim_raises()** (3 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **.expectRepoCalled()** (2 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **.__init__()** (2 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **.test_abac_non_read_operation_raises_assertion()** (2 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **.test_abac_none_policy_returns_service_crud()** (2 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **.test_abac_read_filters_by_access()** (2 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **.test_missing_user_id_raises()** (2 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **.test_missing_user_raises()** (2 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **Handle CRUD operations for Dim entities.** (1 connections) — `gen_epix/casedb/services/case/crud_dim.py`
- **.setup_method()** (1 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **Unit tests for CaseType dimension CRUD service. Tests follow the structure and…** (1 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`

## Relationships

- [Casedb Dim CRUD](Casedb_Dim_CRUD.md) (15 shared connections)
- [Dim CRUD Command](Dim_CRUD_Command.md) (8 shared connections)
- [Casedb Case CRUD Commands](Casedb_Case_CRUD_Commands.md) (5 shared connections)
- [Casedb CaseSet CRUD & Tests](Casedb_CaseSet_CRUD_&_Tests.md) (5 shared connections)
- [Dim Grouping Utility Tests](Dim_Grouping_Utility_Tests.md) (4 shared connections)
- [Dim Batch Creation Tests](Dim_Batch_Creation_Tests.md) (4 shared connections)
- [Case Domain Enums](Case_Domain_Enums.md) (2 shared connections)
- [Dim CRUD](Dim_CRUD.md) (1 shared connections)
- [Case Data Serialization](Case_Data_Serialization.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/services/case/crud_dim.py`
- `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`

## Audit Trail

- EXTRACTED: 86 (99%)
- INFERRED: 1 (1%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*