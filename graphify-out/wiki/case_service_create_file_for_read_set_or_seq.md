# case_service_create_file_for_read_set_or_seq

> 79 nodes · cohesion 0.04

## Key Concepts

- **case_service_create_file_for_read_set_or_seq()** (22 connections) — `gen_epix/casedb/services/case/create_seq.py`
- **retrieve_complete_case_type.py** (21 connections) — `gen_epix/casedb/services/case/retrieve_complete_case_type.py`
- **create_seq.py** (20 connections) — `gen_epix/casedb/services/case/create_seq.py`
- **_get_cases_for_create_file_for_read_sets_or_seqs()** (17 connections) — `gen_epix/casedb/services/case/create_seq.py`
- **test_casedb_create_seq.py** (14 connections) — `test/casedb/unit/services/case/upload/test_casedb_create_seq.py`
- **TestGetCasesForCreateReadSetsOrSeqs** (13 connections) — `test/casedb/unit/services/case/upload/test_casedb_create_seq.py`
- **TestCasedbCaseCreateSeq** (12 connections) — `test/casedb/unit/services/case/upload/test_casedb_create_seq.py`
- **fixture** (11 connections)
- **CreateFileForReadSetCommand** (10 connections) — `gen_epix/casedb/domain/command/case.py`
- **CreateFileForSeqCommand** (10 connections) — `gen_epix/casedb/domain/command/case.py`
- **TestCaseServiceCreateFileForReadSetOrSeq** (10 connections) — `test/casedb/unit/services/case/upload/test_casedb_create_seq.py`
- **_create_file()** (8 connections) — `gen_epix/casedb/services/case/create_seq.py`
- **UUID** (5 connections)
- **_get_hash_uuid()** (4 connections) — `gen_epix/casedb/services/case/create_seq.py`
- **.create_file_for_read_set()** (4 connections) — `gen_epix/casedb/services/case/service.py`
- **.create_file_for_seq()** (4 connections) — `gen_epix/casedb/services/case/service.py`
- **UUID** (4 connections)
- **.sample_cols()** (4 connections) — `test/casedb/unit/services/case/upload/test_casedb_create_seq.py`
- **.test_get_cases_success_for_read_sets()** (4 connections) — `test/casedb/unit/services/case/upload/test_casedb_create_seq.py`
- **.test_get_cases_success_for_seqs()** (4 connections) — `test/casedb/unit/services/case/upload/test_casedb_create_seq.py`
- **BaseCaseService** (3 connections)
- **.mock_case_abac()** (3 connections) — `test/casedb/unit/services/case/upload/test_casedb_create_seq.py`
- **.mock_repository()** (3 connections) — `test/casedb/unit/services/case/upload/test_casedb_create_seq.py`
- **.mock_service()** (3 connections) — `test/casedb/unit/services/case/upload/test_casedb_create_seq.py`
- **.mock_user()** (3 connections) — `test/casedb/unit/services/case/upload/test_casedb_create_seq.py`
- *... and 54 more nodes in this community*

## Relationships

- [BaseCaseService](BaseCaseService.md) (22 shared connections)
- [casedb/domain/command/__init__.py](casedb-domain-command-__init__.py.md) (6 shared connections)
- [CrudOperation](CrudOperation.md) (5 shared connections)
- [BaseUnitOfWork](BaseUnitOfWork.md) (5 shared connections)
- [CaseService](CaseService.md) (4 shared connections)
- [casedb/domain/enum.py](casedb-domain-enum.py.md) (3 shared connections)
- [CasedbRemoteApp](CasedbRemoteApp.md) (2 shared connections)
- [Command](Command.md) (2 shared connections)
- [seqdb/domain/enum.py](seqdb-domain-enum.py.md) (2 shared connections)
- [casedb/domain/model/__init__.py](casedb-domain-model-__init__.py.md) (2 shared connections)
- [DatetimeRangeFilter](DatetimeRangeFilter.md) (2 shared connections)
- [SeqdbTestClient](SeqdbTestClient.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/domain/command/case.py`
- `gen_epix/casedb/services/case/create_seq.py`
- `gen_epix/casedb/services/case/retrieve_complete_case_type.py`
- `gen_epix/casedb/services/case/service.py`
- `test/casedb/unit/services/case/upload/test_casedb_create_seq.py`

## Audit Trail

- EXTRACTED: 181 (98%)
- INFERRED: 4 (2%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*