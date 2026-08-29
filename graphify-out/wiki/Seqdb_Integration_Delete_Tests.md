# Seqdb Integration Delete Tests

> 9 nodes

## Key Concepts

- **TestDelete** (8 connections) — `test/seqdb/integration/build_db/delete.py`
- **Env** (4 connections)
- **.test_delete_organization_raise()** (3 connections) — `test/seqdb/integration/build_db/delete.py`
- **.test_delete_user()** (3 connections) — `test/seqdb/integration/build_db/delete.py`
- **.test_delete_user_raise()** (3 connections) — `test/seqdb/integration/build_db/delete.py`
- **.test_delete_organization()** (2 connections) — `test/seqdb/integration/build_db/delete.py`
- **skipif** (2 connections)
- **scenario_ids** (1 connections)
- **RBAC permissions: - root: CRUD - app_admin: R - refdata_admin: R - org_admin: R…** (1 connections) — `test/seqdb/integration/build_db/delete.py`

## Relationships

- [commondb/domain/enum.py](commondb-domain-enum.py.md) (2 shared connections)
- [TestClient](TestClient.md) (1 shared connections)

## Source Files

- `test/seqdb/integration/build_db/delete.py`

## Audit Trail

- EXTRACTED: 14 (93%)
- INFERRED: 1 (7%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*