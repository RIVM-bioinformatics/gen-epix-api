# BaseRepository

> 30 nodes · cohesion 0.15

## Key Concepts

- **BaseRepository** (62 connections) — `gen_epix/fastapp/repository.py`
- **.update_association()** (13 connections) — `gen_epix/fastapp/repository.py`
- **Hashable** (13 connections)
- **Model** (12 connections)
- **.crud()** (11 connections) — `gen_epix/fastapp/repository.py`
- **.read_fields()** (7 connections) — `gen_epix/fastapp/repository.py`
- **.verify_crud_args()** (7 connections) — `gen_epix/fastapp/repository.py`
- **Any** (7 connections)
- **._delete_without_associations()** (6 connections) — `gen_epix/fastapp/repository.py`
- **._handle_association_transactions()** (6 connections) — `gen_epix/fastapp/repository.py`
- **._get_obj_id_pairs()** (5 connections) — `gen_epix/fastapp/repository.py`
- **.verify_valid_ids()** (5 connections) — `gen_epix/fastapp/repository.py`
- **.create_repository()** (4 connections) — `gen_epix/fastapp/repository.py`
- **._get_relevant_existing_objs()** (4 connections) — `gen_epix/fastapp/repository.py`
- **._parse_update_association_parameters()** (4 connections) — `gen_epix/fastapp/repository.py`
- **._verify_any_excluded_ids_or_pairs()** (4 connections) — `gen_epix/fastapp/repository.py`
- **._verify_obj_id_pairs_uniqueness()** (4 connections) — `gen_epix/fastapp/repository.py`
- **.clear_repository_content()** (3 connections) — `gen_epix/fastapp/repository.py`
- **.split_filter()** (3 connections) — `gen_epix/fastapp/repository.py`
- **.__init__()** (2 connections) — `gen_epix/fastapp/repository.py`
- **.test_class_abstract_create_repository_raises()** (2 connections) — `test/fastapp/unit/test_fastapp_base_repository.py`
- **.id()** (1 connections) — `gen_epix/fastapp/repository.py`
- **.name()** (1 connections) — `gen_epix/fastapp/repository.py`
- **Update association objects of the given model class that represent an…** (1 connections) — `gen_epix/fastapp/repository.py`
- **Factory method to create a repository instance with the given parameters.** (1 connections) — `gen_epix/fastapp/repository.py`
- *... and 5 more nodes in this community*

## Relationships

- [casedb/repositories/__init__.py](casedb-repositories-__init__.py.md) (12 shared connections)
- [CrudOperation](CrudOperation.md) (9 shared connections)
- [make_assoc](make_assoc.md) (6 shared connections)
- [BaseUnitOfWork](BaseUnitOfWork.md) (6 shared connections)
- [DictRepository](DictRepository.md) (4 shared connections)
- [ServiceTestClient](ServiceTestClient.md) (3 shared connections)
- [Filter](Filter.md) (3 shared connections)
- [BaseAppComposer](BaseAppComposer.md) (2 shared connections)
- [DatetimeRangeFilter](DatetimeRangeFilter.md) (2 shared connections)
- [test_get_full_persons_by_person_ids.py](test_get_full_persons_by_person_ids.py.md) (2 shared connections)
- [SeqSARepository](SeqSARepository.md) (2 shared connections)
- [test_fastapp_rbac_service.py](test_fastapp_rbac_service.py.md) (2 shared connections)

## Source Files

- `gen_epix/fastapp/repository.py`
- `test/fastapp/unit/test_fastapp_base_repository.py`

## Audit Trail

- EXTRACTED: 126 (99%)
- INFERRED: 1 (1%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*