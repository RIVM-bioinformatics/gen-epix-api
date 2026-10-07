# Case Upload Validation

> 23 nodes · cohesion 0.12

## Key Concepts

- **CaseForUpload** (14 connections) — `gen_epix/casedb/domain/model/case/upload.py`
- **ReadSetForUpload** (9 connections) — `gen_epix/casedb/domain/model/case/upload.py`
- **SeqForUpload** (9 connections) — `gen_epix/casedb/domain/model/case/upload.py`
- **._validate_case_for_upload()** (6 connections) — `gen_epix/casedb/domain/model/case/upload.py`
- **._validate_read_sets_or_seqs()** (5 connections) — `gen_epix/casedb/domain/model/case/upload.py`
- **._serialize_id()** (4 connections) — `gen_epix/casedb/domain/model/case/upload.py`
- **._validate_read_set_for_upload()** (4 connections) — `gen_epix/casedb/domain/model/case/upload.py`
- **._serialize_id()** (4 connections) — `gen_epix/casedb/domain/model/case/upload.py`
- **._validate_seq_for_upload()** (4 connections) — `gen_epix/casedb/domain/model/case/upload.py`
- **._validate_no_col_id_overlap()** (3 connections) — `gen_epix/casedb/domain/model/case/upload.py`
- **model_validator** (3 connections)
- **Self** (3 connections)
- **UUID** (3 connections)
- **field_serializer** (2 connections)
- **Serialize UUID identifiers as strings while retaining ``None``.** (2 connections) — `gen_epix/casedb/domain/model/case/upload.py`
- **Validate sample ID and assembly protocol.** (1 connections) — `gen_epix/casedb/domain/model/case/upload.py`
- **Represents a case upload with identifiers, read sets, and sequences. Model…** (1 connections) — `gen_epix/casedb/domain/model/case/upload.py`
- **Validate column uniqueness and alternate sample identifier mappings.** (1 connections) — `gen_epix/casedb/domain/model/case/upload.py`
- **Validate one group of read sets or sequences. Args: values: Upload children to…** (1 connections) — `gen_epix/casedb/domain/model/case/upload.py`
- **Validate that read sets and sequences use disjoint columns. Raises: ValueError:…** (1 connections) — `gen_epix/casedb/domain/model/case/upload.py`
- **Represents a read set to upload and associate with a case and sample. A single…** (1 connections) — `gen_epix/casedb/domain/model/case/upload.py`
- **Validate sample ID and sequencing protocol.** (1 connections) — `gen_epix/casedb/domain/model/case/upload.py`
- **Represents a sequence to upload and associate with a case and sample. A single…** (1 connections) — `gen_epix/casedb/domain/model/case/upload.py`

## Relationships

- [Case Upload Batch Models](Case_Upload_Batch_Models.md) (4 shared connections)
- [Upload Identifier Models](Upload_Identifier_Models.md) (4 shared connections)
- [Complete Case Type Models](Complete_Case_Type_Models.md) (3 shared connections)
- [Case Upload ABAC Tests](Case_Upload_ABAC_Tests.md) (2 shared connections)
- [Case Operational Data Models](Case_Operational_Data_Models.md) (2 shared connections)
- [Commondb Base Models](Commondb_Base_Models.md) (2 shared connections)
- [Domain & Entity Registry](Domain_&_Entity_Registry.md) (2 shared connections)
- [Case Upload Test Setup](Case_Upload_Test_Setup.md) (1 shared connections)
- [Batch Upload Validation](Batch_Upload_Validation.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/domain/model/case/upload.py`

## Audit Trail

- EXTRACTED: 45 (87%)
- INFERRED: 7 (13%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*