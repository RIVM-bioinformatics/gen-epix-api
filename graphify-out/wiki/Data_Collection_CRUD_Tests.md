# Data Collection CRUD Tests

> 19 nodes · cohesion 0.11

## Key Concepts

- **TestUpdate** (11 connections) — `test/omopdb/integration/build_db/update.py`
- **TestRead** (9 connections) — `test/omopdb/integration/build_db/read.py`
- **dependency** (4 connections)
- **.test_read_organization_admin_emails_raise()** (3 connections) — `test/omopdb/integration/build_db/read.py`
- **.test_read_user_raise()** (3 connections) — `test/omopdb/integration/build_db/read.py`
- **TestCreate** (3 connections) — `test/omopdb/integration/build_db/test_omopdb_build.py`
- **TestDelete** (3 connections) — `test/omopdb/integration/build_db/test_omopdb_build.py`
- **TestRead** (3 connections) — `test/omopdb/integration/build_db/test_omopdb_build.py`
- **TestUpdate** (3 connections) — `test/omopdb/integration/build_db/test_omopdb_build.py`
- **.test_update_data_collection_raise()** (3 connections) — `test/omopdb/integration/build_db/update.py`
- **skipif** (2 connections)
- **.test_read_organization_admin_emails()** (2 connections) — `test/omopdb/integration/build_db/read.py`
- **.test_read_user()** (2 connections) — `test/omopdb/integration/build_db/read.py`
- **.test_update_data_collection()** (2 connections) — `test/omopdb/integration/build_db/update.py`
- **.test_update_user()** (2 connections) — `test/omopdb/integration/build_db/update.py`
- **.test_update_user_role()** (2 connections) — `test/omopdb/integration/build_db/update.py`
- **scenario_ids** (1 connections)
- **scenario_ids** (1 connections)
- **skipif** (1 connections)

## Relationships

- [Integration Test Client](Integration_Test_Client.md) (11 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (9 shared connections)
- [Organization Delete Tests](Organization_Delete_Tests.md) (1 shared connections)
- [Role Generation & Hierarchy](Role_Generation_&_Hierarchy.md) (1 shared connections)

## Source Files

- `test/omopdb/integration/build_db/read.py`
- `test/omopdb/integration/build_db/test_omopdb_build.py`
- `test/omopdb/integration/build_db/update.py`

## Audit Trail

- EXTRACTED: 37 (90%)
- INFERRED: 4 (10%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*