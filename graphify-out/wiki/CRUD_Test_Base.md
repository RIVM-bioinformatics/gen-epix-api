# CRUD Test Base

> 38 nodes · cohesion 0.06

## Key Concepts

- **BaseCrudTestCase** (28 connections) — `test/casedb/unit/services/case/base.py`
- **scenario_ids** (7 connections)
- **.create_crud_command()** (6 connections) — `test/casedb/unit/services/case/base.py`
- **TestDeleteSomeOperation** (6 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_case_set.py`
- **TestReadOperations** (6 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_case_set.py`
- **TestAbacCreateOperation** (5 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_case_set.py`
- **TestAbacNoPolicy** (5 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_case_set.py`
- **TestAdminPath** (5 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_case_set.py`
- **TestDeleteAllOperation** (5 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_case_set.py`
- **TestUpdateOperation** (5 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_case_set.py`
- **BaseRefColTestCase** (5 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_ref_col.py`
- **._make_uow()** (4 connections) — `test/casedb/unit/services/case/base.py`
- **.create_case_abac()** (2 connections) — `test/casedb/unit/services/case/base.py`
- **.create_case_sets()** (2 connections) — `test/casedb/unit/services/case/base.py`
- **.setup_method()** (2 connections) — `test/casedb/unit/services/case/base.py`
- **UUID** (2 connections)
- **Tests for delete-all operation denial with ABAC policy.** (2 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_case_set.py`
- **.test_delete_some_allowed_calls_crud()** (2 connections) — `test/casedb/unit/services/case/crud/test_casedb_crud_case_set.py`
- **Any** (1 connections)
- **Create mocked CaseSet objects with required attributes.** (1 connections) — `test/casedb/unit/services/case/base.py`
- **Create a mocked ABAC object with configurable allowance.** (1 connections) — `test/casedb/unit/services/case/base.py`
- **Base test case providing common service and UOW fixtures for CRUD tests.…** (1 connections) — `test/casedb/unit/services/case/base.py`
- **Create a ``BaseUnitOfWork`` mock with context-manager support.** (1 connections) — `test/casedb/unit/services/case/base.py`
- **Create a mocked command with all standard attributes wired. If ``user_id`` is…** (1 connections) — `test/casedb/unit/services/case/base.py`
- **skip** (1 connections)
- *... and 13 more nodes in this community*

## Relationships

- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (14 shared connections)
- [Command Category & ABAC Tests](Command_Category_&_ABAC_Tests.md) (3 shared connections)
- [Role Generation & Hierarchy](Role_Generation_&_Hierarchy.md) (3 shared connections)
- [Reference Column CRUD](Reference_Column_CRUD.md) (3 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (2 shared connections)
- [SQLAlchemy Case Repository](SQLAlchemy_Case_Repository.md) (2 shared connections)
- [CRUD Access Filter Cascade](CRUD_Access_Filter_Cascade.md) (1 shared connections)
- [Dimension CRUD Service](Dimension_CRUD_Service.md) (1 shared connections)

## Source Files

- `test/casedb/unit/services/case/base.py`
- `test/casedb/unit/services/case/crud/test_casedb_crud_case_set.py`
- `test/casedb/unit/services/case/crud/test_casedb_crud_ref_col.py`

## Audit Trail

- EXTRACTED: 70 (95%)
- INFERRED: 4 (5%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*