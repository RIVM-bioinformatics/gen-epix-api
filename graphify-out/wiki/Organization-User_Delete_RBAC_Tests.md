# Organization/User Delete RBAC Tests

> 9 nodes · cohesion 0.33

## Key Concepts

- **TestDelete** (8 connections) — `test/commondb/integration/build_db/delete.py`
- **Env** (4 connections)
- **.test_delete_organization_raise()** (3 connections) — `test/commondb/integration/build_db/delete.py`
- **.test_delete_user()** (3 connections) — `test/commondb/integration/build_db/delete.py`
- **.test_delete_user_raise()** (3 connections) — `test/commondb/integration/build_db/delete.py`
- **skipif** (2 connections)
- **.test_delete_organization()** (2 connections) — `test/commondb/integration/build_db/delete.py`
- **scenario_ids** (1 connections)
- **RBAC permissions: - root: CRUD - app_admin: R - refdata_admin: R - org_admin: R…** (1 connections) — `test/commondb/integration/build_db/delete.py`

## Relationships

- [Commondb Enums & Demo Data](Commondb_Enums_&_Demo_Data.md) (2 shared connections)
- [Integration Test Client Helpers](Integration_Test_Client_Helpers.md) (1 shared connections)

## Source Files

- `test/commondb/integration/build_db/delete.py`

## Audit Trail

- EXTRACTED: 14 (93%)
- INFERRED: 1 (7%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*