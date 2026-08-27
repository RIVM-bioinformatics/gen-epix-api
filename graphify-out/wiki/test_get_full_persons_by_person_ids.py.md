# test_get_full_persons_by_person_ids.py

> 45 nodes · cohesion 0.08

## Key Concepts

- **test_get_full_persons_by_person_ids.py** (18 connections) — `test/omopdb/unit/repositories/test_get_full_persons_by_person_ids.py`
- **omop_sa.py** (15 connections) — `gen_epix/omopdb/repositories/omop_sa.py`
- **omop_dict.py** (12 connections) — `gen_epix/omopdb/repositories/omop_dict.py`
- **repository/omop.py** (11 connections) — `gen_epix/omopdb/domain/repository/omop.py`
- **BaseOmopRepository** (11 connections) — `gen_epix/omopdb/domain/repository/omop.py`
- **OmopDictRepository** (11 connections) — `gen_epix/omopdb/repositories/omop_dict.py`
- **OmopSARepository** (11 connections) — `gen_epix/omopdb/repositories/omop_sa.py`
- **service/omop.py** (9 connections) — `gen_epix/omopdb/domain/service/omop.py`
- **_make_sa_repo()** (8 connections) — `test/omopdb/unit/repositories/test_get_full_persons_by_person_ids.py`
- **.get_person_ids_modified_in_range()** (5 connections) — `gen_epix/omopdb/domain/repository/omop.py`
- **.get_person_ids_modified_in_range()** (5 connections) — `gen_epix/omopdb/repositories/omop_dict.py`
- **_make_dict_repo()** (5 connections) — `test/omopdb/unit/repositories/test_get_full_persons_by_person_ids.py`
- **.get_full_persons_by_person_ids()** (4 connections) — `gen_epix/omopdb/domain/repository/omop.py`
- **UUID** (4 connections)
- **.get_full_persons_by_person_ids()** (4 connections) — `gen_epix/omopdb/repositories/omop_dict.py`
- **UUID** (4 connections)
- **.get_person_ids_modified_in_range()** (4 connections) — `gen_epix/omopdb/repositories/omop_sa.py`
- **UUID** (4 connections)
- **_col_mapper()** (4 connections) — `test/omopdb/unit/repositories/test_get_full_persons_by_person_ids.py`
- **Session** (4 connections)
- **_sa_session()** (4 connections) — `test/omopdb/unit/repositories/test_get_full_persons_by_person_ids.py`
- **.get_specimen_ids_by_cohort_ids()** (3 connections) — `gen_epix/omopdb/domain/repository/omop.py`
- **.get_specimen_ids_by_cohort_ids()** (3 connections) — `gen_epix/omopdb/repositories/omop_dict.py`
- **See parent class method** (3 connections) — `gen_epix/omopdb/repositories/omop_dict.py`
- **.get_full_persons_by_person_ids()** (3 connections) — `gen_epix/omopdb/repositories/omop_sa.py`
- *... and 20 more nodes in this community*

## Relationships

- [BaseUnitOfWork](BaseUnitOfWork.md) (9 shared connections)
- [omopdb/domain/model/__init__.py](omopdb-domain-model-__init__.py.md) (8 shared connections)
- [casedb/repositories/__init__.py](casedb-repositories-__init__.py.md) (7 shared connections)
- [test_get_specimen_ids_by_cohort_ids.py](test_get_specimen_ids_by_cohort_ids.py.md) (6 shared connections)
- [omopdb/domain/enum.py](omopdb-domain-enum.py.md) (5 shared connections)
- [SAUnitOfWork](SAUnitOfWork.md) (3 shared connections)
- [BaseRepository](BaseRepository.md) (2 shared connections)
- [DictRepository](DictRepository.md) (2 shared connections)
- [SARepository](SARepository.md) (2 shared connections)
- [omopdb/repositories/sa_model/__init__.py](omopdb-repositories-sa_model-__init__.py.md) (2 shared connections)
- [services/user_manager.py](services-user_manager.py.md) (1 shared connections)
- [BaseService](BaseService.md) (1 shared connections)

## Source Files

- `gen_epix/omopdb/domain/repository/omop.py`
- `gen_epix/omopdb/domain/service/omop.py`
- `gen_epix/omopdb/repositories/omop_dict.py`
- `gen_epix/omopdb/repositories/omop_sa.py`
- `test/omopdb/unit/repositories/test_get_full_persons_by_person_ids.py`

## Audit Trail

- EXTRACTED: 123 (96%)
- INFERRED: 5 (4%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*