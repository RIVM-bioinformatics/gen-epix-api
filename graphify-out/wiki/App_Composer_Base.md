# App Composer Base

> 16 nodes · cohesion 0.15

## Key Concepts

- **BaseAppComposer** (17 connections) — `gen_epix/commondb/base_env.py`
- **.create_repository_from_pkl()** (9 connections) — `gen_epix/fastapp/repositories/dict/repository.py`
- **.create_repository()** (6 connections) — `gen_epix/commondb/base_env.py`
- **.services()** (4 connections) — `gen_epix/commondb/base_env.py`
- **Enum** (4 connections)
- **.repositories()** (3 connections) — `gen_epix/commondb/base_env.py`
- **.app()** (2 connections) — `gen_epix/commondb/base_env.py`
- **.cfg()** (2 connections) — `gen_epix/commondb/base_env.py`
- **Any** (2 connections)
- **Dynaconf** (2 connections)
- **.idp_user_dependency()** (1 connections) — `gen_epix/commondb/base_env.py`
- **.__init__()** (1 connections) — `gen_epix/commondb/base_env.py`
- **.new_user_dependency()** (1 connections) — `gen_epix/commondb/base_env.py`
- **.registered_user_dependency()** (1 connections) — `gen_epix/commondb/base_env.py`
- **App** (1 connections)
- **Load a DictRepository from a pickle file (plain or gzip-compressed).** (1 connections) — `gen_epix/fastapp/repositories/dict/repository.py`

## Relationships

- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (4 shared connections)
- [In-Memory Dict Repository](In-Memory_Dict_Repository.md) (4 shared connections)
- [FastApp Entity & Model Core](FastApp_Entity_&_Model_Core.md) (3 shared connections)
- [Repository Association Handling](Repository_Association_Handling.md) (3 shared connections)
- [Integration Test Client Helpers](Integration_Test_Client_Helpers.md) (2 shared connections)
- [Commondb Enums & Demo Data](Commondb_Enums_&_Demo_Data.md) (1 shared connections)
- [App Composition & Startup](App_Composition_&_Startup.md) (1 shared connections)
- [Base Service Class](Base_Service_Class.md) (1 shared connections)
- [Dict Repository Loading Tests](Dict_Repository_Loading_Tests.md) (1 shared connections)
- [Repository CRUD Base](Repository_CRUD_Base.md) (1 shared connections)

## Source Files

- `gen_epix/commondb/base_env.py`
- `gen_epix/fastapp/repositories/dict/repository.py`

## Audit Trail

- EXTRACTED: 36 (92%)
- INFERRED: 3 (8%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*