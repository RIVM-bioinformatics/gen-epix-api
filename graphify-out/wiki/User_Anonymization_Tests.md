# User Anonymization Tests

> 20 nodes · cohesion 0.11

## Key Concepts

- **TestUpdate** (12 connections) — `test/commondb/integration/build_db/update.py`
- **TestRead** (9 connections) — `test/commondb/integration/build_db/read.py`
- **dependency** (4 connections)
- **.test_read_organization_admin_emails_raise()** (3 connections) — `test/commondb/integration/build_db/read.py`
- **.test_read_user_raise()** (3 connections) — `test/commondb/integration/build_db/read.py`
- **TestCreate** (3 connections) — `test/commondb/integration/build_db/test_commondb_build.py`
- **TestRead** (3 connections) — `test/commondb/integration/build_db/test_commondb_build.py`
- **TestUpdate** (3 connections) — `test/commondb/integration/build_db/test_commondb_build.py`
- **.test_anonymize_user()** (3 connections) — `test/commondb/integration/build_db/update.py`
- **.test_update_data_collection_raise()** (3 connections) — `test/commondb/integration/build_db/update.py`
- **skipif** (2 connections)
- **.test_read_organization_admin_emails()** (2 connections) — `test/commondb/integration/build_db/read.py`
- **.test_read_user()** (2 connections) — `test/commondb/integration/build_db/read.py`
- **.test_update_data_collection()** (2 connections) — `test/commondb/integration/build_db/update.py`
- **.test_update_user()** (2 connections) — `test/commondb/integration/build_db/update.py`
- **.test_update_user_role()** (2 connections) — `test/commondb/integration/build_db/update.py`
- **scenario_ids** (1 connections)
- **scenario_ids** (1 connections)
- **skipif** (1 connections)
- **Anonymize and deactivate a user's personal information.** (1 connections) — `test/commondb/integration/build_db/update.py`

## Relationships

- [Integration Test Client](Integration_Test_Client.md) (12 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (8 shared connections)
- [Organization Delete Tests](Organization_Delete_Tests.md) (1 shared connections)
- [Role Generation & Hierarchy](Role_Generation_&_Hierarchy.md) (1 shared connections)

## Source Files

- `test/commondb/integration/build_db/read.py`
- `test/commondb/integration/build_db/test_commondb_build.py`
- `test/commondb/integration/build_db/update.py`

## Audit Trail

- EXTRACTED: 38 (90%)
- INFERRED: 4 (10%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*