# FileCompression

> 30 nodes

## Key Concepts

- **FileCompression** (14 connections) — `gen_epix/seqdb/domain/enum.py`
- **services/file.py** (13 connections) — `gen_epix/seqdb/services/file.py`
- **BaseFileService** (11 connections) — `gen_epix/seqdb/domain/service/file.py`
- **service/file.py** (11 connections) — `gen_epix/seqdb/domain/service/file.py`
- **crud_file.py** (11 connections) — `gen_epix/seqdb/services/seq/crud_file.py`
- **FileService** (8 connections) — `gen_epix/seqdb/services/file.py`
- **file_service_crud_file()** (8 connections) — `gen_epix/seqdb/services/seq/crud_file.py`
- **.crud_file()** (5 connections) — `gen_epix/seqdb/domain/service/file.py`
- **.create_file()** (5 connections) — `gen_epix/seqdb/services/file.py`
- **.crud_file()** (5 connections) — `gen_epix/seqdb/services/file.py`
- **._get_file_text_stream()** (5 connections) — `gen_epix/seqdb/services/file.py`
- **._serialize_file_format()** (4 connections) — `gen_epix/seqdb/domain/model/seq/reads.py`
- **.create_file()** (4 connections) — `gen_epix/seqdb/domain/service/file.py`
- **._verify_fasta_content()** (4 connections) — `gen_epix/seqdb/services/file.py`
- **._verify_fastq_content()** (4 connections) — `gen_epix/seqdb/services/file.py`
- **UUID** (3 connections)
- **UUID** (3 connections)
- **UUID** (2 connections)
- **.register_handlers()** (1 connections) — `gen_epix/seqdb/domain/service/file.py`
- **field_serializer** (1 connections)
- **File** (1 connections)
- **File** (1 connections)
- **File** (1 connections)
- **Create a new file and return its unique identifier.** (1 connections) — `gen_epix/seqdb/domain/service/file.py`
- **Perform CRUD operations on files based on the command.** (1 connections) — `gen_epix/seqdb/domain/service/file.py`
- *... and 5 more nodes in this community*

## Relationships

- [seqdb/domain/enum.py](seqdb-domain-enum.py.md) (7 shared connections)
- [casedb/domain/command/__init__.py](casedb-domain-command-__init__.py.md) (6 shared connections)
- [SeqdbTestClient](SeqdbTestClient.md) (3 shared connections)
- [CrudOperation](CrudOperation.md) (3 shared connections)
- [seqdb/domain/model/__init__.py](seqdb-domain-model-__init__.py.md) (3 shared connections)
- [services/user_manager.py](services-user_manager.py.md) (2 shared connections)
- [BaseService](BaseService.md) (2 shared connections)
- [OrganizationService](OrganizationService.md) (2 shared connections)
- [BaseSeqdbService](BaseSeqdbService.md) (2 shared connections)
- [case_service_create_file_for_read_set_or_seq](case_service_create_file_for_read_set_or_seq.md) (1 shared connections)
- [Seqdb Upload Unit Tests (Base Case)](Seqdb_Upload_Unit_Tests_Base_Case.md) (1 shared connections)
- [validate_int_enum_value](validate_int_enum_value.md) (1 shared connections)

## Source Files

- `gen_epix/seqdb/domain/enum.py`
- `gen_epix/seqdb/domain/model/seq/reads.py`
- `gen_epix/seqdb/domain/service/file.py`
- `gen_epix/seqdb/services/file.py`
- `gen_epix/seqdb/services/seq/crud_file.py`

## Audit Trail

- EXTRACTED: 84 (99%)
- INFERRED: 1 (1%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*