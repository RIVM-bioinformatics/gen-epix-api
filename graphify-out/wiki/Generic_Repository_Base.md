# Generic Repository Base

> 45 nodes · cohesion 0.09

## Key Concepts

- **BaseRepository** (77 connections) — `gen_epix/fastapp/repository.py`
- **.update_association()** (14 connections) — `gen_epix/fastapp/repository.py`
- **Hashable** (13 connections)
- **Model** (12 connections)
- **.crud()** (11 connections) — `gen_epix/fastapp/repository.py`
- **._handle_association_transactions()** (7 connections) — `gen_epix/fastapp/repository.py`
- **.read_fields()** (7 connections) — `gen_epix/fastapp/repository.py`
- **Any** (7 connections)
- **TestRaiseOnDuplicateIds** (7 connections) — `test/fastapp/unit/test_fastapp_base_repository.py`
- **._delete_without_associations()** (6 connections) — `gen_epix/fastapp/repository.py`
- **._get_obj_id_pairs()** (6 connections) — `gen_epix/fastapp/repository.py`
- **.uow()** (6 connections) — `gen_epix/fastapp/repository.py`
- **._parse_update_association_parameters()** (5 connections) — `gen_epix/fastapp/repository.py`
- **.raise_on_duplicate_ids()** (5 connections) — `gen_epix/fastapp/repository.py`
- **.verify_valid_ids()** (5 connections) — `gen_epix/fastapp/repository.py`
- **._get_user_and_repository()** (5 connections) — `gen_epix/fastapp/service.py`
- **.create_repository()** (4 connections) — `gen_epix/fastapp/repository.py`
- **._get_relevant_existing_objs()** (4 connections) — `gen_epix/fastapp/repository.py`
- **.__init__()** (4 connections) — `gen_epix/fastapp/repository.py`
- **get_id_pair()** (4 connections) — `gen_epix/fastapp/repository.py`
- **._verify_any_excluded_ids_or_pairs()** (4 connections) — `gen_epix/fastapp/repository.py`
- **._verify_obj_id_pairs_uniqueness()** (4 connections) — `gen_epix/fastapp/repository.py`
- **.clear_repository_content()** (3 connections) — `gen_epix/fastapp/repository.py`
- **.split_filter()** (3 connections) — `gen_epix/fastapp/repository.py`
- **.id()** (2 connections) — `gen_epix/fastapp/repository.py`
- *... and 20 more nodes in this community*

## Relationships

- [SQLAlchemy Case Repository](SQLAlchemy_Case_Repository.md) (10 shared connections)
- [Domain Registry & ABAC Policies](Domain_Registry_&_ABAC_Policies.md) (7 shared connections)
- [Commondb Repository Interfaces](Commondb_Repository_Interfaces.md) (6 shared connections)
- [FastApp Test Fixtures](FastApp_Test_Fixtures.md) (5 shared connections)
- [App Composer Base](App_Composer_Base.md) (4 shared connections)
- [In-Memory Dict Repository](In-Memory_Dict_Repository.md) (4 shared connections)
- [Casedb Repository Contracts](Casedb_Repository_Contracts.md) (4 shared connections)
- [Audit Metadata Modifiers](Audit_Metadata_Modifiers.md) (4 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (4 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (3 shared connections)
- [CRUD Argument Verification](CRUD_Argument_Verification.md) (3 shared connections)
- [Row Filter Matching](Row_Filter_Matching.md) (3 shared connections)

## Source Files

- `gen_epix/fastapp/repository.py`
- `gen_epix/fastapp/service.py`
- `test/fastapp/unit/test_fastapp_base_repository.py`

## Audit Trail

- EXTRACTED: 149 (91%)
- INFERRED: 14 (9%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*