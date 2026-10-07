# Database Session Isolation

> 63 nodes · cohesion 0.05

## Key Concepts

- **test_fastapp_sa_repository.py** (50 connections) — `test/fastapp/unit/repositories/sa/test_fastapp_sa_repository.py`
- **SAUnitOfWork** (32 connections) — `gen_epix/fastapp/repositories/sa/unit_of_work.py`
- **EqualsStringFilter** (14 connections) — `gen_epix/filter/equals_string.py`
- **_make_obj()** (12 connections) — `test/fastapp/unit/repositories/sa/test_fastapp_sa_repository.py`
- **IsolationLevel** (10 connections) — `gen_epix/fastapp/enum.py`
- **EqualsNumberFilter** (10 connections) — `gen_epix/filter/equals_number.py`
- **EqualsFilter** (9 connections) — `test/filter/unit/test_filter_base_filter.py`
- **.__exit__()** (7 connections) — `gen_epix/fastapp/repositories/sa/unit_of_work.py`
- **.default_isolation_level()** (5 connections) — `gen_epix/fastapp/repositories/sa/repository.py`
- **.test_connection()** (5 connections) — `gen_epix/fastapp/repositories/sa/repository.py`
- **._handle_exception()** (5 connections) — `gen_epix/fastapp/repositories/sa/unit_of_work.py`
- **test_read_fields()** (5 connections) — `test/fastapp/unit/repositories/sa/test_fastapp_sa_repository.py`
- **test_split_filter_and_get_where_clause()** (5 connections) — `test/fastapp/unit/repositories/sa/test_fastapp_sa_repository.py`
- **.__init__()** (4 connections) — `gen_epix/fastapp/repositories/sa/unit_of_work.py`
- **repo()** (4 connections) — `test/fastapp/unit/repositories/sa/test_fastapp_sa_repository.py`
- **RepoModel** (4 connections) — `test/fastapp/unit/repositories/sa/test_fastapp_sa_repository.py`
- **test_create_read_update_upsert_delete_and_exists()** (4 connections) — `test/fastapp/unit/repositories/sa/test_fastapp_sa_repository.py`
- **test_crud_return_ids_pagination_and_object_filter()** (4 connections) — `test/fastapp/unit/repositories/sa/test_fastapp_sa_repository.py`
- **test_print_db_content()** (4 connections) — `test/fastapp/unit/repositories/sa/test_fastapp_sa_repository.py`
- **test_read_all_applies_zero_range_bound()** (4 connections) — `test/fastapp/unit/repositories/sa/test_fastapp_sa_repository.py`
- **test_verify_valid_ids()** (4 connections) — `test/fastapp/unit/repositories/sa/test_fastapp_sa_repository.py`
- **.commit()** (3 connections) — `gen_epix/fastapp/repositories/sa/unit_of_work.py`
- **.rollback()** (3 connections) — `gen_epix/fastapp/repositories/sa/unit_of_work.py`
- **.session()** (3 connections) — `gen_epix/fastapp/repositories/sa/unit_of_work.py`
- **OtherModel** (3 connections) — `test/fastapp/unit/repositories/sa/test_fastapp_sa_repository.py`
- *... and 38 more nodes in this community*

## Relationships

- [SQLAlchemy Repository Queries](SQLAlchemy_Repository_Queries.md) (29 shared connections)
- [SQLAlchemy Case Repository](SQLAlchemy_Case_Repository.md) (11 shared connections)
- [SQLAlchemy Engine Factory](SQLAlchemy_Engine_Factory.md) (9 shared connections)
- [Commondb SQLAlchemy Mapper](Commondb_SQLAlchemy_Mapper.md) (7 shared connections)
- [Filter Base Abstractions](Filter_Base_Abstractions.md) (6 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (5 shared connections)
- [In-Memory Dict Repository](In-Memory_Dict_Repository.md) (3 shared connections)
- [CRUD Access Filter Cascade](CRUD_Access_Filter_Cascade.md) (3 shared connections)
- [Domain & Entity Registry](Domain_&_Entity_Registry.md) (3 shared connections)
- [SQLAlchemy Model Mapper](SQLAlchemy_Model_Mapper.md) (3 shared connections)
- [Filter Test Base](Filter_Test_Base.md) (3 shared connections)
- [SQL Injection Tests](SQL_Injection_Tests.md) (2 shared connections)

## Source Files

- `gen_epix/fastapp/enum.py`
- `gen_epix/fastapp/repositories/dict/unit_of_work.py`
- `gen_epix/fastapp/repositories/sa/repository.py`
- `gen_epix/fastapp/repositories/sa/unit_of_work.py`
- `gen_epix/fastapp/unit_of_work.py`
- `gen_epix/filter/equals_number.py`
- `gen_epix/filter/equals_string.py`
- `test/fastapp/unit/repositories/sa/test_fastapp_sa_repository.py`
- `test/filter/unit/test_filter_base_filter.py`

## Audit Trail

- EXTRACTED: 163 (85%)
- INFERRED: 29 (15%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*