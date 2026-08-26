# Casedb Retrieve Case Query Logic

> 89 nodes · cohesion 0.05

## Key Concepts

- **retrieve_case.py** (36 connections) — `gen_epix/casedb/services/case/retrieve_case.py`
- **BaseRetrieveCaseTestCase** (25 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- **case_service_retrieve_cases_by_query()** (22 connections) — `gen_epix/casedb/services/case/retrieve_case.py`
- **case_service_retrieve_cases_by_id()** (16 connections) — `gen_epix/casedb/services/case/retrieve_case.py`
- **.attach_abac_policy()** (16 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- **.test_happy_path_with_filters_case_sets_and_max_limit()** (14 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- **validate_concept_or_region()** (13 connections) — `gen_epix/casedb/services/case/retrieve_case.py`
- **TestRetrieveCasesByQuery** (13 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- **case_service_retrieve_case_cohort_links_by_case_type()** (12 connections) — `gen_epix/casedb/services/case/retrieve_case.py`
- **_verify_case_filter()** (12 connections) — `gen_epix/casedb/services/case/retrieve_case.py`
- **.set_repository_case_type()** (11 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- **.set_retrieve_cases_result()** (11 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- **_verify_filter_validity()** (10 connections) — `gen_epix/casedb/services/case/retrieve_case.py`
- **.create_case()** (10 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- **.create_case_type()** (10 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- **TestRetrieveCasesById** (10 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- **.test_filter_invalid_members_raises()** (10 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- **.test_filter_invalid_type_raises()** (10 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- **_get_valid_concepts()** (9 connections) — `gen_epix/casedb/services/case/retrieve_case.py`
- **_get_valid_region_values()** (9 connections) — `gen_epix/casedb/services/case/retrieve_case.py`
- **BaseCaseService** (9 connections)
- **_verify_case_set_access()** (9 connections) — `gen_epix/casedb/services/case/retrieve_case.py`
- **.create_col()** (8 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- **.test_happy_path_without_filters_or_case_sets()** (8 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- **RefCol** (7 connections)
- *... and 64 more nodes in this community*

## Relationships

- [Casedb ABAC & Filter Logic](Casedb_ABAC_&_Filter_Logic.md) (40 shared connections)
- [Casedb Case CRUD Commands](Casedb_Case_CRUD_Commands.md) (22 shared connections)
- [Case Query & Rights Retrieval](Case_Query_&_Rights_Retrieval.md) (7 shared connections)
- [Casedb Domain Enums & Policy](Casedb_Domain_Enums_&_Policy.md) (4 shared connections)
- [Casedb Domain CRUD Commands](Casedb_Domain_CRUD_Commands.md) (4 shared connections)
- [Case Domain Enums](Case_Domain_Enums.md) (2 shared connections)
- [Casedb Case Service](Casedb_Case_Service.md) (2 shared connections)
- [Casedb CaseSet CRUD & Tests](Casedb_CaseSet_CRUD_&_Tests.md) (1 shared connections)
- [Upload/ETL Result Model](Upload-ETL_Result_Model.md) (1 shared connections)
- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (1 shared connections)
- [Interval Transformation](Interval_Transformation.md) (1 shared connections)
- [Case Data Serialization](Case_Data_Serialization.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/services/case/retrieve_case.py`
- `gen_epix/casedb/services/case/service.py`
- `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`

## Audit Trail

- EXTRACTED: 277 (92%)
- INFERRED: 24 (8%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*