# Seq Format Validation

> 45 nodes · cohesion 0.06

## Key Concepts

- **Protocol** (42 connections) — `gen_epix/seqdb/domain/model/seq/protocol.py`
- **validate_int_enum_value()** (17 connections) — `gen_epix/commondb/domain/model/base.py`
- **field_validator** (7 connections)
- **ProtocolSet** (6 connections) — `gen_epix/seqdb/domain/model/seq/protocol.py`
- **ProtocolSetMember** (6 connections) — `gen_epix/seqdb/domain/model/seq/protocol.py`
- **._validate_seq_format()** (4 connections) — `gen_epix/seqdb/domain/model/seq/base.py`
- **._serialize_format()** (4 connections) — `gen_epix/seqdb/domain/model/seq/base.py`
- **._validate_format()** (4 connections) — `gen_epix/seqdb/domain/model/seq/base.py`
- **._validate_qc_result()** (4 connections) — `gen_epix/seqdb/domain/model/seq/base.py`
- **._validate_seq_profile_type()** (4 connections) — `gen_epix/seqdb/domain/model/seq/profile.py`
- **._serialize_int_enums()** (4 connections) — `gen_epix/seqdb/domain/model/seq/protocol.py`
- **._serialize_ref_seq_id()** (4 connections) — `gen_epix/seqdb/domain/model/seq/protocol.py`
- **._validate_datetime_to_utc()** (4 connections) — `gen_epix/seqdb/domain/model/seq/protocol.py`
- **._validate_props()** (4 connections) — `gen_epix/seqdb/domain/model/seq/protocol.py`
- **._validate_protocol_type()** (4 connections) — `gen_epix/seqdb/domain/model/seq/protocol.py`
- **._validate_protocol_type_dependencies()** (4 connections) — `gen_epix/seqdb/domain/model/seq/protocol.py`
- **._validate_seq_distance_type()** (4 connections) — `gen_epix/seqdb/domain/model/seq/protocol.py`
- **._validate_seq_profile_type()** (4 connections) — `gen_epix/seqdb/domain/model/seq/protocol.py`
- **field_validator** (3 connections)
- **.get_seq_profile_type_for_distance_protocol()** (3 connections) — `gen_epix/seqdb/domain/model/seq/protocol.py`
- **._validate_git_commit_hash()** (3 connections) — `gen_epix/seqdb/domain/model/seq/protocol.py`
- **._validate_git_repository_uri()** (3 connections) — `gen_epix/seqdb/domain/model/seq/protocol.py`
- **Model** (3 connections)
- **FormatType** (2 connections)
- **datetime** (2 connections)
- *... and 20 more nodes in this community*

## Relationships

- [Seqdb Domain Models (Sample/Classification)](Seqdb_Domain_Models_Sample-Classification.md) (22 shared connections)
- [Entity Key Generation](Entity_Key_Generation.md) (12 shared connections)
- [Seqdb Enums](Seqdb_Enums.md) (8 shared connections)
- [Protocol Field Validation Tests](Protocol_Field_Validation_Tests.md) (6 shared connections)
- [Commondb Organization Domain Models](Commondb_Organization_Domain_Models.md) (5 shared connections)
- [Seq File Format Validation](Seq_File_Format_Validation.md) (3 shared connections)
- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (3 shared connections)
- [Case Type Props Validation](Case_Type_Props_Validation.md) (1 shared connections)
- [Case Data Serialization](Case_Data_Serialization.md) (1 shared connections)

## Source Files

- `gen_epix/commondb/domain/model/base.py`
- `gen_epix/seqdb/domain/model/seq/base.py`
- `gen_epix/seqdb/domain/model/seq/profile.py`
- `gen_epix/seqdb/domain/model/seq/protocol.py`

## Audit Trail

- EXTRACTED: 96 (83%)
- INFERRED: 20 (17%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*