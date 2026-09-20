# Reference Column CRUD

> 35 nodes · cohesion 0.09

## Key Concepts

- **case_service_crud_ref_col()** (20 connections) — `gen_epix/casedb/services/case/crud_ref_col.py`
- **crud_ref_col.py** (14 connections) — `gen_epix/casedb/services/case/crud_ref_col.py`
- **.create_ref_col()** (11 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_ref_col.py`
- **TestRefColCreateAndUpdate** (11 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_ref_col.py`
- **RefColCrudCommand** (10 connections) — `gen_epix/casedb/domain/command/case.py`
- **TestRefColReadAndDelete** (7 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_ref_col.py`
- **_verify_ref_col_concept_set_type_and_unit()** (6 connections) — `gen_epix/casedb/services/case/crud_ref_col.py`
- **TestRefColStateValidation** (5 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_ref_col.py`
- **.test_update_immutable_field_raises()** (4 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_ref_col.py`
- **parametrize** (3 connections)
- **.test_create_with_matching_concept_set_type_and_unit_returns_crud_result()** (3 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_ref_col.py`
- **.test_create_with_matching_dimension_type_returns_crud_result()** (3 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_ref_col.py`
- **.test_create_with_mismatched_concept_set_type_raises()** (3 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_ref_col.py`
- **.test_create_with_mismatched_concept_set_unit_raises()** (3 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_ref_col.py`
- **.test_create_with_mismatched_dimension_type_raises()** (3 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_ref_col.py`
- **.test_required_linked_id_is_enforced()** (3 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_ref_col.py`
- **.test_schema_type_requires_one_schema_source()** (3 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_ref_col.py`
- **RefCol** (2 connections)
- **UUID** (2 connections)
- **scenario_ids** (2 connections)
- **UUID** (2 connections)
- **.test_exists_operation_returns_crud_result()** (2 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_ref_col.py`
- **.test_delete_returns_crud_result()** (2 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_ref_col.py`
- **.test_read_with_restricted_policy_uses_access_filter()** (2 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_ref_col.py`
- **.test_read_without_policy_returns_crud_result()** (2 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_ref_col.py`
- *... and 10 more nodes in this community*

## Relationships

- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (13 shared connections)
- [Case Type & Column Commands](Case_Type_&_Column_Commands.md) (7 shared connections)
- [Column & Dimension Enums](Column_&_Dimension_Enums.md) (3 shared connections)
- [CRUD Test Base](CRUD_Test_Base.md) (3 shared connections)
- [Case Type Access Tests](Case_Type_Access_Tests.md) (1 shared connections)
- [Base Case Service Interface](Base_Case_Service_Interface.md) (1 shared connections)
- [Case Service Implementation](Case_Service_Implementation.md) (1 shared connections)
- [Geographic Region Commands](Geographic_Region_Commands.md) (1 shared connections)
- [Sequence File Creation](Sequence_File_Creation.md) (1 shared connections)
- [Case CRUD Service Operations](Case_CRUD_Service_Operations.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/domain/command/case.py`
- `gen_epix/casedb/services/case/crud_ref_col.py`
- `test/casedb/unit/services/case/crud/test_casedb_crud_ref_col.py`

## Audit Trail

- EXTRACTED: 83 (98%)
- INFERRED: 2 (2%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*