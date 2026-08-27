# BaseCaseService

> 130 nodes · cohesion 0.03

## Key Concepts

- **BaseCaseService** (147 connections) — `gen_epix/casedb/services/case/base.py`
- **case/service.py** (97 connections) — `gen_epix/casedb/services/case/service.py`
- **casedb/services/case/base.py** (49 connections) — `gen_epix/casedb/services/case/base.py`
- **case/crud_common.py** (46 connections) — `gen_epix/casedb/services/case/crud_common.py`
- **casedb/domain/exc.py** (38 connections) — `gen_epix/casedb/domain/exc.py`
- **BaseCaseAbacPolicy** (25 connections) — `gen_epix/casedb/domain/policy/abac.py`
- **test_casedb_retrieve_similar_cases.py** (22 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_similar_cases.py`
- **test_casedb_retrieve_is_own_cases.py** (20 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_is_own_cases.py`
- **case_service_retrieve_is_own_cases()** (19 connections) — `gen_epix/casedb/services/case/retrieve_is_own_cases.py`
- **retrieve_seq.py** (18 connections) — `gen_epix/casedb/services/case/retrieve_seq.py`
- **test_retrieve_complete_case_type.py** (18 connections) — `test/casedb/unit/services/case/retrieve_case/test_retrieve_complete_case_type.py`
- **crud_case.py** (17 connections) — `gen_epix/casedb/services/case/crud_case.py`
- **crud_case_data_collection_link.py** (16 connections) — `gen_epix/casedb/services/case/crud_case_data_collection_link.py`
- **casedb/domain/policy/abac.py** (15 connections) — `gen_epix/casedb/domain/policy/abac.py`
- **case_service_retrieve_similar_cases()** (15 connections) — `gen_epix/casedb/services/case/retrieve_similar_cases.py`
- **.get_case_abac_from_command()** (14 connections) — `gen_epix/casedb/domain/policy/abac.py`
- **retrieve_similar_cases.py** (14 connections) — `gen_epix/casedb/services/case/retrieve_similar_cases.py`
- **crud_ref_col.py** (13 connections) — `gen_epix/casedb/services/case/crud_ref_col.py`
- **retrieve_stats.py** (13 connections) — `gen_epix/casedb/services/case/retrieve_stats.py`
- **retrieve_is_own_cases.py** (12 connections) — `gen_epix/casedb/services/case/retrieve_is_own_cases.py`
- **case_service_retrieve_complete_case_type()** (11 connections) — `gen_epix/casedb/services/case/retrieve_complete_case_type.py`
- **UUID** (10 connections)
- **case_service_crud_case_set_category()** (10 connections) — `gen_epix/casedb/services/case/crud_case_set_category.py`
- **case_service_crud_case_set_status()** (10 connections) — `gen_epix/casedb/services/case/crud_case_set_status.py`
- **case_service_crud_case_type_set_category()** (10 connections) — `gen_epix/casedb/services/case/crud_case_type_set_category.py`
- *... and 105 more nodes in this community*

## Relationships

- [_crud_cascade_delete](_crud_cascade_delete.md) (67 shared connections)
- [get_case_abac_from_command](get_case_abac_from_command.md) (35 shared connections)
- [BaseUnitOfWork](BaseUnitOfWork.md) (23 shared connections)
- [CrudOperation](CrudOperation.md) (21 shared connections)
- [case_service_create_file_for_read_set_or_seq](case_service_create_file_for_read_set_or_seq.md) (20 shared connections)
- [BaseIsOwnCasesTestCase](BaseIsOwnCasesTestCase.md) (19 shared connections)
- [BaseCaseService](BaseCaseService.md) (15 shared connections)
- [crud_dim.py](crud_dim.py.md) (13 shared connections)
- [retrieve_case.py](retrieve_case.py.md) (13 shared connections)
- [CaseService](CaseService.md) (13 shared connections)
- [commondb/domain/enum.py](commondb-domain-enum.py.md) (12 shared connections)
- [composite.py](composite.py.md) (12 shared connections)

## Source Files

- `gen_epix/casedb/domain/exc.py`
- `gen_epix/casedb/domain/policy/abac.py`
- `gen_epix/casedb/services/case/base.py`
- `gen_epix/casedb/services/case/create_case_set.py`
- `gen_epix/casedb/services/case/crud_case.py`
- `gen_epix/casedb/services/case/crud_case_data_collection_link.py`
- `gen_epix/casedb/services/case/crud_case_set_category.py`
- `gen_epix/casedb/services/case/crud_case_set_status.py`
- `gen_epix/casedb/services/case/crud_case_type_set_category.py`
- `gen_epix/casedb/services/case/crud_common.py`
- `gen_epix/casedb/services/case/crud_genetic_distance_protocol.py`
- `gen_epix/casedb/services/case/crud_ref_col.py`
- `gen_epix/casedb/services/case/crud_tree_algorithm.py`
- `gen_epix/casedb/services/case/crud_tree_algorithm_class.py`
- `gen_epix/casedb/services/case/retrieve_complete_case_type.py`
- `gen_epix/casedb/services/case/retrieve_is_own_cases.py`
- `gen_epix/casedb/services/case/retrieve_seq.py`
- `gen_epix/casedb/services/case/retrieve_similar_cases.py`
- `gen_epix/casedb/services/case/retrieve_stats.py`
- `gen_epix/casedb/services/case/service.py`

## Audit Trail

- EXTRACTED: 607 (87%)
- INFERRED: 94 (13%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*