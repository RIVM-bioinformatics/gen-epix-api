# Dict Repository Loading Tests

> 9 nodes · cohesion 0.25

## Key Concepts

- **.create_repository()** (11 connections) — `gen_epix/fastapp/repositories/dict/repository.py`
- **.create_repository_from_json()** (9 connections) — `gen_epix/fastapp/repositories/dict/repository.py`
- **test_create_repository_detect_pkl_calls_from_pkl()** (7 connections) — `test/fastapp/unit/repositories/dict/test_fastapp_dict_repository.py`
- **test_create_repository_detect_zip_calls_from_json()** (7 connections) — `test/fastapp/unit/repositories/dict/test_fastapp_dict_repository.py`
- **._create_empty_db_for_entities()** (6 connections) — `gen_epix/fastapp/repositories/dict/repository.py`
- **MonkeyPatch** (5 connections)
- **Load a DictRepository from a zip archive containing per-entity JSON files.** (1 connections) — `gen_epix/fastapp/repositories/dict/repository.py`
- **Create an empty db map with one entry per persistable model class.** (1 connections) — `gen_epix/fastapp/repositories/dict/repository.py`
- **Instantiate a DictRepository, optionally loading data from a pkl/zip file.** (1 connections) — `gen_epix/fastapp/repositories/dict/repository.py`

## Relationships

- [In-Memory Dict Repository](In-Memory_Dict_Repository.md) (16 shared connections)
- [FastApp Entity & Model Core](FastApp_Entity_&_Model_Core.md) (5 shared connections)
- [Repository CRUD Base](Repository_CRUD_Base.md) (4 shared connections)
- [Repository Association Handling](Repository_Association_Handling.md) (2 shared connections)
- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (2 shared connections)
- [App Composer Base](App_Composer_Base.md) (1 shared connections)

## Source Files

- `gen_epix/fastapp/repositories/dict/repository.py`
- `test/fastapp/unit/repositories/dict/test_fastapp_dict_repository.py`

## Audit Trail

- EXTRACTED: 33 (85%)
- INFERRED: 6 (15%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*