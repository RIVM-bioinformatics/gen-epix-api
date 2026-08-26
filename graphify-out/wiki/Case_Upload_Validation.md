# Case Upload Validation

> 23 nodes · cohesion 0.12

## Key Concepts

- **CaseForUpload** (14 connections) — `gen_epix/casedb/domain/model/case/upload.py`
- **ReadSetForUpload** (10 connections) — `gen_epix/casedb/domain/model/case/upload.py`
- **SeqForUpload** (10 connections) — `gen_epix/casedb/domain/model/case/upload.py`
- **._validate_case_for_upload()** (6 connections) — `gen_epix/casedb/domain/model/case/upload.py`
- **._validate_read_sets_or_seqs()** (4 connections) — `gen_epix/casedb/domain/model/case/upload.py`
- **._validate_read_set_for_upload()** (4 connections) — `gen_epix/casedb/domain/model/case/upload.py`
- **._validate_seq_for_upload()** (4 connections) — `gen_epix/casedb/domain/model/case/upload.py`
- **._validate_no_col_id_overlap()** (3 connections) — `gen_epix/casedb/domain/model/case/upload.py`
- **model_validator** (3 connections)
- **Self** (3 connections)
- **UUID** (3 connections)
- **._serialize_id()** (3 connections) — `gen_epix/casedb/domain/model/case/upload.py`
- **._serialize_id()** (3 connections) — `gen_epix/casedb/domain/model/case/upload.py`
- **field_serializer** (2 connections)
- **Model** (2 connections)
- **ParentForUpload** (1 connections)
- **Validate sample ID and assembly protocol.** (1 connections) — `gen_epix/casedb/domain/model/case/upload.py`
- **A case intended for upload, together with any relevant associated data.** (1 connections) — `gen_epix/casedb/domain/model/case/upload.py`
- **Verify that read_sets and seqs contain no duplicate col_id, no overlapping…** (1 connections) — `gen_epix/casedb/domain/model/case/upload.py`
- **Verify that col_ids in read_sets and seqs do not overlap.** (1 connections) — `gen_epix/casedb/domain/model/case/upload.py`
- **A single read set to be uploaded and associated with both an existing case in…** (1 connections) — `gen_epix/casedb/domain/model/case/upload.py`
- **Validate sample ID and sequencing protocol.** (1 connections) — `gen_epix/casedb/domain/model/case/upload.py`
- **A single sequence to be uploaded and associated with both an existing case in…** (1 connections) — `gen_epix/casedb/domain/model/case/upload.py`

## Relationships

- [Case Data Serialization](Case_Data_Serialization.md) (8 shared connections)
- [Commondb Organization Domain Models](Commondb_Organization_Domain_Models.md) (4 shared connections)
- [Case Upload Feature Tests](Case_Upload_Feature_Tests.md) (2 shared connections)
- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (2 shared connections)
- [FastApp Entity & Model Core](FastApp_Entity_&_Model_Core.md) (2 shared connections)
- [Case Upload Test Setup](Case_Upload_Test_Setup.md) (1 shared connections)
- [Identifiers Validation Mixin](Identifiers_Validation_Mixin.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/domain/model/case/upload.py`

## Audit Trail

- EXTRACTED: 45 (88%)
- INFERRED: 6 (12%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*