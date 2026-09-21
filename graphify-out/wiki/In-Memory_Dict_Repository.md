# In-Memory Dict Repository

> 92 nodes · cohesion 0.07

## Key Concepts

- **DictRepository** (125 connections) — `gen_epix/fastapp/repositories/dict/repository.py`
- **test_fastapp_dict_repository.py** (67 connections) — `test/fastapp/unit/repositories/dict/test_fastapp_dict_repository.py`
- **scenario_ids** (41 connections)
- **UUID** (31 connections)
- **make_parent_entity()** (18 connections) — `test/fastapp/unit/repositories/dict/test_fastapp_dict_repository.py`
- **ParentModel** (18 connections) — `test/fastapp/unit/repositories/dict/test_fastapp_dict_repository.py`
- **.create_repository()** (12 connections) — `gen_epix/fastapp/repositories/dict/repository.py`
- **DictUnitOfWork** (12 connections) — `gen_epix/fastapp/repositories/dict/unit_of_work.py`
- **fastapp/repositories/__init__.py** (12 connections) — `gen_epix/fastapp/repositories/__init__.py`
- **test_create_repository_from_json_happy()** (12 connections) — `test/fastapp/unit/repositories/dict/test_fastapp_dict_repository.py`
- **make_repo()** (11 connections) — `test/fastapp/unit/repositories/dict/test_fastapp_dict_repository.py`
- **ChildModel** (10 connections) — `test/fastapp/unit/repositories/dict/test_fastapp_dict_repository.py`
- **.create_repository_from_pkl()** (9 connections) — `gen_epix/fastapp/repositories/dict/repository.py`
- **make_child_entity()** (9 connections) — `test/fastapp/unit/repositories/dict/test_fastapp_dict_repository.py`
- **pc_repo()** (9 connections) — `test/fastapp/unit/repositories/dict/test_fastapp_dict_repository.py`
- **.create_repository_from_json()** (8 connections) — `gen_epix/fastapp/repositories/dict/repository.py`
- **dict/unit_of_work.py** (7 connections) — `gen_epix/fastapp/repositories/dict/unit_of_work.py`
- **parent_repo()** (7 connections) — `test/fastapp/unit/repositories/dict/test_fastapp_dict_repository.py`
- **test_create_repository_detect_pkl_calls_from_pkl()** (7 connections) — `test/fastapp/unit/repositories/dict/test_fastapp_dict_repository.py`
- **test_create_repository_detect_zip_calls_from_json()** (7 connections) — `test/fastapp/unit/repositories/dict/test_fastapp_dict_repository.py`
- **test_create_repository_no_file_initializes_empty_db()** (7 connections) — `test/fastapp/unit/repositories/dict/test_fastapp_dict_repository.py`
- **test_delete_all_ignores_links_from_non_persistable_models()** (7 connections) — `test/fastapp/unit/repositories/dict/test_fastapp_dict_repository.py`
- **test_init_composite_id_field_raises()** (7 connections) — `test/fastapp/unit/repositories/dict/test_fastapp_dict_repository.py`
- **dict/__init__.py** (6 connections) — `gen_epix/fastapp/repositories/dict/__init__.py`
- **.uow()** (6 connections) — `gen_epix/fastapp/repositories/dict/repository.py`
- *... and 67 more nodes in this community*

## Relationships

- [Generic Repository CRUD](Generic_Repository_CRUD.md) (37 shared connections)
- [SQLAlchemy Case Repository](SQLAlchemy_Case_Repository.md) (11 shared connections)
- [Domain & Entity Registry](Domain_&_Entity_Registry.md) (10 shared connections)
- [Audit Metadata Modifiers](Audit_Metadata_Modifiers.md) (9 shared connections)
- [FastApp Test Fixtures](FastApp_Test_Fixtures.md) (7 shared connections)
- [System & ABAC Repositories](System_&_ABAC_Repositories.md) (6 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (5 shared connections)
- [Generic Repository Base](Generic_Repository_Base.md) (4 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (4 shared connections)
- [App Composer Base](App_Composer_Base.md) (3 shared connections)
- [Casedb Repository Contracts](Casedb_Repository_Contracts.md) (3 shared connections)
- [Database Session Isolation](Database_Session_Isolation.md) (3 shared connections)

## Source Files

- `gen_epix/fastapp/repositories/__init__.py`
- `gen_epix/fastapp/repositories/dict/__init__.py`
- `gen_epix/fastapp/repositories/dict/repository.py`
- `gen_epix/fastapp/repositories/dict/unit_of_work.py`
- `test/fastapp/unit/repositories/dict/test_fastapp_dict_repository.py`

## Audit Trail

- EXTRACTED: 331 (82%)
- INFERRED: 73 (18%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*