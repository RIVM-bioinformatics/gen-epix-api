# Seq File Format Validation

> 32 nodes · cohesion 0.09

## Key Concepts

- **Seq** (29 connections) — `gen_epix/seqdb/domain/model/seq/seq.py`
- **Contig** (11 connections) — `gen_epix/seqdb/domain/model/seq/seq.py`
- **validate_int_enum_value_or_none()** (10 connections) — `gen_epix/commondb/domain/model/base.py`
- **computed_field** (7 connections)
- **SeqFileFormat** (5 connections) — `gen_epix/seqdb/domain/enum.py`
- **._validate_file_compression()** (4 connections) — `gen_epix/seqdb/domain/model/seq/reads.py`
- **._validate_file_format()** (4 connections) — `gen_epix/seqdb/domain/model/seq/reads.py`
- **._validate_file_compression()** (4 connections) — `gen_epix/seqdb/domain/model/seq/seq.py`
- **._validate_file_format()** (4 connections) — `gen_epix/seqdb/domain/model/seq/seq.py`
- **._serialize_id()** (3 connections) — `gen_epix/seqdb/domain/model/seq/seq.py`
- **field_validator** (3 connections)
- **._serialize_contigs()** (3 connections) — `gen_epix/seqdb/domain/model/seq/seq.py`
- **._validate_contigs()** (3 connections) — `gen_epix/seqdb/domain/model/seq/seq.py`
- **._validate_state()** (3 connections) — `gen_epix/seqdb/domain/model/seq/seq.py`
- **IntEnum** (2 connections)
- **field_validator** (2 connections)
- **field_serializer** (2 connections)
- **QualityMixin** (2 connections)
- **UUID** (2 connections)
- **.is_available()** (2 connections) — `gen_epix/seqdb/domain/model/seq/seq.py`
- **.length()** (2 connections) — `gen_epix/seqdb/domain/model/seq/seq.py`
- **.max_contig_length()** (2 connections) — `gen_epix/seqdb/domain/model/seq/seq.py`
- **.median_contig_length()** (2 connections) — `gen_epix/seqdb/domain/model/seq/seq.py`
- **.min_contig_length()** (2 connections) — `gen_epix/seqdb/domain/model/seq/seq.py`
- **.n50()** (2 connections) — `gen_epix/seqdb/domain/model/seq/seq.py`
- *... and 7 more nodes in this community*

## Relationships

- [Seqdb Domain Models (Sample/Classification)](Seqdb_Domain_Models_Sample-Classification.md) (12 shared connections)
- [Entity Key Generation](Entity_Key_Generation.md) (6 shared connections)
- [Seqdb Enums](Seqdb_Enums.md) (4 shared connections)
- [Seq Format Validation](Seq_Format_Validation.md) (3 shared connections)
- [Commondb Organization Domain Models](Commondb_Organization_Domain_Models.md) (2 shared connections)
- [File Creation Command](File_Creation_Command.md) (2 shared connections)
- [Nextclade Sequence Conversion](Nextclade_Sequence_Conversion.md) (2 shared connections)
- [Seqdb Test Client](Seqdb_Test_Client.md) (1 shared connections)
- [Seqdb Upload Test Suite](Seqdb_Upload_Test_Suite.md) (1 shared connections)
- [Seq Model Tests](Seq_Model_Tests.md) (1 shared connections)
- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (1 shared connections)

## Source Files

- `gen_epix/commondb/domain/model/base.py`
- `gen_epix/seqdb/domain/enum.py`
- `gen_epix/seqdb/domain/model/seq/reads.py`
- `gen_epix/seqdb/domain/model/seq/seq.py`

## Audit Trail

- EXTRACTED: 74 (94%)
- INFERRED: 5 (6%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*