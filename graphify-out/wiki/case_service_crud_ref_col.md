# case_service_crud_ref_col

> 29 nodes · cohesion 0.11

## Key Concepts

- **case_service_crud_ref_col()** (19 connections) — `gen_epix/casedb/services/case/crud_ref_col.py`
- **test_casedb_crud_ref_col.py** (15 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_ref_col.py`
- **TestRefColCreateAndUpdate** (8 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_ref_col.py`
- **.create_ref_col()** (7 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_ref_col.py`
- **TestRefColReadAndDelete** (7 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_ref_col.py`
- **BaseRefColTestCase** (5 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_ref_col.py`
- **TestRefColStateValidation** (5 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_ref_col.py`
- **.test_update_immutable_field_raises()** (4 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_ref_col.py`
- **parametrize** (3 connections)
- **.test_create_with_matching_dimension_type_returns_crud_result()** (3 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_ref_col.py`
- **.test_create_with_mismatched_dimension_type_raises()** (3 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_ref_col.py`
- **.test_required_linked_id_is_enforced()** (3 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_ref_col.py`
- **.test_schema_type_requires_one_schema_source()** (3 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_ref_col.py`
- **UUID** (2 connections)
- **scenario_ids** (2 connections)
- **UUID** (2 connections)
- **.test_exists_operation_returns_crud_result()** (2 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_ref_col.py`
- **.test_delete_returns_crud_result()** (2 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_ref_col.py`
- **.test_read_with_restricted_policy_uses_access_filter()** (2 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_ref_col.py`
- **.test_read_without_policy_returns_crud_result()** (2 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_ref_col.py`
- **BaseCaseService** (1 connections)
- **RefCol** (1 connections)
- **Handle CRUD operations for RefCol entities.** (1 connections) — `gen_epix/casedb/services/case/crud_ref_col.py`
- **RefCol** (1 connections)
- **Unit tests for RefCol CRUD service behavior and model state validation.** (1 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_ref_col.py`
- *... and 4 more nodes in this community*

## Relationships

- [BaseCaseService](BaseCaseService.md) (6 shared connections)
- [DatetimeRangeFilter](DatetimeRangeFilter.md) (3 shared connections)
- [_crud_cascade_delete](_crud_cascade_delete.md) (2 shared connections)
- [CrudOperation](CrudOperation.md) (2 shared connections)
- [BaseCrudTestCase](BaseCrudTestCase.md) (2 shared connections)
- [CaseService](CaseService.md) (1 shared connections)
- [TestcasedbEdgeCasesRefDataAccess](TestcasedbEdgeCasesRefDataAccess.md) (1 shared connections)
- [commondb/domain/enum.py](commondb-domain-enum.py.md) (1 shared connections)
- [casedb/domain/enum.py](casedb-domain-enum.py.md) (1 shared connections)
- [casedb/domain/model/__init__.py](casedb-domain-model-__init__.py.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/services/case/crud_ref_col.py`
- `test/casedb/unit/services/case/crud/test_casedb_crud_ref_col.py`

## Audit Trail

- EXTRACTED: 63 (98%)
- INFERRED: 1 (2%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*