# Case Stats Retrieval

> 42 nodes · cohesion 0.12

## Key Concepts

- **case_service_retrieve_case_stats()** (20 connections) — `gen_epix/casedb/services/case/retrieve_stats.py`
- **TypedDatetimeRangeFilter** (19 connections) — `gen_epix/filter/datetime_range.py`
- **test_casedb_retrieve_stats.py** (19 connections) — `test/casedb/unit/services/case/retrieve_stats/test_casedb_retrieve_stats.py`
- **CaseStats** (15 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **BaseRetrieveStatsTestCase** (11 connections) — `test/casedb/unit/services/case/retrieve_stats/test_casedb_retrieve_stats.py`
- **RetrieveCaseSetStatsCommand** (10 connections) — `gen_epix/casedb/domain/command/case.py`
- **RetrieveCaseTypeStatsCommand** (10 connections) — `gen_epix/casedb/domain/command/case.py`
- **.create_complete_case_type()** (10 connections) — `test/casedb/unit/services/case/retrieve_stats/test_casedb_retrieve_stats.py`
- **.case_type_stats_cmd()** (9 connections) — `test/casedb/unit/services/case/retrieve_stats/test_casedb_retrieve_stats.py`
- **.mock_abac()** (9 connections) — `test/casedb/unit/services/case/retrieve_stats/test_casedb_retrieve_stats.py`
- **TestCaseTypeStats** (9 connections) — `test/casedb/unit/services/case/retrieve_stats/test_casedb_retrieve_stats.py`
- **.case_set_stats_cmd()** (7 connections) — `test/casedb/unit/services/case/retrieve_stats/test_casedb_retrieve_stats.py`
- **UUID** (7 connections)
- **.test_case_set_ids_filter_and_stats()** (7 connections) — `test/casedb/unit/services/case/retrieve_stats/test_casedb_retrieve_stats.py`
- **.test_no_case_type_ids_full_access_reads_all()** (7 connections) — `test/casedb/unit/services/case/retrieve_stats/test_casedb_retrieve_stats.py`
- **datetime** (6 connections)
- **TestCaseSetStats** (6 connections) — `test/casedb/unit/services/case/retrieve_stats/test_casedb_retrieve_stats.py`
- **.test_special_case_case_set_with_no_members()** (6 connections) — `test/casedb/unit/services/case/retrieve_stats/test_casedb_retrieve_stats.py`
- **.test_no_case_type_ids_restricted_access_uses_abac_ids()** (6 connections) — `test/casedb/unit/services/case/retrieve_stats/test_casedb_retrieve_stats.py`
- **.test_provided_case_type_ids_authorized_computes_stats()** (6 connections) — `test/casedb/unit/services/case/retrieve_stats/test_casedb_retrieve_stats.py`
- **.retrieve_case_stats()** (5 connections) — `gen_epix/casedb/domain/service/case.py`
- **.retrieve_case_stats()** (5 connections) — `gen_epix/casedb/services/case/service.py`
- **.create_case_set()** (5 connections) — `test/casedb/unit/services/case/retrieve_stats/test_casedb_retrieve_stats.py`
- **.retrieve_case_set_stats()** (4 connections) — `gen_epix/casedb/services/remote_app.py`
- **.retrieve_case_type_stats()** (4 connections) — `gen_epix/casedb/services/remote_app.py`
- *... and 17 more nodes in this community*

## Relationships

- [Casedb ABAC & Filter Logic](Casedb_ABAC_&_Filter_Logic.md) (12 shared connections)
- [Casedb Domain CRUD Commands](Casedb_Domain_CRUD_Commands.md) (7 shared connections)
- [Case Domain Enums](Case_Domain_Enums.md) (6 shared connections)
- [Case Data Serialization](Case_Data_Serialization.md) (3 shared connections)
- [Casedb Domain Enums & Policy](Casedb_Domain_Enums_&_Policy.md) (3 shared connections)
- [Case API Endpoints](Case_API_Endpoints.md) (3 shared connections)
- [Project Utility Functions](Project_Utility_Functions.md) (2 shared connections)
- [Case Query & Rights Retrieval](Case_Query_&_Rights_Retrieval.md) (2 shared connections)
- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (2 shared connections)
- [Casedb Case CRUD Commands](Casedb_Case_CRUD_Commands.md) (2 shared connections)
- [Casedb Remote App Client](Casedb_Remote_App_Client.md) (2 shared connections)
- [Upload/ETL Result Model](Upload-ETL_Result_Model.md) (2 shared connections)

## Source Files

- `gen_epix/casedb/domain/command/case.py`
- `gen_epix/casedb/domain/model/case/non_persistable.py`
- `gen_epix/casedb/domain/service/case.py`
- `gen_epix/casedb/services/case/retrieve_stats.py`
- `gen_epix/casedb/services/case/service.py`
- `gen_epix/casedb/services/remote_app.py`
- `gen_epix/filter/datetime_range.py`
- `test/casedb/unit/services/case/retrieve_stats/test_casedb_retrieve_stats.py`

## Audit Trail

- EXTRACTED: 144 (94%)
- INFERRED: 9 (6%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*