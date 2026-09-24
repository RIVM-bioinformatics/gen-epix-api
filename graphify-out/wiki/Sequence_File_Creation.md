# Sequence File Creation

> 87 nodes · cohesion 0.03

## Key Concepts

- **casedb/services/case/base.py** (51 connections) — `gen_epix/casedb/services/case/base.py`
- **create_seq.py** (21 connections) — `gen_epix/casedb/services/case/create_seq.py`
- **case_service_create_file_for_read_set_or_seq()** (20 connections) — `gen_epix/casedb/services/case/create_seq.py`
- **_get_cases_for_create_file_for_read_sets_or_seqs()** (17 connections) — `gen_epix/casedb/services/case/create_seq.py`
- **test_casedb_create_seq.py** (14 connections) — `test/casedb/unit/services/case/upload/test_casedb_create_seq.py`
- **TestCasedbCaseCreateSeq** (13 connections) — `test/casedb/unit/services/case/upload/test_casedb_create_seq.py`
- **TestGetCasesForCreateReadSetsOrSeqs** (13 connections) — `test/casedb/unit/services/case/upload/test_casedb_create_seq.py`
- **fixture** (11 connections)
- **TestCaseServiceCreateFileForReadSetOrSeq** (11 connections) — `test/casedb/unit/services/case/upload/test_casedb_create_seq.py`
- **CreateFileForReadSetCommand** (10 connections) — `gen_epix/casedb/domain/command/case.py`
- **CreateFileForSeqCommand** (10 connections) — `gen_epix/casedb/domain/command/case.py`
- **_create_file()** (8 connections) — `gen_epix/casedb/services/case/create_seq.py`
- **case_service_crud_tree_algorithm_class()** (8 connections) — `gen_epix/casedb/services/case/crud_tree_algorithm_class.py`
- **_get_hash_uuid()** (5 connections) — `gen_epix/casedb/services/case/create_seq.py`
- **UUID** (5 connections)
- **case/crud_tree_algorithm_class.py** (5 connections) — `gen_epix/casedb/services/case/crud_tree_algorithm_class.py`
- **UUID** (4 connections)
- **.sample_cols()** (4 connections) — `test/casedb/unit/services/case/upload/test_casedb_create_seq.py`
- **.test_get_cases_success_for_read_sets()** (4 connections) — `test/casedb/unit/services/case/upload/test_casedb_create_seq.py`
- **.test_get_cases_success_for_seqs()** (4 connections) — `test/casedb/unit/services/case/upload/test_casedb_create_seq.py`
- **.mock_case_abac()** (3 connections) — `test/casedb/unit/services/case/upload/test_casedb_create_seq.py`
- **.mock_repository()** (3 connections) — `test/casedb/unit/services/case/upload/test_casedb_create_seq.py`
- **.mock_service()** (3 connections) — `test/casedb/unit/services/case/upload/test_casedb_create_seq.py`
- **.mock_user()** (3 connections) — `test/casedb/unit/services/case/upload/test_casedb_create_seq.py`
- **.sample_case_read_sets()** (3 connections) — `test/casedb/unit/services/case/upload/test_casedb_create_seq.py`
- *... and 62 more nodes in this community*

## Relationships

- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (32 shared connections)
- [Case Type & Column Commands](Case_Type_&_Column_Commands.md) (14 shared connections)
- [Case CRUD Service Operations](Case_CRUD_Service_Operations.md) (8 shared connections)
- [SQLAlchemy Case Repository](SQLAlchemy_Case_Repository.md) (7 shared connections)
- [Base Case Service Interface](Base_Case_Service_Interface.md) (4 shared connections)
- [Case Service Implementation](Case_Service_Implementation.md) (3 shared connections)
- [Case Ownership & File Commands](Case_Ownership_&_File_Commands.md) (2 shared connections)
- [Seqdb Sequence Retrieval Commands](Seqdb_Sequence_Retrieval_Commands.md) (2 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (2 shared connections)
- [Genetic Distance Protocol CRUD](Genetic_Distance_Protocol_CRUD.md) (2 shared connections)
- [Seqdb File Commands & Enums](Seqdb_File_Commands_&_Enums.md) (2 shared connections)
- [File & Result Format Enums](File_&_Result_Format_Enums.md) (2 shared connections)

## Source Files

- `gen_epix/casedb/domain/command/case.py`
- `gen_epix/casedb/services/case/base.py`
- `gen_epix/casedb/services/case/create_seq.py`
- `gen_epix/casedb/services/case/crud_tree_algorithm_class.py`
- `test/casedb/unit/services/case/upload/test_casedb_create_seq.py`

## Audit Trail

- EXTRACTED: 217 (97%)
- INFERRED: 6 (3%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*