# Organization/User Read RBAC Tests

> 8 nodes · cohesion 0.39

## Key Concepts

- **TestRead** (8 connections) — `test/seqdb/integration/build_db/read.py`
- **Env** (4 connections)
- **.test_read_organization_admin_emails_raise()** (3 connections) — `test/seqdb/integration/build_db/read.py`
- **.test_read_user_raise()** (3 connections) — `test/seqdb/integration/build_db/read.py`
- **skipif** (2 connections)
- **.test_read_organization_admin_emails()** (2 connections) — `test/seqdb/integration/build_db/read.py`
- **.test_read_user()** (2 connections) — `test/seqdb/integration/build_db/read.py`
- **scenario_ids** (1 connections)

## Relationships

- [Commondb Enums & Demo Data](Commondb_Enums_&_Demo_Data.md) (2 shared connections)
- [Integration Test Client Helpers](Integration_Test_Client_Helpers.md) (1 shared connections)

## Source Files

- `test/seqdb/integration/build_db/read.py`

## Audit Trail

- EXTRACTED: 13 (93%)
- INFERRED: 1 (7%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*