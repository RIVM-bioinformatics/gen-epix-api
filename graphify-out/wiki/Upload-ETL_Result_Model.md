# Upload/ETL Result Model

> 123 nodes · cohesion 0.04

## Key Concepts

- **model/upload.py** (41 connections) — `gen_epix/commondb/domain/model/upload.py`
- **test_seqdb_upload.py** (40 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **commondb/domain/literal.py** (37 connections) — `gen_epix/commondb/domain/literal.py`
- **User** (37 connections) — `gen_epix/commondb/domain/model/organization.py`
- **SampleBatchUploadResult** (32 connections) — `gen_epix/seqdb/domain/model/seq/upload.py`
- **UploadSamplesCommand** (31 connections) — `gen_epix/seqdb/domain/command/seq.py`
- **_verify_children_seq_profiles()** (30 connections) — `gen_epix/seqdb/services/seq/upload_verify_batch.py`
- **test_seqdb_upload_verify_batch_refdata.py** (29 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload_verify_batch_refdata.py`
- **upload_verify_batch.py** (26 connections) — `gen_epix/seqdb/services/seq/upload_verify_batch.py`
- **EtlStatus** (24 connections) — `gen_epix/commondb/domain/enum.py`
- **_verify_sample_refdata()** (24 connections) — `gen_epix/seqdb/services/seq/upload_verify_batch.py`
- **services/seq/upload.py** (23 connections) — `gen_epix/seqdb/services/seq/upload.py`
- **upload_verify_batch_refdata.py** (22 connections) — `gen_epix/seqdb/services/seq/upload_verify_batch_refdata.py`
- **_verify_children_seq_classifications()** (22 connections) — `gen_epix/seqdb/services/seq/upload_verify_batch.py`
- **_verify_batch_refdata_snp_profiles()** (20 connections) — `gen_epix/seqdb/services/seq/upload_verify_batch_refdata.py`
- **_verify_children_seqs()** (19 connections) — `gen_epix/seqdb/services/seq/upload_verify_batch.py`
- **BaseSnpUploadTestCase** (18 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload_verify_batch_refdata.py`
- **UploadAction** (17 connections) — `gen_epix/commondb/domain/enum.py`
- **_verify_protocol()** (17 connections) — `gen_epix/seqdb/services/seq/upload_verify_batch.py`
- **upload_upsert_batch.py** (16 connections) — `gen_epix/seqdb/services/seq/upload_upsert_batch.py`
- **.create_command_and_result()** (16 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload_verify_batch_refdata.py`
- **.create_snp_profile()** (14 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload_verify_batch_refdata.py`
- **SampleBatchUploader** (12 connections) — `gen_epix/seqdb/services/seq/upload.py`
- **_update_profile_distances()** (11 connections) — `gen_epix/seqdb/services/seq/upload_upsert_batch.py`
- **_verify_sample_children()** (11 connections) — `gen_epix/seqdb/services/seq/upload_verify_batch.py`
- *... and 98 more nodes in this community*

## Relationships

- [Seqdb Upload Test Suite](Seqdb_Upload_Test_Suite.md) (88 shared connections)
- [Seqdb Upload Batch Processing](Seqdb_Upload_Batch_Processing.md) (29 shared connections)
- [Casedb Case CRUD Commands](Casedb_Case_CRUD_Commands.md) (21 shared connections)
- [Commondb Enums & Demo Data](Commondb_Enums_&_Demo_Data.md) (21 shared connections)
- [Commondb Organization Domain Models](Commondb_Organization_Domain_Models.md) (20 shared connections)
- [Commondb Upload Test Suite](Commondb_Upload_Test_Suite.md) (19 shared connections)
- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (14 shared connections)
- [Seqdb Domain CRUD Commands](Seqdb_Domain_CRUD_Commands.md) (12 shared connections)
- [Omopdb Upload Test Suite](Omopdb_Upload_Test_Suite.md) (10 shared connections)
- [Casedb CaseSet CRUD & Tests](Casedb_CaseSet_CRUD_&_Tests.md) (8 shared connections)
- [Seqdb Enums](Seqdb_Enums.md) (8 shared connections)
- [Seqdb Distance Calculation Tests](Seqdb_Distance_Calculation_Tests.md) (7 shared connections)

## Source Files

- `gen_epix/casedb/domain/service/seqdb.py`
- `gen_epix/casedb/services/seqdb/service.py`
- `gen_epix/commondb/domain/enum.py`
- `gen_epix/commondb/domain/literal.py`
- `gen_epix/commondb/domain/model/organization.py`
- `gen_epix/commondb/domain/model/upload.py`
- `gen_epix/fastapp/exc.py`
- `gen_epix/seqdb/domain/command/seq.py`
- `gen_epix/seqdb/domain/model/seq/upload.py`
- `gen_epix/seqdb/domain/service/seq.py`
- `gen_epix/seqdb/services/remote_app.py`
- `gen_epix/seqdb/services/seq/service.py`
- `gen_epix/seqdb/services/seq/upload.py`
- `gen_epix/seqdb/services/seq/upload_upsert_batch.py`
- `gen_epix/seqdb/services/seq/upload_verify_batch.py`
- `gen_epix/seqdb/services/seq/upload_verify_batch_refdata.py`
- `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- `test/seqdb/unit/services/seq/upload/test_seqdb_upload_verify_batch_refdata.py`

## Audit Trail

- EXTRACTED: 616 (100%)
- INFERRED: 3 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*