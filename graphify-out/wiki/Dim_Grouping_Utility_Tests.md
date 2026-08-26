# Dim Grouping Utility Tests

> 9 nodes · cohesion 0.33

## Key Concepts

- **_group_dims_by_key()** (11 connections) — `gen_epix/casedb/services/case/crud_dim.py`
- **TestGroupDimsByKey** (9 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **.test_different_keys_produce_separate_groups()** (3 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **.test_insertion_order_preserved_within_group()** (3 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **.test_same_key_dims_grouped_together()** (3 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **.test_single_dim_produces_one_group()** (3 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **.test_empty_list_returns_empty_dict()** (2 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **Group Dims by (case_type_id, ref_dim_id). Each group holds all Dims sharing…** (1 connections) — `gen_epix/casedb/services/case/crud_dim.py`
- **Unit tests for _group_dims_by_key.** (1 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`

## Relationships

- [Dim CRUD Command](Dim_CRUD_Command.md) (4 shared connections)
- [Dim CRUD Service Tests](Dim_CRUD_Service_Tests.md) (4 shared connections)
- [Casedb Dim CRUD](Casedb_Dim_CRUD.md) (4 shared connections)

## Source Files

- `gen_epix/casedb/services/case/crud_dim.py`
- `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`

## Audit Trail

- EXTRACTED: 24 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*