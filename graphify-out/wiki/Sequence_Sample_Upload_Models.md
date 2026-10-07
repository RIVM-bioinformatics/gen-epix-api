# Sequence Sample Upload Models

> 174 nodes · cohesion 0.04

## Key Concepts

- **.create_command_and_result_for_samples()** (67 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.create_sample_for_upload()** (67 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **BaseUploadTestCase** (36 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.create_seq_profile_for_upload()** (33 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **_verify_children_seq_profiles()** (31 connections) — `gen_epix/seqdb/services/seq/upload_verify_batch.py`
- **.get_only_allele_profile_result()** (26 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **TestVerifyChildrenSeqProfiles** (26 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **_verify_children_seq_classifications()** (23 connections) — `gen_epix/seqdb/services/seq/upload_verify_batch.py`
- **_verify_children_seqs()** (20 connections) — `gen_epix/seqdb/services/seq/upload_verify_batch.py`
- **.create_seq_for_upload()** (20 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.create_seq_classification_for_upload()** (19 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.mock_existing_seq_profile_lookup()** (18 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **TestVerifyReferenceData** (18 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.get_only_allele_profile()** (17 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **TestVerifyChildrenSeqClassifications** (16 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.get_only_seq_result()** (15 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **TestVerifyChildrenSeqs** (15 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.get_only_seq_classification()** (14 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.get_only_seq_classification_result()** (14 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.mock_existing_seq_classification_lookup()** (14 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **SeqClassificationForUpload** (12 connections) — `gen_epix/seqdb/domain/model/seq/upload.py`
- **.get_only_seq()** (12 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.mock_existing_seq_lookup()** (12 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **SampleForUpload** (11 connections) — `gen_epix/seqdb/domain/model/seq/upload.py`
- **.test_temporary_seq_id_is_replaced_and_child_links_are_rewritten()** (11 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- *... and 149 more nodes in this community*

## Relationships

- [Sample Batch Upload](Sample_Batch_Upload.md) (73 shared connections)
- [Seq Profile Upload Validation](Seq_Profile_Upload_Validation.md) (6 shared connections)
- [ETL Batch Result Models](ETL_Batch_Result_Models.md) (6 shared connections)
- [Case Upload Batch Models](Case_Upload_Batch_Models.md) (4 shared connections)
- [SQLAlchemy Case Repository](SQLAlchemy_Case_Repository.md) (4 shared connections)
- [Reference Data Access Filters](Reference_Data_Access_Filters.md) (3 shared connections)
- [Case Upload Batch Mixin](Case_Upload_Batch_Mixin.md) (3 shared connections)
- [Organization & ABAC Models](Organization_&_ABAC_Models.md) (2 shared connections)
- [Commondb Base Models](Commondb_Base_Models.md) (2 shared connections)
- [Seq Upload & SQL Models](Seq_Upload_&_SQL_Models.md) (2 shared connections)
- [Case Upload Results](Case_Upload_Results.md) (2 shared connections)
- [Sample Upload Batch Tests](Sample_Upload_Batch_Tests.md) (1 shared connections)

## Source Files

- `gen_epix/seqdb/domain/model/seq/upload.py`
- `gen_epix/seqdb/services/seq/upload_verify_batch.py`
- `test/commondb/unit/upload/test_commondb_upload.py`
- `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`

## Audit Trail

- EXTRACTED: 621 (96%)
- INFERRED: 23 (4%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*