# Exists Filters

> 73 nodes · cohesion 0.06

## Key Concepts

- **test_casedb_retrieve_case.py** (30 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- **BaseRetrieveCaseTestCase** (24 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- **ExistsFilter** (20 connections) — `gen_epix/filter/exists.py`
- **.attach_abac_policy()** (16 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- **NumberSetFilter** (14 connections) — `gen_epix/filter/number_set.py`
- **TestRetrieveCasesByQuery** (13 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- **.test_happy_path_with_filters_case_sets_and_max_limit()** (13 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- **.set_repository_case_type()** (11 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- **.set_retrieve_cases_result()** (11 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- **.create_case()** (10 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- **.create_case_type()** (10 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- **TestRetrieveCasesById** (10 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- **number_set.py** (9 connections) — `gen_epix/filter/number_set.py`
- **.create_col()** (9 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- **.test_filter_invalid_members_raises()** (9 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- **.test_filter_invalid_type_raises()** (9 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- **exists.py** (8 connections) — `gen_epix/filter/exists.py`
- **.create_composite_filter()** (7 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- **.set_repository_cols_and_ref_cols()** (7 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- **.test_happy_path_without_filters_or_case_sets()** (7 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- **.create_typed_number_set_filter()** (6 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- **.create_typed_string_set_filter()** (6 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- **_FakeCaseAbacPolicy** (6 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- **UUID** (6 connections)
- **test_mapping_branches_decimal_col_type()** (6 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- *... and 48 more nodes in this community*

## Relationships

- [Filter Base Abstractions](Filter_Base_Abstractions.md) (17 shared connections)
- [Range Filters](Range_Filters.md) (11 shared connections)
- [Composite Filters](Composite_Filters.md) (6 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (6 shared connections)
- [Case SQLAlchemy Tables](Case_SQLAlchemy_Tables.md) (6 shared connections)
- [Own-Cases Retrieval Tests](Own-Cases_Retrieval_Tests.md) (3 shared connections)
- [Row Filter Matching](Row_Filter_Matching.md) (2 shared connections)
- [Commondb SQLAlchemy Mapper](Commondb_SQLAlchemy_Mapper.md) (2 shared connections)
- [Transform Enums & Intervals](Transform_Enums_&_Intervals.md) (2 shared connections)
- [FastApp HTTP Client](FastApp_HTTP_Client.md) (2 shared connections)
- [Sequence Distance Calculation](Sequence_Distance_Calculation.md) (2 shared connections)
- [Role Generation & Hierarchy](Role_Generation_&_Hierarchy.md) (2 shared connections)

## Source Files

- `gen_epix/filter/exists.py`
- `gen_epix/filter/number_set.py`
- `test/casedb/unit/services/abac/test_casedb_abac.py`
- `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`

## Audit Trail

- EXTRACTED: 221 (94%)
- INFERRED: 13 (6%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*