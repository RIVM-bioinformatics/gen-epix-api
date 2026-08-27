# TestSQLInjection

> 10 nodes · cohesion 0.31

## Key Concepts

- **TestSQLInjection** (7 connections) — `test/commondb/integration/sql_injection/test_commondb_sql_injection.py`
- **get_test_client()** (4 connections) — `test/commondb/integration/sql_injection/test_commondb_sql_injection.py`
- **Session** (4 connections)
- **.session()** (4 connections) — `test/commondb/integration/sql_injection/test_commondb_sql_injection.py`
- **.test_sql_injection_is_existing_user_by_key()** (4 connections) — `test/commondb/integration/sql_injection/test_commondb_sql_injection.py`
- **Env** (3 connections)
- **fixture** (2 connections)
- **.test_sql_injection_orm_where_clause()** (2 connections) — `test/commondb/integration/sql_injection/test_commondb_sql_injection.py`
- **.test_sql_injection_tautology_bypass()** (2 connections) — `test/commondb/integration/sql_injection/test_commondb_sql_injection.py`
- **scenario_ids** (1 connections)

## Relationships

- [commondb/domain/enum.py](commondb-domain-enum.py.md) (2 shared connections)
- [TestClient](TestClient.md) (2 shared connections)
- [SAUnitOfWork](SAUnitOfWork.md) (1 shared connections)

## Source Files

- `test/commondb/integration/sql_injection/test_commondb_sql_injection.py`

## Audit Trail

- EXTRACTED: 17 (89%)
- INFERRED: 2 (11%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*