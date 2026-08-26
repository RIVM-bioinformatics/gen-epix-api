# User Anonymization/Update Tests

> 10 nodes · cohesion 0.29

## Key Concepts

- **TestUpdate** (10 connections) — `test/commondb/integration/build_db/update.py`
- **Env** (5 connections)
- **.test_anonymize_user()** (3 connections) — `test/commondb/integration/build_db/update.py`
- **.test_update_data_collection_raise()** (3 connections) — `test/commondb/integration/build_db/update.py`
- **.test_update_data_collection()** (2 connections) — `test/commondb/integration/build_db/update.py`
- **.test_update_user()** (2 connections) — `test/commondb/integration/build_db/update.py`
- **.test_update_user_role()** (2 connections) — `test/commondb/integration/build_db/update.py`
- **scenario_ids** (1 connections)
- **skipif** (1 connections)
- **Anonymize and deactivate a user's personal information.** (1 connections) — `test/commondb/integration/build_db/update.py`

## Relationships

- [Commondb Enums & Demo Data](Commondb_Enums_&_Demo_Data.md) (2 shared connections)
- [Integration Test Client Helpers](Integration_Test_Client_Helpers.md) (1 shared connections)
- [Read User Policy Tests](Read_User_Policy_Tests.md) (1 shared connections)

## Source Files

- `test/commondb/integration/build_db/update.py`

## Audit Trail

- EXTRACTED: 15 (88%)
- INFERRED: 2 (12%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*