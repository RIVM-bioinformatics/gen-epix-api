# BaseRetrieveCaseTestCase

> 54 nodes · cohesion 0.10

## Key Concepts

- **BaseRetrieveCaseTestCase** (25 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- **case_service_retrieve_cases_by_query()** (22 connections) — `gen_epix/casedb/services/case/retrieve_case.py`
- **case_service_retrieve_cases_by_id()** (16 connections) — `gen_epix/casedb/services/case/retrieve_case.py`
- **.attach_abac_policy()** (16 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- **.test_happy_path_with_filters_case_sets_and_max_limit()** (14 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- **TestRetrieveCasesByQuery** (13 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- **.set_repository_case_type()** (11 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- **.set_retrieve_cases_result()** (11 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- **.create_case()** (10 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- **.create_case_type()** (10 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- **TestRetrieveCasesById** (10 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- **.test_filter_invalid_members_raises()** (10 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- **.test_filter_invalid_type_raises()** (10 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- **.create_col()** (8 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- **.test_happy_path_without_filters_or_case_sets()** (8 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- **.create_composite_filter()** (7 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- **.set_repository_cols_and_ref_cols()** (7 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- **test_mapping_branches_decimal_col_type()** (7 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- **test_mapping_branches_text_col_type()** (7 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- **.test_max_limit_truncates_cases()** (7 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- **.test_zero_read_max_falls_back_to_service_default()** (7 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- **.create_typed_number_set_filter()** (6 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- **.create_typed_string_set_filter()** (6 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- **_FakeCaseAbacPolicy** (6 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- **UUID** (6 connections)
- *... and 29 more nodes in this community*

## Relationships

- [composite.py](composite.py.md) (24 shared connections)
- [retrieve_case.py](retrieve_case.py.md) (9 shared connections)
- [BaseCaseService](BaseCaseService.md) (8 shared connections)
- [case/non_persistable.py](case-non_persistable.py.md) (4 shared connections)
- [CaseService](CaseService.md) (1 shared connections)
- [Command](Command.md) (1 shared connections)
- [Role](Role.md) (1 shared connections)
- [DatetimeRangeFilter](DatetimeRangeFilter.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/services/case/retrieve_case.py`
- `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`

## Audit Trail

- EXTRACTED: 176 (93%)
- INFERRED: 13 (7%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*