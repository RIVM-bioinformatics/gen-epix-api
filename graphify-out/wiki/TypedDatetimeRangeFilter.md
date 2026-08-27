# TypedDatetimeRangeFilter

> 41 nodes · cohesion 0.11

## Key Concepts

- **TypedDatetimeRangeFilter** (19 connections) — `gen_epix/filter/datetime_range.py`
- **test_casedb_retrieve_stats.py** (19 connections) — `test/casedb/unit/services/case/retrieve_stats/test_casedb_retrieve_stats.py`
- **case_service_retrieve_case_stats()** (17 connections) — `gen_epix/casedb/services/case/retrieve_stats.py`
- **BaseRetrieveStatsTestCase** (11 connections) — `test/casedb/unit/services/case/retrieve_stats/test_casedb_retrieve_stats.py`
- **.create_complete_case_type()** (10 connections) — `test/casedb/unit/services/case/retrieve_stats/test_casedb_retrieve_stats.py`
- **RetrieveCaseSetStatsCommand** (9 connections) — `gen_epix/casedb/domain/command/case.py`
- **RetrieveCaseTypeStatsCommand** (9 connections) — `gen_epix/casedb/domain/command/case.py`
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
- **.create_case()** (4 connections) — `test/casedb/unit/services/case/retrieve_stats/test_casedb_retrieve_stats.py`
- *... and 16 more nodes in this community*

## Relationships

- [composite.py](composite.py.md) (8 shared connections)
- [DatetimeRangeFilter](DatetimeRangeFilter.md) (6 shared connections)
- [BaseCaseService](BaseCaseService.md) (6 shared connections)
- [casedb/domain/command/__init__.py](casedb-domain-command-__init__.py.md) (5 shared connections)
- [api/case.py](api-case.py.md) (3 shared connections)
- [CrudOperation](CrudOperation.md) (3 shared connections)
- [Command](Command.md) (2 shared connections)
- [CasedbRemoteApp](CasedbRemoteApp.md) (2 shared connections)
- [commondb/domain/enum.py](commondb-domain-enum.py.md) (2 shared connections)
- [SARepository](SARepository.md) (1 shared connections)
- [CaseService](CaseService.md) (1 shared connections)
- [case/non_persistable.py](case-non_persistable.py.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/domain/command/case.py`
- `gen_epix/casedb/domain/service/case.py`
- `gen_epix/casedb/services/case/retrieve_stats.py`
- `gen_epix/casedb/services/case/service.py`
- `gen_epix/casedb/services/remote_app.py`
- `gen_epix/filter/datetime_range.py`
- `test/casedb/unit/services/case/retrieve_stats/test_casedb_retrieve_stats.py`

## Audit Trail

- EXTRACTED: 130 (94%)
- INFERRED: 8 (6%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*