# Commondb SQLAlchemy Mapper

> 41 nodes · cohesion 0.06

## Key Concepts

- **sa/repository.py** (52 connections) — `gen_epix/fastapp/repositories/sa/repository.py`
- **sa/__init__.py** (16 connections) — `gen_epix/fastapp/repositories/sa/__init__.py`
- **mapper.py** (15 connections) — `gen_epix/fastapp/repositories/sa/mapper.py`
- **sa_mapper.py** (13 connections) — `gen_epix/commondb/repositories/sa_mapper.py`
- **BaseSAMapperFactory** (10 connections) — `gen_epix/fastapp/repositories/sa/mapper.py`
- **CommondbSAMapper** (8 connections) — `gen_epix/commondb/repositories/sa_mapper.py`
- **CommondbSAMapperFactory** (8 connections) — `gen_epix/commondb/repositories/sa_mapper.py`
- **.create_unique_values_temp_table()** (7 connections) — `gen_epix/fastapp/repositories/sa/repository.py`
- **.dump()** (5 connections) — `gen_epix/commondb/repositories/sa_mapper.py`
- **.update()** (5 connections) — `gen_epix/commondb/repositories/sa_mapper.py`
- **SAMapperFactory** (5 connections) — `gen_epix/fastapp/repositories/sa/mapper.py`
- **.create_mapper()** (4 connections) — `gen_epix/commondb/repositories/sa_mapper.py`
- **Model** (3 connections)
- **.create_mapper()** (3 connections) — `gen_epix/fastapp/repositories/sa/mapper.py`
- **Any** (2 connections)
- **Hashable** (2 connections)
- **UUID** (2 connections)
- **Map commondb domain models to SQLAlchemy rows with protected audit metadata.** (1 connections) — `gen_epix/commondb/repositories/sa_mapper.py`
- **Encapsulates creation of commondb SQLAlchemy mappers for audit-metadata-enabled…** (1 connections) — `gen_epix/commondb/repositories/sa_mapper.py`
- **Create a mapper that enforces commondb audit metadata behavior. Args:…** (1 connections) — `gen_epix/commondb/repositories/sa_mapper.py`
- **Encapsulates a SAMapper subclass for all databases that use RowMetadataMixin.…** (1 connections) — `gen_epix/commondb/repositories/sa_mapper.py`
- **Update a SQLAlchemy row from a domain model using commondb metadata rules.…** (1 connections) — `gen_epix/commondb/repositories/sa_mapper.py`
- **Dump a domain model while hiding protected audit metadata. For users without…** (1 connections) — `gen_epix/commondb/repositories/sa_mapper.py`
- **# TODO: this should not happen here, but in the service layer. The service…** (1 connections) — `gen_epix/commondb/repositories/sa_mapper.py`
- **SQLAlchemy repository, mapper, and unit-of-work exports.** (1 connections) — `gen_epix/fastapp/repositories/sa/__init__.py`
- *... and 16 more nodes in this community*

## Relationships

- [SQLAlchemy Model Mapper](SQLAlchemy_Model_Mapper.md) (11 shared connections)
- [Database Session Isolation](Database_Session_Isolation.md) (7 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (6 shared connections)
- [SQLAlchemy Repository Queries](SQLAlchemy_Repository_Queries.md) (6 shared connections)
- [Field Type Metadata](Field_Type_Metadata.md) (5 shared connections)
- [SQLAlchemy Schema Migrations](SQLAlchemy_Schema_Migrations.md) (5 shared connections)
- [Domain Registry & ABAC Policies](Domain_Registry_&_ABAC_Policies.md) (4 shared connections)
- [SQLAlchemy Case Repository](SQLAlchemy_Case_Repository.md) (4 shared connections)
- [System & ABAC Repositories](System_&_ABAC_Repositories.md) (3 shared connections)
- [Range Filters](Range_Filters.md) (3 shared connections)
- [FastAPI App Composition](FastAPI_App_Composition.md) (2 shared connections)
- [Command Exception Handling](Command_Exception_Handling.md) (2 shared connections)

## Source Files

- `gen_epix/commondb/repositories/sa_mapper.py`
- `gen_epix/fastapp/repositories/sa/__init__.py`
- `gen_epix/fastapp/repositories/sa/mapper.py`
- `gen_epix/fastapp/repositories/sa/repository.py`

## Audit Trail

- EXTRACTED: 129 (98%)
- INFERRED: 3 (2%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*