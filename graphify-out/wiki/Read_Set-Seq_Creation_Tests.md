# Read Set/Seq Creation Tests

> 18 nodes · cohesion 0.11

## Key Concepts

- **TestGetCasesForCreateReadSetsOrSeqs** (13 connections) — `test/casedb/unit/services/case/upload/test_casedb_create_seq.py`
- **.mock_uow()** (3 connections) — `test/casedb/unit/services/case/upload/test_casedb_create_seq.py`
- **.sample_cases()** (3 connections) — `test/casedb/unit/services/case/upload/test_casedb_create_seq.py`
- **.sample_genetic_reads_cols()** (3 connections) — `test/casedb/unit/services/case/upload/test_casedb_create_seq.py`
- **.sample_genetic_sequence_cols()** (3 connections) — `test/casedb/unit/services/case/upload/test_casedb_create_seq.py`
- **.test_abac_authorization_failure()** (3 connections) — `test/casedb/unit/services/case/upload/test_casedb_create_seq.py`
- **.test_invalid_col_type_for_read_sets_raises_error()** (3 connections) — `test/casedb/unit/services/case/upload/test_casedb_create_seq.py`
- **.test_invalid_command_type_raises_error()** (3 connections) — `test/casedb/unit/services/case/upload/test_casedb_create_seq.py`
- **.test_mismatched_case_type_raises_error()** (3 connections) — `test/casedb/unit/services/case/upload/test_casedb_create_seq.py`
- **Test _get_cases_for_create_file_for_read_sets_or_seqs function.** (1 connections) — `test/casedb/unit/services/case/upload/test_casedb_create_seq.py`
- **Create a mock UnitOfWork for testing.** (1 connections) — `test/casedb/unit/services/case/upload/test_casedb_create_seq.py`
- **Create sample RefCol objects with GENETIC_READS type for testing.** (1 connections) — `test/casedb/unit/services/case/upload/test_casedb_create_seq.py`
- **Create sample RefCol objects with GENETIC_SEQUENCE type for testing.** (1 connections) — `test/casedb/unit/services/case/upload/test_casedb_create_seq.py`
- **Create sample Case objects for testing.** (1 connections) — `test/casedb/unit/services/case/upload/test_casedb_create_seq.py`
- **Test that invalid column type for ReadSets raises InvalidArgumentsError.** (1 connections) — `test/casedb/unit/services/case/upload/test_casedb_create_seq.py`
- **Test that mismatched CaseTypes raise InvalidArgumentsError.** (1 connections) — `test/casedb/unit/services/case/upload/test_casedb_create_seq.py`
- **Test that ABAC authorization failure raises UnauthorizedAuthError.** (1 connections) — `test/casedb/unit/services/case/upload/test_casedb_create_seq.py`
- **Test that invalid command type raises InvalidArgumentsError.** (1 connections) — `test/casedb/unit/services/case/upload/test_casedb_create_seq.py`

## Relationships

- [Case Create Seq Tests](Case_Create_Seq_Tests.md) (5 shared connections)
- [Case File Upload Commands](Case_File_Upload_Commands.md) (4 shared connections)
- [Case Retrieval Tests](Case_Retrieval_Tests.md) (3 shared connections)

## Source Files

- `test/casedb/unit/services/case/upload/test_casedb_create_seq.py`

## Audit Trail

- EXTRACTED: 29 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*