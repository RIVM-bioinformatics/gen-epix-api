# Dim Batch Creation Tests

> 11 nodes · cohesion 0.24

## Key Concepts

- **TestCrudCreateDimBatch** (8 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **.test_large_batch_matches_pre_refactor_set_dim_occurrence()** (6 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **._make_cmd()** (5 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **.test_large_batch_same_key_sequential_occurrences()** (5 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **.test_two_groups_independent_occurrence_sequences()** (5 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **.expectList()** (2 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **Any** (2 connections)
- **Dims belonging to different (case_type_id, ref_dim_id) groups each get…** (1 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **Integration-style unit tests for _crud_create_dim with large batches. These…** (1 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **50 dims sharing (case_type_id, ref_dim_id) with no existing dims get…** (1 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **The new grouping approach assigns identical occurrences to what…** (1 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`

## Relationships

- [Dim CRUD Service Tests](Dim_CRUD_Service_Tests.md) (4 shared connections)
- [Casedb Dim CRUD](Casedb_Dim_CRUD.md) (4 shared connections)
- [Dim CRUD Command](Dim_CRUD_Command.md) (3 shared connections)

## Source Files

- `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`

## Audit Trail

- EXTRACTED: 24 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*