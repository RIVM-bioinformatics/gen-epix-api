# Bulk ID Retrieval by Temp Table

> 16 nodes · cohesion 0.13

## Key Concepts

- **._in_session_read_some()** (8 connections) — `gen_epix/fastapp/repositories/sa/repository.py`
- **.create_unique_values_temp_table()** (7 connections) — `gen_epix/fastapp/repositories/sa/repository.py`
- **.get_session()** (7 connections) — `gen_epix/fastapp/repositories/sa/repository.py`
- **._select_with_id_join()** (7 connections) — `gen_epix/fastapp/repositories/sa/repository.py`
- **Session** (5 connections)
- **._in_session_verify_retrieved_ids()** (5 connections) — `gen_epix/fastapp/repositories/sa/repository.py`
- **UUID** (2 connections)
- **TypeEngine** (1 connections)
- **Create an SQL temp table with a single columns with unique values. This can be…** (1 connections) — `gen_epix/fastapp/repositories/sa/repository.py`
- **Build a SELECT restricted to the given ids via a temp-table JOIN. Avoids ODBC…** (1 connections) — `gen_epix/fastapp/repositories/sa/repository.py`
- **:param optimize_parameter_handling: if True, avoid parameterized query that…** (1 connections) — `gen_epix/fastapp/repositories/sa/repository.py`
- **Raise InvalidIdsError if fewer rows were returned than requested.** (1 connections) — `gen_epix/fastapp/repositories/sa/repository.py`
- **Create and return a new SA session at the given isolation level.** (1 connections) — `gen_epix/fastapp/repositories/sa/repository.py`
- **MetaData** (1 connections)
- **Select** (1 connections)
- **Table** (1 connections)

## Relationships

- [Repository Query Helpers](Repository_Query_Helpers.md) (7 shared connections)
- [FastApp SA Repository Core](FastApp_SA_Repository_Core.md) (6 shared connections)
- [SA Model Mapper](SA_Model_Mapper.md) (3 shared connections)
- [Case Domain Enums](Case_Domain_Enums.md) (1 shared connections)
- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (1 shared connections)

## Source Files

- `gen_epix/fastapp/repositories/sa/repository.py`

## Audit Trail

- EXTRACTED: 34 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*