# retrieve_case.py

> 41 nodes · cohesion 0.09

## Key Concepts

- **retrieve_case.py** (36 connections) — `gen_epix/casedb/services/case/retrieve_case.py`
- **validate_concept_or_region()** (13 connections) — `gen_epix/casedb/services/case/retrieve_case.py`
- **case_service_retrieve_case_cohort_links_by_case_type()** (12 connections) — `gen_epix/casedb/services/case/retrieve_case.py`
- **_verify_case_filter()** (12 connections) — `gen_epix/casedb/services/case/retrieve_case.py`
- **_verify_filter_validity()** (10 connections) — `gen_epix/casedb/services/case/retrieve_case.py`
- **_get_valid_concepts()** (9 connections) — `gen_epix/casedb/services/case/retrieve_case.py`
- **_get_valid_region_values()** (9 connections) — `gen_epix/casedb/services/case/retrieve_case.py`
- **BaseCaseService** (9 connections)
- **_verify_case_set_access()** (9 connections) — `gen_epix/casedb/services/case/retrieve_case.py`
- **RetrieveCaseCohortLinksByCaseTypeCommand** (8 connections) — `gen_epix/casedb/domain/command/case.py`
- **RefCol** (7 connections)
- **_get_map_functions_for_filters()** (6 connections) — `gen_epix/casedb/services/case/retrieve_case.py`
- **User** (6 connections)
- **TestRetrieveCaseCohortLinksByCaseType** (6 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- **_get_map_function_for_col()** (5 connections) — `gen_epix/casedb/services/case/retrieve_case.py`
- **UUID** (5 connections)
- **_validate_filter_members()** (5 connections) — `gen_epix/casedb/services/case/retrieve_case.py`
- **.retrieve_case_cohort_links_by_case_type()** (4 connections) — `gen_epix/casedb/domain/service/case.py`
- **.retrieve_case_cohort_links_by_case_type()** (4 connections) — `gen_epix/casedb/services/case/service.py`
- **.retrieve_case_cohort_links_by_case_type()** (4 connections) — `gen_epix/casedb/services/remote_app.py`
- **Any** (2 connections)
- **Col** (2 connections)
- **.test_empty_cases_returns_empty_list()** (2 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- **.test_happy_path_returns_all_with_identity_cohort_mapping()** (2 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- **CompositeFilter** (1 connections)
- *... and 16 more nodes in this community*

## Relationships

- [BaseCaseService](BaseCaseService.md) (14 shared connections)
- [BaseRetrieveCaseTestCase](BaseRetrieveCaseTestCase.md) (9 shared connections)
- [composite.py](composite.py.md) (6 shared connections)
- [case/non_persistable.py](case-non_persistable.py.md) (5 shared connections)
- [BaseUnitOfWork](BaseUnitOfWork.md) (5 shared connections)
- [StringSetFilter](StringSetFilter.md) (4 shared connections)
- [UuidSetFilter](UuidSetFilter.md) (4 shared connections)
- [casedb/domain/command/__init__.py](casedb-domain-command-__init__.py.md) (3 shared connections)
- [CrudOperation](CrudOperation.md) (2 shared connections)
- [CompositeFilter](CompositeFilter.md) (2 shared connections)
- [Command](Command.md) (1 shared connections)
- [commondb/domain/literal.py](commondb-domain-literal.py.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/domain/command/case.py`
- `gen_epix/casedb/domain/service/case.py`
- `gen_epix/casedb/services/case/retrieve_case.py`
- `gen_epix/casedb/services/case/service.py`
- `gen_epix/casedb/services/remote_app.py`
- `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`

## Audit Trail

- EXTRACTED: 122 (92%)
- INFERRED: 11 (8%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*