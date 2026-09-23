# Case Statistics Tests

> 30 nodes · cohesion 0.14

## Key Concepts

- **DatetimeRangeFilter** (34 connections) — `gen_epix/filter/datetime_range.py`
- **BaseRetrieveStatsTestCase** (12 connections) — `test/casedb/unit/services/case/retrieve_stats/test_casedb_retrieve_stats.py`
- **.create_complete_case_type()** (10 connections) — `test/casedb/unit/services/case/retrieve_stats/test_casedb_retrieve_stats.py`
- **TestCaseTypeStats** (10 connections) — `test/casedb/unit/services/case/retrieve_stats/test_casedb_retrieve_stats.py`
- **.case_type_stats_cmd()** (9 connections) — `test/casedb/unit/services/case/retrieve_stats/test_casedb_retrieve_stats.py`
- **.mock_abac()** (9 connections) — `test/casedb/unit/services/case/retrieve_stats/test_casedb_retrieve_stats.py`
- **.case_set_stats_cmd()** (7 connections) — `test/casedb/unit/services/case/retrieve_stats/test_casedb_retrieve_stats.py`
- **UUID** (7 connections)
- **.test_special_case_case_set_with_no_members()** (7 connections) — `test/casedb/unit/services/case/retrieve_stats/test_casedb_retrieve_stats.py`
- **TestCaseSetStats** (6 connections) — `test/casedb/unit/services/case/retrieve_stats/test_casedb_retrieve_stats.py`
- **.test_case_set_ids_filter_and_stats()** (6 connections) — `test/casedb/unit/services/case/retrieve_stats/test_casedb_retrieve_stats.py`
- **.create_case_set()** (5 connections) — `test/casedb/unit/services/case/retrieve_stats/test_casedb_retrieve_stats.py`
- **.create_case()** (4 connections) — `test/casedb/unit/services/case/retrieve_stats/test_casedb_retrieve_stats.py`
- **.test_no_case_type_ids_full_access_reads_all()** (4 connections) — `test/casedb/unit/services/case/retrieve_stats/test_casedb_retrieve_stats.py`
- **.test_no_case_type_ids_restricted_access_uses_abac_ids()** (4 connections) — `test/casedb/unit/services/case/retrieve_stats/test_casedb_retrieve_stats.py`
- **.test_provided_case_type_ids_authorized_computes_stats()** (4 connections) — `test/casedb/unit/services/case/retrieve_stats/test_casedb_retrieve_stats.py`
- **.test_no_case_sets_initially_sets_ids_from_members_and_returns_empty()** (3 connections) — `test/casedb/unit/services/case/retrieve_stats/test_casedb_retrieve_stats.py`
- **.test_provided_case_type_ids_unauthorized_raises()** (3 connections) — `test/casedb/unit/services/case/retrieve_stats/test_casedb_retrieve_stats.py`
- **.setup_method()** (2 connections) — `test/casedb/unit/services/case/retrieve_stats/test_casedb_retrieve_stats.py`
- **datetime** (2 connections)
- **scenario_ids** (2 connections)
- **mock_read_fields()** (2 connections) — `test/casedb/unit/services/case/retrieve_stats/test_casedb_retrieve_stats.py`
- **.test_missing_abac_policy_raises_assertion()** (2 connections) — `test/casedb/unit/services/case/retrieve_stats/test_casedb_retrieve_stats.py`
- **Represents a filter matching datetimes within the configured bounds.** (1 connections) — `gen_epix/filter/datetime_range.py`
- **Case** (1 connections)
- *... and 5 more nodes in this community*

## Relationships

- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (13 shared connections)
- [Case Repository](Case_Repository.md) (7 shared connections)
- [Casedb Case API Models](Casedb_Case_API_Models.md) (3 shared connections)
- [SQLAlchemy Case Repository](SQLAlchemy_Case_Repository.md) (3 shared connections)
- [Filter Base Abstractions](Filter_Base_Abstractions.md) (3 shared connections)
- [Case Service Implementation](Case_Service_Implementation.md) (3 shared connections)
- [Case Access Rights](Case_Access_Rights.md) (2 shared connections)
- [Role Generation & Hierarchy](Role_Generation_&_Hierarchy.md) (2 shared connections)
- [Sequence File Creation](Sequence_File_Creation.md) (1 shared connections)
- [Commondb SQLAlchemy Mapper](Commondb_SQLAlchemy_Mapper.md) (1 shared connections)
- [Case Association Retrieval](Case_Association_Retrieval.md) (1 shared connections)

## Source Files

- `gen_epix/filter/datetime_range.py`
- `test/casedb/unit/services/case/retrieve_stats/test_casedb_retrieve_stats.py`

## Audit Trail

- EXTRACTED: 85 (85%)
- INFERRED: 15 (15%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*