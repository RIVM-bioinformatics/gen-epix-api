# SQLAlchemy Engine Factory

> 36 nodes · cohesion 0.07

## Key Concepts

- **.create_sa_repository()** (14 connections) — `gen_epix/fastapp/repositories/sa/repository.py`
- **test_crud_dispatch()** (8 connections) — `test/fastapp/unit/repositories/sa/test_fastapp_sa_repository.py`
- **EngineFactory** (7 connections) — `gen_epix/fastapp/repositories/sa/engine_factory.py`
- **.clear_repository_content()** (7 connections) — `gen_epix/fastapp/repositories/sa/repository.py`
- **.create_repository()** (7 connections) — `gen_epix/fastapp/repositories/sa/repository.py`
- **.create_engine()** (6 connections) — `gen_epix/fastapp/repositories/sa/engine_factory.py`
- **._process_repository_params()** (6 connections) — `gen_epix/fastapp/repositories/sa/repository.py`
- **test_create_sa_repository_attached_sqlite_is_in_memory()** (6 connections) — `test/fastapp/unit/repositories/sa/test_fastapp_sa_repository.py`
- **MonkeyPatch** (5 connections)
- **test_clear_repository_content_drops_default_schema_tables()** (5 connections) — `test/fastapp/unit/repositories/sa/test_fastapp_sa_repository.py`
- **test_create_repository_delegates()** (5 connections) — `test/fastapp/unit/repositories/sa/test_fastapp_sa_repository.py`
- **test_create_sa_repository_default_sqlite_is_in_memory()** (5 connections) — `test/fastapp/unit/repositories/sa/test_fastapp_sa_repository.py`
- **test_create_sa_repository_does_not_create_non_sqlite_schema_by_default()** (5 connections) — `test/fastapp/unit/repositories/sa/test_fastapp_sa_repository.py`
- **Path** (4 connections)
- **test_create_sa_repository()** (4 connections) — `test/fastapp/unit/repositories/sa/test_fastapp_sa_repository.py`
- **test_create_sa_repository_sqlite_shared_memory_uri()** (4 connections) — `test/fastapp/unit/repositories/sa/test_fastapp_sa_repository.py`
- **engine_factory.py** (3 connections) — `gen_epix/fastapp/repositories/sa/engine_factory.py`
- **test_clear_repository_content_smoke_in_memory()** (3 connections) — `test/fastapp/unit/repositories/sa/test_fastapp_sa_repository.py`
- **._compose_key()** (2 connections) — `gen_epix/fastapp/repositories/sa/engine_factory.py`
- **.__init__()** (2 connections) — `gen_epix/fastapp/repositories/sa/engine_factory.py`
- **Engine** (1 connections)
- **Thread-safe SQLAlchemy engine factory.** (1 connections) — `gen_epix/fastapp/repositories/sa/engine_factory.py`
- **Encapsulates creation and management of SQLAlchemy engines.** (1 connections) — `gen_epix/fastapp/repositories/sa/engine_factory.py`
- **Initialize a EngineFactory instance.** (1 connections) — `gen_epix/fastapp/repositories/sa/engine_factory.py`
- **Create a new SQLAlchemy engine or return an existing one for the given…** (1 connections) — `gen_epix/fastapp/repositories/sa/engine_factory.py`
- *... and 11 more nodes in this community*

## Relationships

- [SQLAlchemy Repository Queries](SQLAlchemy_Repository_Queries.md) (19 shared connections)
- [Database Session Isolation](Database_Session_Isolation.md) (9 shared connections)
- [Domain & Entity Registry](Domain_&_Entity_Registry.md) (3 shared connections)
- [Commondb SQLAlchemy Mapper](Commondb_SQLAlchemy_Mapper.md) (2 shared connections)
- [Generic Repository Base](Generic_Repository_Base.md) (1 shared connections)
- [FastApp API Tests](FastApp_API_Tests.md) (1 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (1 shared connections)

## Source Files

- `gen_epix/fastapp/repositories/sa/engine_factory.py`
- `gen_epix/fastapp/repositories/sa/repository.py`
- `test/fastapp/unit/repositories/sa/test_fastapp_sa_repository.py`

## Audit Trail

- EXTRACTED: 66 (82%)
- INFERRED: 14 (18%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*