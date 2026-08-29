# Omopdb Integration Update Tests

> 8 nodes

## Key Concepts

- **TestUpdate** (9 connections) — `test/omopdb/integration/build_db/update.py`
- **Env** (4 connections)
- **.test_update_data_collection_raise()** (3 connections) — `test/omopdb/integration/build_db/update.py`
- **.test_update_data_collection()** (2 connections) — `test/omopdb/integration/build_db/update.py`
- **.test_update_user()** (2 connections) — `test/omopdb/integration/build_db/update.py`
- **.test_update_user_role()** (2 connections) — `test/omopdb/integration/build_db/update.py`
- **scenario_ids** (1 connections)
- **skipif** (1 connections)

## Relationships

- [commondb/domain/enum.py](commondb-domain-enum.py.md) (2 shared connections)
- [TestClient](TestClient.md) (1 shared connections)
- [Role](Role.md) (1 shared connections)

## Source Files

- `test/omopdb/integration/build_db/update.py`

## Audit Trail

- EXTRACTED: 12 (86%)
- INFERRED: 2 (14%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*