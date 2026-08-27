# DatetimeRangeFilter

> 24 nodes · cohesion 0.15

## Key Concepts

- **DatetimeRangeFilter** (21 connections) — `gen_epix/filter/datetime_range.py`
- **ColType** (18 connections) — `gen_epix/casedb/domain/enum.py`
- **CaseStats** (14 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **case_sa.py** (14 connections) — `gen_epix/casedb/repositories/case_sa.py`
- **repository/case.py** (12 connections) — `gen_epix/casedb/domain/repository/case.py`
- **BaseCaseRepository** (12 connections) — `gen_epix/casedb/domain/repository/case.py`
- **case_dict.py** (11 connections) — `gen_epix/casedb/repositories/case_dict.py`
- **.retrieve_case_stats()** (7 connections) — `gen_epix/casedb/domain/repository/case.py`
- **CaseDictRepository** (6 connections) — `gen_epix/casedb/repositories/case_dict.py`
- **.retrieve_case_stats()** (6 connections) — `gen_epix/casedb/repositories/case_dict.py`
- **CaseSARepository** (6 connections) — `gen_epix/casedb/repositories/case_sa.py`
- **.retrieve_case_stats()** (6 connections) — `gen_epix/casedb/repositories/case_sa.py`
- **.serialize_valid_col_types_by_dim_type()** (5 connections) — `gen_epix/casedb/api/case.py`
- **._validate_model()** (3 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **._get_date_mappers()** (3 connections) — `gen_epix/casedb/domain/repository/case.py`
- **datetime** (2 connections)
- **UUID** (2 connections)
- **UUID** (2 connections)
- **UUID** (2 connections)
- **field_serializer** (1 connections)
- **Serialize dim-type keys and col-type sets to plain string dicts.** (1 connections) — `gen_epix/casedb/api/case.py`
- **model_validator** (1 connections)
- **Self** (1 connections)
- **Retrieve case statistics for a given case type and optional filters.** (1 connections) — `gen_epix/casedb/domain/repository/case.py`

## Relationships

- [BaseUnitOfWork](BaseUnitOfWork.md) (9 shared connections)
- [casedb/repositories/__init__.py](casedb-repositories-__init__.py.md) (7 shared connections)
- [composite.py](composite.py.md) (7 shared connections)
- [TypedDatetimeRangeFilter](TypedDatetimeRangeFilter.md) (6 shared connections)
- [casedb/domain/enum.py](casedb-domain-enum.py.md) (6 shared connections)
- [casedb/domain/model/__init__.py](casedb-domain-model-__init__.py.md) (6 shared connections)
- [Any](Any.md) (3 shared connections)
- [case_service_crud_ref_col](case_service_crud_ref_col.md) (3 shared connections)
- [BaseCaseService](BaseCaseService.md) (3 shared connections)
- [CaseService](CaseService.md) (3 shared connections)
- [test_retrieve_stats.py](test_retrieve_stats.py.md) (2 shared connections)
- [BaseRepository](BaseRepository.md) (2 shared connections)

## Source Files

- `gen_epix/casedb/api/case.py`
- `gen_epix/casedb/domain/enum.py`
- `gen_epix/casedb/domain/model/case/non_persistable.py`
- `gen_epix/casedb/domain/repository/case.py`
- `gen_epix/casedb/repositories/case_dict.py`
- `gen_epix/casedb/repositories/case_sa.py`
- `gen_epix/filter/datetime_range.py`

## Audit Trail

- EXTRACTED: 108 (94%)
- INFERRED: 7 (6%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*