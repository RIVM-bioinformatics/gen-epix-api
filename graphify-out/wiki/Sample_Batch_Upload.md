# Sample Batch Upload

> 125 nodes · cohesion 0.03

## Key Concepts

- **EtlStatus** (91 connections) — `gen_epix/etl/enum.py`
- **test_seqdb_upload.py** (38 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **UploadAction** (37 connections) — `gen_epix/commondb/domain/enum.py`
- **SampleBatchUploadResult** (33 connections) — `gen_epix/seqdb/domain/model/seq/upload.py`
- **UploadSamplesCommand** (31 connections) — `gen_epix/seqdb/domain/command/seq.py`
- **upload_verify_batch.py** (27 connections) — `gen_epix/seqdb/services/seq/upload_verify_batch.py`
- **test_seqdb_upload_verify_batch_refdata.py** (27 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload_verify_batch_refdata.py`
- **services/seq/upload.py** (24 connections) — `gen_epix/seqdb/services/seq/upload.py`
- **_verify_sample_refdata()** (24 connections) — `gen_epix/seqdb/services/seq/upload_verify_batch.py`
- **upload_verify_batch_refdata.py** (23 connections) — `gen_epix/seqdb/services/seq/upload_verify_batch_refdata.py`
- **_verify_batch_refdata_snp_profiles()** (23 connections) — `gen_epix/seqdb/services/seq/upload_verify_batch_refdata.py`
- **BaseSnpUploadTestCase** (20 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload_verify_batch_refdata.py`
- **_verify_protocol()** (19 connections) — `gen_epix/seqdb/services/seq/upload_verify_batch.py`
- **upload_upsert_batch.py** (17 connections) — `gen_epix/seqdb/services/seq/upload_upsert_batch.py`
- **.create_command_and_result()** (16 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload_verify_batch_refdata.py`
- **.create_snp_profile()** (14 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload_verify_batch_refdata.py`
- **_update_profile_distances()** (12 connections) — `gen_epix/seqdb/services/seq/upload_upsert_batch.py`
- **SampleBatchUploader** (11 connections) — `gen_epix/seqdb/services/seq/upload.py`
- **_verify_batch_refdata_allele_profiles()** (11 connections) — `gen_epix/seqdb/services/seq/upload_verify_batch_refdata.py`
- **_verify_batch_refdata_mlva_profiles()** (11 connections) — `gen_epix/seqdb/services/seq/upload_verify_batch_refdata.py`
- **_verify_sample_children()** (11 connections) — `gen_epix/seqdb/services/seq/upload_verify_batch.py`
- **.create_protocol()** (11 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload_verify_batch_refdata.py`
- **_create_sample_refdata()** (10 connections) — `gen_epix/seqdb/services/seq/upload_upsert_batch.py`
- **.mock_crud_for_snp()** (10 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload_verify_batch_refdata.py`
- **_verify_batch_refdata_kmer_profiles()** (9 connections) — `gen_epix/seqdb/services/seq/upload_verify_batch_refdata.py`
- *... and 100 more nodes in this community*

## Relationships

- [Sequence Sample Upload Models](Sequence_Sample_Upload_Models.md) (73 shared connections)
- [ETL Batch Result Models](ETL_Batch_Result_Models.md) (25 shared connections)
- [Case Upload Batch Mixin](Case_Upload_Batch_Mixin.md) (24 shared connections)
- [Case Upload Batch Models](Case_Upload_Batch_Models.md) (22 shared connections)
- [SQLAlchemy Case Repository](SQLAlchemy_Case_Repository.md) (17 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (16 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (15 shared connections)
- [Parent-Child Upload Models](Parent-Child_Upload_Models.md) (9 shared connections)
- [Case Upload Results](Case_Upload_Results.md) (9 shared connections)
- [Upload Identifier Models](Upload_Identifier_Models.md) (8 shared connections)
- [Seqdb Sequence Commands](Seqdb_Sequence_Commands.md) (8 shared connections)
- [Organization & ABAC Models](Organization_&_ABAC_Models.md) (8 shared connections)

## Source Files

- `gen_epix/casedb/domain/service/seqdb.py`
- `gen_epix/casedb/services/seqdb/service.py`
- `gen_epix/commondb/domain/enum.py`
- `gen_epix/etl/enum.py`
- `gen_epix/seqdb/domain/command/seq.py`
- `gen_epix/seqdb/domain/model/seq/upload.py`
- `gen_epix/seqdb/domain/service/seq.py`
- `gen_epix/seqdb/services/client.py`
- `gen_epix/seqdb/services/seq/service.py`
- `gen_epix/seqdb/services/seq/upload.py`
- `gen_epix/seqdb/services/seq/upload_upsert_batch.py`
- `gen_epix/seqdb/services/seq/upload_verify_batch.py`
- `gen_epix/seqdb/services/seq/upload_verify_batch_refdata.py`
- `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- `test/seqdb/unit/services/seq/upload/test_seqdb_upload_verify_batch_refdata.py`

## Audit Trail

- EXTRACTED: 474 (83%)
- INFERRED: 97 (17%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*