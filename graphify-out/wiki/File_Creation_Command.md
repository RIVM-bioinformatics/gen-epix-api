# File Creation Command

> 31 nodes · cohesion 0.11

## Key Concepts

- **FileCompression** (14 connections) — `gen_epix/seqdb/domain/enum.py`
- **services/file.py** (13 connections) — `gen_epix/seqdb/services/file.py`
- **service/file.py** (11 connections) — `gen_epix/seqdb/domain/service/file.py`
- **BaseFileService** (11 connections) — `gen_epix/seqdb/domain/service/file.py`
- **crud_file.py** (11 connections) — `gen_epix/seqdb/services/seq/crud_file.py`
- **CreateFileCommand** (9 connections) — `gen_epix/seqdb/domain/command/file.py`
- **FileService** (8 connections) — `gen_epix/seqdb/services/file.py`
- **file_service_crud_file()** (8 connections) — `gen_epix/seqdb/services/seq/crud_file.py`
- **.crud_file()** (5 connections) — `gen_epix/seqdb/domain/service/file.py`
- **.create_file()** (5 connections) — `gen_epix/seqdb/services/file.py`
- **.crud_file()** (5 connections) — `gen_epix/seqdb/services/file.py`
- **._get_file_text_stream()** (5 connections) — `gen_epix/seqdb/services/file.py`
- **.create_file()** (4 connections) — `gen_epix/seqdb/domain/service/file.py`
- **._verify_fasta_content()** (4 connections) — `gen_epix/seqdb/services/file.py`
- **._verify_fastq_content()** (4 connections) — `gen_epix/seqdb/services/file.py`
- **UUID** (3 connections)
- **UUID** (3 connections)
- **UUID** (2 connections)
- **Command** (1 connections)
- **Create a file. The given expected format and compression are used to verify the…** (1 connections) — `gen_epix/seqdb/domain/command/file.py`
- **.register_handlers()** (1 connections) — `gen_epix/seqdb/domain/service/file.py`
- **File** (1 connections)
- **Create a new file and return its unique identifier.** (1 connections) — `gen_epix/seqdb/domain/service/file.py`
- **Perform CRUD operations on files based on the command.** (1 connections) — `gen_epix/seqdb/domain/service/file.py`
- **File** (1 connections)
- *... and 6 more nodes in this community*

## Relationships

- [Seqdb Domain CRUD Commands](Seqdb_Domain_CRUD_Commands.md) (7 shared connections)
- [Seqdb Enums](Seqdb_Enums.md) (7 shared connections)
- [App Composition & Service Wiring](App_Composition_&_Service_Wiring.md) (3 shared connections)
- [Seqdb Test Client](Seqdb_Test_Client.md) (3 shared connections)
- [Commondb Organization Domain Models](Commondb_Organization_Domain_Models.md) (3 shared connections)
- [Abac Service Access Control](Abac_Service_Access_Control.md) (2 shared connections)
- [Seq File Format Validation](Seq_File_Format_Validation.md) (2 shared connections)
- [Organization Service](Organization_Service.md) (2 shared connections)
- [Base Service Class](Base_Service_Class.md) (2 shared connections)
- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (2 shared connections)
- [Seqdb Service CRUD](Seqdb_Service_CRUD.md) (1 shared connections)
- [Casedb Domain CRUD Commands](Casedb_Domain_CRUD_Commands.md) (1 shared connections)

## Source Files

- `gen_epix/seqdb/domain/command/file.py`
- `gen_epix/seqdb/domain/enum.py`
- `gen_epix/seqdb/domain/service/file.py`
- `gen_epix/seqdb/services/file.py`
- `gen_epix/seqdb/services/seq/crud_file.py`

## Audit Trail

- EXTRACTED: 88 (99%)
- INFERRED: 1 (1%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*