# CasedbRemoteApp

> 50 nodes · cohesion 0.09

## Key Concepts

- **CasedbRemoteApp** (47 connections) — `gen_epix/casedb/services/remote_app.py`
- **TestNonCrudHandlers** (21 connections) — `test/casedb/unit/remote_app/test_casedb_remote_app.py`
- **Any** (20 connections)
- **_mock_response()** (19 connections) — `test/casedb/unit/remote_app/test_casedb_remote_app.py`
- **test_casedb_remote_app.py** (13 connections) — `test/casedb/unit/remote_app/test_casedb_remote_app.py`
- **.case_type_set_case_type_update_association()** (4 connections) — `gen_epix/casedb/services/remote_app.py`
- **.col_set_col_update_association()** (4 connections) — `gen_epix/casedb/services/remote_app.py`
- **.create_case_set()** (4 connections) — `gen_epix/casedb/services/remote_app.py`
- **.create_file_for_read_set()** (4 connections) — `gen_epix/casedb/services/remote_app.py`
- **.create_file_for_seq()** (4 connections) — `gen_epix/casedb/services/remote_app.py`
- **.disease_etiological_agent_update_association()** (4 connections) — `gen_epix/casedb/services/remote_app.py`
- **.retrieve_is_own_cases()** (4 connections) — `gen_epix/casedb/services/remote_app.py`
- **UUID** (4 connections)
- **.test_case_type_set_case_type_update_association()** (4 connections) — `test/casedb/unit/remote_app/test_casedb_remote_app.py`
- **.test_col_set_col_update_association()** (4 connections) — `test/casedb/unit/remote_app/test_casedb_remote_app.py`
- **.test_create_case_set()** (4 connections) — `test/casedb/unit/remote_app/test_casedb_remote_app.py`
- **.test_create_file_for_read_set()** (4 connections) — `test/casedb/unit/remote_app/test_casedb_remote_app.py`
- **.test_create_file_for_seq()** (4 connections) — `test/casedb/unit/remote_app/test_casedb_remote_app.py`
- **.test_disease_etiological_agent_update_association()** (4 connections) — `test/casedb/unit/remote_app/test_casedb_remote_app.py`
- **.test_retrieve_case_rights()** (4 connections) — `test/casedb/unit/remote_app/test_casedb_remote_app.py`
- **.test_retrieve_case_set_rights()** (4 connections) — `test/casedb/unit/remote_app/test_casedb_remote_app.py`
- **.test_retrieve_case_stats_by_case_set()** (4 connections) — `test/casedb/unit/remote_app/test_casedb_remote_app.py`
- **.test_retrieve_case_stats_by_case_type()** (4 connections) — `test/casedb/unit/remote_app/test_casedb_remote_app.py`
- **.test_retrieve_cases_by_id()** (4 connections) — `test/casedb/unit/remote_app/test_casedb_remote_app.py`
- **.test_retrieve_complete_case_type()** (4 connections) — `test/casedb/unit/remote_app/test_casedb_remote_app.py`
- *... and 25 more nodes in this community*

## Relationships

- [CrudOperation](CrudOperation.md) (6 shared connections)
- [casedb/domain/command/__init__.py](casedb-domain-command-__init__.py.md) (6 shared connections)
- [Command](Command.md) (3 shared connections)
- [TypedDatetimeRangeFilter](TypedDatetimeRangeFilter.md) (2 shared connections)
- [case_service_create_file_for_read_set_or_seq](case_service_create_file_for_read_set_or_seq.md) (2 shared connections)
- [CommondbRemoteApp](CommondbRemoteApp.md) (1 shared connections)
- [retrieve_case.py](retrieve_case.py.md) (1 shared connections)
- [case/non_persistable.py](case-non_persistable.py.md) (1 shared connections)
- [UploadCasesCommand](UploadCasesCommand.md) (1 shared connections)
- [TestRetrieveCompleteCaseType](TestRetrieveCompleteCaseType.md) (1 shared connections)
- [RetrievePhylogeneticTreeByCasesCommand](RetrievePhylogeneticTreeByCasesCommand.md) (1 shared connections)
- [RetrieveSimilarCasesCommand](RetrieveSimilarCasesCommand.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/services/remote_app.py`
- `test/casedb/unit/remote_app/test_casedb_remote_app.py`

## Audit Trail

- EXTRACTED: 139 (99%)
- INFERRED: 2 (1%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*