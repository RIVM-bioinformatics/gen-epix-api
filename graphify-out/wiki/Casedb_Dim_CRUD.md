# Casedb Dim CRUD

> 31 nodes · cohesion 0.11

## Key Concepts

- **DimLike** (27 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **_set_dim_occurrence()** (16 connections) — `gen_epix/casedb/services/case/crud_dim.py`
- **TestSetDimOccurrence** (15 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **TestAdminUpdate** (5 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **.test_different_case_types_not_included_in_calculation()** (4 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **.test_different_ref_dims_not_included_in_calculation()** (4 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **.test_existing_dims_with_gaps_assigns_max_plus_one()** (4 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **.test_multiple_existing_dims_assigns_max_plus_one()** (4 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **.test_new_dims_with_existing_dims_get_correct_sequence()** (4 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **.test_no_existing_dims_assigns_occurrence_1()** (4 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **.test_one_existing_dim_assigns_occurrence_2()** (4 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **.test_three_new_dims_same_batch_get_sequential_occurrences()** (4 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **.test_two_new_dims_deterministic_regardless_of_initial_values()** (4 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **.test_two_new_dims_deterministic_regardless_of_processing_order()** (4 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **.test_two_new_dims_same_batch_get_sequential_occurrences()** (4 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **.test_update_ref_dim_id_changes_raises()** (3 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **.test_update_time_stats_exclusivity_unsets_others()** (3 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **Assign a deterministic occurrence value to a Dim. The occurrence must be…** (1 connections) — `gen_epix/casedb/services/case/crud_dim.py`
- **Lightweight object mimicking Dim for testing side effects.** (1 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **Unit tests for _set_dim_occurrence function. Tests ensure deterministic, order-…** (1 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **When no existing dimensions exist, first new dim gets occurrence 1.** (1 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **When one persisted dimension exists, next dim gets occurrence 2.** (1 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **When multiple persisted dims exist, next dim gets max + 1.** (1 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **When persisted dims have gaps (e.g., 1 and 3), next dim gets max + 1. This is…** (1 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- **Two new dims in same batch with same (case_type_id, ref_dim_id) get sequential…** (1 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`
- *... and 6 more nodes in this community*

## Relationships

- [Dim CRUD Service Tests](Dim_CRUD_Service_Tests.md) (15 shared connections)
- [Dim Batch Creation Tests](Dim_Batch_Creation_Tests.md) (4 shared connections)
- [Dim Grouping Utility Tests](Dim_Grouping_Utility_Tests.md) (4 shared connections)
- [Dim CRUD Command](Dim_CRUD_Command.md) (2 shared connections)

## Source Files

- `gen_epix/casedb/services/case/crud_dim.py`
- `test/casedb/unit/services/case/crud/test_casedb_crud_dim.py`

## Audit Trail

- EXTRACTED: 76 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*