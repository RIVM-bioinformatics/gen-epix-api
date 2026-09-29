# Organization Delete Tests

> 23 nodes · cohesion 0.10

## Key Concepts

- **TestDelete** (10 connections) — `test/commondb/integration/build_db/delete.py`
- **TestDelete** (9 connections) — `test/omopdb/integration/build_db/delete.py`
- **TestDelete** (9 connections) — `test/seqdb/integration/build_db/delete.py`
- **.test_delete_organization_raise()** (3 connections) — `test/commondb/integration/build_db/delete.py`
- **.test_delete_user()** (3 connections) — `test/commondb/integration/build_db/delete.py`
- **.test_delete_user_raise()** (3 connections) — `test/commondb/integration/build_db/delete.py`
- **TestDelete** (3 connections) — `test/commondb/integration/build_db/test_commondb_build.py`
- **.test_delete_organization_raise()** (3 connections) — `test/omopdb/integration/build_db/delete.py`
- **.test_delete_user()** (3 connections) — `test/omopdb/integration/build_db/delete.py`
- **.test_delete_user_raise()** (3 connections) — `test/omopdb/integration/build_db/delete.py`
- **RBAC permissions: - root: CRUD - app_admin: R - refdata_admin: R - org_admin: R…** (3 connections) — `test/seqdb/integration/build_db/delete.py`
- **.test_delete_organization_raise()** (3 connections) — `test/seqdb/integration/build_db/delete.py`
- **.test_delete_user()** (3 connections) — `test/seqdb/integration/build_db/delete.py`
- **.test_delete_user_raise()** (3 connections) — `test/seqdb/integration/build_db/delete.py`
- **skipif** (2 connections)
- **.test_delete_organization()** (2 connections) — `test/commondb/integration/build_db/delete.py`
- **skipif** (2 connections)
- **.test_delete_organization()** (2 connections) — `test/omopdb/integration/build_db/delete.py`
- **skipif** (2 connections)
- **.test_delete_organization()** (2 connections) — `test/seqdb/integration/build_db/delete.py`
- **scenario_ids** (1 connections)
- **scenario_ids** (1 connections)
- **scenario_ids** (1 connections)

## Relationships

- [Integration Test Client](Integration_Test_Client.md) (15 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (5 shared connections)
- [Organization & ABAC Models](Organization_&_ABAC_Models.md) (3 shared connections)
- [Organization Contacts Retrieval](Organization_Contacts_Retrieval.md) (1 shared connections)
- [User Anonymization Tests](User_Anonymization_Tests.md) (1 shared connections)
- [Data Collection CRUD Tests](Data_Collection_CRUD_Tests.md) (1 shared connections)

## Source Files

- `test/commondb/integration/build_db/delete.py`
- `test/commondb/integration/build_db/test_commondb_build.py`
- `test/omopdb/integration/build_db/delete.py`
- `test/seqdb/integration/build_db/delete.py`

## Audit Trail

- EXTRACTED: 48 (94%)
- INFERRED: 3 (6%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*