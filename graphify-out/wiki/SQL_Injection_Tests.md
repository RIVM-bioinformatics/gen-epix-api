# SQL Injection Tests

> 9 nodes · cohesion 0.31

## Key Concepts

- **TestSQLInjection** (9 connections) — `test/commondb/integration/sql_injection/test_commondb_sql_injection.py`
- **Session** (4 connections)
- **.session()** (4 connections) — `test/commondb/integration/sql_injection/test_commondb_sql_injection.py`
- **.test_sql_injection_is_existing_user_by_key()** (4 connections) — `test/commondb/integration/sql_injection/test_commondb_sql_injection.py`
- **get_test_client()** (3 connections) — `test/commondb/integration/sql_injection/test_commondb_sql_injection.py`
- **fixture** (2 connections)
- **.test_sql_injection_orm_where_clause()** (2 connections) — `test/commondb/integration/sql_injection/test_commondb_sql_injection.py`
- **.test_sql_injection_tautology_bypass()** (2 connections) — `test/commondb/integration/sql_injection/test_commondb_sql_injection.py`
- **scenario_ids** (1 connections)

## Relationships

- [Integration Test Client](Integration_Test_Client.md) (4 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (2 shared connections)
- [Database Session Isolation](Database_Session_Isolation.md) (2 shared connections)
- [Organization SQL Repository](Organization_SQL_Repository.md) (1 shared connections)

## Source Files

- `test/commondb/integration/sql_injection/test_commondb_sql_injection.py`

## Audit Trail

- EXTRACTED: 16 (80%)
- INFERRED: 4 (20%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*