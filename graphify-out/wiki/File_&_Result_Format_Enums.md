# File & Result Format Enums

> 42 nodes · cohesion 0.06

## Key Concepts

- **IntEnumWithJsonSchemaMixin** (18 connections) — `gen_epix/seqdb/domain/enum.py`
- **IntEnum** (15 connections)
- **FileCompression** (14 connections) — `gen_epix/seqdb/domain/enum.py`
- **QualityControlResult** (8 connections) — `gen_epix/seqdb/domain/enum.py`
- **FileFormat** (7 connections) — `gen_epix/seqdb/domain/enum.py`
- **ReadsFileFormat** (6 connections) — `gen_epix/seqdb/domain/enum.py`
- **SeqFileFormat** (6 connections) — `gen_epix/seqdb/domain/enum.py`
- **.__get_pydantic_json_schema__()** (5 connections) — `gen_epix/seqdb/domain/enum.py`
- **SeqDistanceFormat** (5 connections) — `gen_epix/seqdb/domain/enum.py`
- **._serialize_file_format()** (5 connections) — `gen_epix/seqdb/domain/model/seq/reads.py`
- **._validate_file_compression()** (5 connections) — `gen_epix/seqdb/domain/model/seq/reads.py`
- **.create_file()** (5 connections) — `test/seqdb/seqdb_test_client.py`
- **AstResultFormat** (4 connections) — `gen_epix/seqdb/domain/enum.py`
- **PcrResultFormat** (4 connections) — `gen_epix/seqdb/domain/enum.py`
- **SeqClassificationFormat** (4 connections) — `gen_epix/seqdb/domain/enum.py`
- **SeqProfileFormat** (4 connections) — `gen_epix/seqdb/domain/enum.py`
- **SeqTaxonomyFormat** (4 connections) — `gen_epix/seqdb/domain/enum.py`
- **.get_sort_key()** (2 connections) — `gen_epix/seqdb/domain/enum.py`
- **.is_usable()** (2 connections) — `gen_epix/seqdb/domain/enum.py`
- **field_validator** (2 connections)
- **CoreSchema** (1 connections)
- **Encapsulates ordered quality-control outcomes for sequence data.** (1 connections) — `gen_epix/seqdb/domain/enum.py`
- **Return whether this result permits downstream use of the data.** (1 connections) — `gen_epix/seqdb/domain/enum.py`
- **Return an ordering key for quality-control results. The key equals the enum…** (1 connections) — `gen_epix/seqdb/domain/enum.py`
- **Encapsulates enum member names in generated JSON schemas for readability.** (1 connections) — `gen_epix/seqdb/domain/enum.py`
- *... and 17 more nodes in this community*

## Relationships

- [Seqdb File Commands & Enums](Seqdb_File_Commands_&_Enums.md) (15 shared connections)
- [Protocol & Profile Type Enums](Protocol_&_Profile_Type_Enums.md) (6 shared connections)
- [Seqdb Protocol Factories](Seqdb_Protocol_Factories.md) (5 shared connections)
- [Commondb Base Models](Commondb_Base_Models.md) (5 shared connections)
- [Sequence Repository Queries](Sequence_Repository_Queries.md) (3 shared connections)
- [Sequence File Creation](Sequence_File_Creation.md) (2 shared connections)
- [Contig Length Computed Fields](Contig_Length_Computed_Fields.md) (2 shared connections)
- [Sequence Format Conversion](Sequence_Format_Conversion.md) (2 shared connections)
- [Protocol Creation Tests](Protocol_Creation_Tests.md) (1 shared connections)

## Source Files

- `gen_epix/seqdb/domain/enum.py`
- `gen_epix/seqdb/domain/model/seq/reads.py`
- `test/seqdb/seqdb_test_client.py`

## Audit Trail

- EXTRACTED: 94 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*