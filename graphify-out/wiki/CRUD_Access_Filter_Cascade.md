# CRUD Access Filter Cascade

> 24 nodes · cohesion 0.16

## Key Concepts

- **DummyCmd** (15 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_common.py`
- **TestCrudWithAccessFilter** (15 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_common.py`
- **DummyEntity** (7 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_common.py`
- **DummyLink** (7 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_common.py`
- **.test_no_access_filter_provided_keeps_original()** (5 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_common.py`
- **.test_sets_filter_when_original_is_none()** (5 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_common.py`
- **.__init__()** (4 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_common.py`
- **.test_cascade_with_base_class_mapping_populates_subclass()** (4 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_common.py`
- **.test_cascade_with_matching_link_and_none_obj_ids()** (4 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_common.py`
- **.test_cascade_with_matching_link_and_obj_ids_uses_compose_filter()** (4 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_common.py`
- **.test_cascade_with_non_matching_links_does_nothing()** (4 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_common.py`
- **.test_delete_all_skips_cascade()** (4 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_common.py`
- **.test_sets_composite_filter_and_restores_original()** (4 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_common.py`
- **UUID** (3 connections)
- **side_effect()** (3 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_common.py`
- **.get_obj_ids()** (2 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_common.py`
- **.test_cascade_not_invoked_when_not_delete()** (2 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_common.py`
- **.test_cascade_with_unknown_model_sets_empty_mapping()** (2 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_common.py`
- **.__init__()** (1 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_common.py`
- **.__init__()** (1 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_common.py`
- **Minimal dummy command object for testing purposes.** (1 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_common.py`
- **Tests for crud_with_access_filter including cascade delete behavior.** (1 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_common.py`
- **side_effect()** (1 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_common.py`
- **side_effect()** (1 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_common.py`

## Relationships

- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (6 shared connections)
- [Database Session Isolation](Database_Session_Isolation.md) (3 shared connections)
- [Command Category & ABAC Tests](Command_Category_&_ABAC_Tests.md) (2 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (1 shared connections)
- [Row Filter Matching](Row_Filter_Matching.md) (1 shared connections)
- [CRUD Test Base](CRUD_Test_Base.md) (1 shared connections)

## Source Files

- `test/casedb/unit/services/case/crud/test_casedb_crud_common.py`

## Audit Trail

- EXTRACTED: 53 (93%)
- INFERRED: 4 (7%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*