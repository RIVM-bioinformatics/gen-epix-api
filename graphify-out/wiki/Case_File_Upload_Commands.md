# Case File Upload Commands

> 13 nodes · cohesion 0.29

## Key Concepts

- **case_service_create_file_for_read_set_or_seq()** (22 connections) — `gen_epix/casedb/services/case/create_seq.py`
- **_get_cases_for_create_file_for_read_sets_or_seqs()** (17 connections) — `gen_epix/casedb/services/case/create_seq.py`
- **CreateFileForReadSetCommand** (10 connections) — `gen_epix/casedb/domain/command/case.py`
- **CreateFileForSeqCommand** (10 connections) — `gen_epix/casedb/domain/command/case.py`
- **_create_file()** (8 connections) — `gen_epix/casedb/services/case/create_seq.py`
- **UUID** (5 connections)
- **_get_hash_uuid()** (4 connections) — `gen_epix/casedb/services/case/create_seq.py`
- **.create_file_for_read_set()** (4 connections) — `gen_epix/casedb/services/case/service.py`
- **.create_file_for_seq()** (4 connections) — `gen_epix/casedb/services/case/service.py`
- **BaseCaseService** (3 connections)
- **Upload a raw reads file (e.g., FASTQ) for a case's read-set column and return…** (1 connections) — `gen_epix/casedb/domain/command/case.py`
- **Upload an assembled sequence file (e.g., FASTA) for a case's sequence column…** (1 connections) — `gen_epix/casedb/domain/command/case.py`
- **Case** (1 connections)

## Relationships

- [Casedb Case CRUD Commands](Casedb_Case_CRUD_Commands.md) (12 shared connections)
- [File Creation Tests](File_Creation_Tests.md) (8 shared connections)
- [Casedb Domain CRUD Commands](Casedb_Domain_CRUD_Commands.md) (6 shared connections)
- [Read Set/Seq Creation Tests](Read_Set-Seq_Creation_Tests.md) (4 shared connections)
- [Casedb Case Service](Casedb_Case_Service.md) (4 shared connections)
- [Case Service CRUD](Case_Service_CRUD.md) (2 shared connections)
- [File Creation & Case Ownership](File_Creation_&_Case_Ownership.md) (2 shared connections)
- [Case Retrieval Tests](Case_Retrieval_Tests.md) (2 shared connections)
- [Casedb Domain Enums & Policy](Casedb_Domain_Enums_&_Policy.md) (1 shared connections)
- [Seqdb Enums](Seqdb_Enums.md) (1 shared connections)
- [Case ABAC Tests](Case_ABAC_Tests.md) (1 shared connections)
- [File Creation Command](File_Creation_Command.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/domain/command/case.py`
- `gen_epix/casedb/services/case/create_seq.py`
- `gen_epix/casedb/services/case/service.py`

## Audit Trail

- EXTRACTED: 64 (96%)
- INFERRED: 3 (4%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*