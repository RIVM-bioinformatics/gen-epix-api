# SQLAlchemy Schema Migrations

> 52 nodes · cohesion 0.06

## Key Concepts

- **sa/util.py** (22 connections) — `gen_epix/fastapp/repositories/sa/util.py`
- **create_sa_type_from_field_info()** (12 connections) — `gen_epix/fastapp/repositories/sa/util.py`
- **get_sa_type_kwargs_from_field_info()** (8 connections) — `gen_epix/fastapp/repositories/sa/util.py`
- **ServerUtcCurrentTime** (7 connections) — `gen_epix/fastapp/repositories/sa/util.py`
- **ServerUtcTimestamp** (7 connections) — `gen_epix/fastapp/repositories/sa/util.py`
- **compiles** (6 connections)
- **SQLCompiler** (6 connections)
- **get_type_from_annotation()** (5 connections) — `gen_epix/fastapp/domain/util.py`
- **mssql_utc_current_time()** (5 connections) — `gen_epix/fastapp/repositories/sa/util.py`
- **postgresql_utc_current_time()** (5 connections) — `gen_epix/fastapp/repositories/sa/util.py`
- **postgresql_utc_timestamp()** (5 connections) — `gen_epix/fastapp/repositories/sa/util.py`
- **sqlite_utc_current_time()** (5 connections) — `gen_epix/fastapp/repositories/sa/util.py`
- **sqlite_utc_timestamp()** (5 connections) — `gen_epix/fastapp/repositories/sa/util.py`
- **UTCDateTime** (5 connections) — `gen_epix/fastapp/repositories/sa/util.py`
- **bbc386e12a58_initial_schema.py** (4 connections) — `gen_epix/casedb/repositories/sa_alembic/versions/bbc386e12a58_initial_schema.py`
- **b9c5e10bf42c_initial_schema.py** (4 connections) — `gen_epix/commondb/repositories/sa_alembic/versions/b9c5e10bf42c_initial_schema.py`
- **mssql_utc_timestamp()** (4 connections) — `gen_epix/fastapp/repositories/sa/util.py`
- **.process_result_value()** (4 connections) — `gen_epix/fastapp/repositories/sa/util.py`
- **252f23d99c89_initial_schema.py** (4 connections) — `gen_epix/omopdb/repositories/sa_alembic/versions/252f23d99c89_initial_schema.py`
- **973d81851aeb_initial_schema.py** (4 connections) — `gen_epix/seqdb/repositories/sa_alembic/versions/973d81851aeb_initial_schema.py`
- **Any** (3 connections)
- **ComputedFieldInfo** (2 connections)
- **_create_schemas()** (2 connections) — `gen_epix/casedb/repositories/sa_alembic/versions/bbc386e12a58_initial_schema.py`
- **upgrade()** (2 connections) — `gen_epix/casedb/repositories/sa_alembic/versions/bbc386e12a58_initial_schema.py`
- **_create_schemas()** (2 connections) — `gen_epix/commondb/repositories/sa_alembic/versions/b9c5e10bf42c_initial_schema.py`
- *... and 27 more nodes in this community*

## Relationships

- [Casedb ABAC SQL Models](Casedb_ABAC_SQL_Models.md) (6 shared connections)
- [Commondb SQLAlchemy Mapper](Commondb_SQLAlchemy_Mapper.md) (5 shared connections)
- [In-Memory Dict Repository](In-Memory_Dict_Repository.md) (3 shared connections)
- [Domain Registry & ABAC Policies](Domain_Registry_&_ABAC_Policies.md) (2 shared connections)
- [Transform Enums & Intervals](Transform_Enums_&_Intervals.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/repositories/sa_alembic/versions/bbc386e12a58_initial_schema.py`
- `gen_epix/commondb/repositories/sa_alembic/versions/b9c5e10bf42c_initial_schema.py`
- `gen_epix/fastapp/domain/util.py`
- `gen_epix/fastapp/repositories/sa/util.py`
- `gen_epix/omopdb/repositories/sa_alembic/versions/252f23d99c89_initial_schema.py`
- `gen_epix/seqdb/repositories/sa_alembic/versions/973d81851aeb_initial_schema.py`

## Audit Trail

- EXTRACTED: 95 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*