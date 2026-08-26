# Repository Association Handling

> 35 nodes · cohesion 0.12

## Key Concepts

- **BaseRepository** (65 connections) — `gen_epix/fastapp/repository.py`
- **.update_association()** (13 connections) — `gen_epix/fastapp/repository.py`
- **Hashable** (13 connections)
- **Model** (12 connections)
- **.crud()** (11 connections) — `gen_epix/fastapp/repository.py`
- **.verify_crud_args()** (8 connections) — `gen_epix/fastapp/repository.py`
- **.read_fields()** (7 connections) — `gen_epix/fastapp/repository.py`
- **Any** (7 connections)
- **._delete_without_associations()** (6 connections) — `gen_epix/fastapp/repository.py`
- **._handle_association_transactions()** (6 connections) — `gen_epix/fastapp/repository.py`
- **TestRaiseOnDuplicateIds** (6 connections) — `test/fastapp/unit/test_fastapp_base_repository.py`
- **._get_obj_id_pairs()** (5 connections) — `gen_epix/fastapp/repository.py`
- **.verify_valid_ids()** (5 connections) — `gen_epix/fastapp/repository.py`
- **.create_repository()** (4 connections) — `gen_epix/fastapp/repository.py`
- **._get_relevant_existing_objs()** (4 connections) — `gen_epix/fastapp/repository.py`
- **._parse_update_association_parameters()** (4 connections) — `gen_epix/fastapp/repository.py`
- **.raise_on_duplicate_ids()** (4 connections) — `gen_epix/fastapp/repository.py`
- **._verify_any_excluded_ids_or_pairs()** (4 connections) — `gen_epix/fastapp/repository.py`
- **._verify_obj_id_pairs_uniqueness()** (4 connections) — `gen_epix/fastapp/repository.py`
- **.clear_repository_content()** (3 connections) — `gen_epix/fastapp/repository.py`
- **.split_filter()** (3 connections) — `gen_epix/fastapp/repository.py`
- **.__init__()** (2 connections) — `gen_epix/fastapp/repository.py`
- **.test_class_abstract_create_repository_raises()** (2 connections) — `test/fastapp/unit/test_fastapp_base_repository.py`
- **.test_duplicates_raise()** (2 connections) — `test/fastapp/unit/test_fastapp_base_repository.py`
- **.test_no_duplicates()** (2 connections) — `test/fastapp/unit/test_fastapp_base_repository.py`
- *... and 10 more nodes in this community*

## Relationships

- [Casedb Repository Implementations](Casedb_Repository_Implementations.md) (9 shared connections)
- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (9 shared connections)
- [Casedb Case CRUD Commands](Casedb_Case_CRUD_Commands.md) (7 shared connections)
- [Repository Test Base](Repository_Test_Base.md) (6 shared connections)
- [App Composer Base](App_Composer_Base.md) (3 shared connections)
- [Fastapp CRUD Command Tests](Fastapp_CRUD_Command_Tests.md) (3 shared connections)
- [Case Domain Enums](Case_Domain_Enums.md) (3 shared connections)
- [Geo/Ontology/Abac Repositories](Geo-Ontology-Abac_Repositories.md) (3 shared connections)
- [Query Filter Engine](Query_Filter_Engine.md) (3 shared connections)
- [Dict Repository Loading Tests](Dict_Repository_Loading_Tests.md) (2 shared connections)
- [Service Test Client Fixtures](Service_Test_Client_Fixtures.md) (2 shared connections)
- [OMOP Repository](OMOP_Repository.md) (2 shared connections)

## Source Files

- `gen_epix/fastapp/repository.py`
- `test/fastapp/unit/test_fastapp_base_repository.py`

## Audit Trail

- EXTRACTED: 138 (99%)
- INFERRED: 1 (1%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*