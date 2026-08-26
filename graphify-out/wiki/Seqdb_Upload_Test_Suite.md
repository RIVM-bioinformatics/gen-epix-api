# Seqdb Upload Test Suite

> 194 nodes · cohesion 0.03

## Key Concepts

- **.create_command_and_result_for_samples()** (67 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.create_sample_for_upload()** (67 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **UploadResult** (52 connections) — `gen_epix/commondb/domain/model/upload.py`
- **.create_seq_profile_for_upload()** (33 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **BaseUploadTestCase** (32 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.get_only_allele_profile_result()** (26 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **TestVerifyChildrenSeqProfiles** (24 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.create_seq_for_upload()** (20 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.create_seq_classification_for_upload()** (19 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.mock_existing_seq_profile_lookup()** (18 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.get_only_allele_profile()** (17 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **TestVerifyReferenceData** (17 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.get_only_seq_result()** (15 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **TestVerifyChildrenSeqClassifications** (15 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.get_only_seq_classification()** (14 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.get_only_seq_classification_result()** (14 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.mock_existing_seq_classification_lookup()** (14 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **TestVerifyChildrenSeqs** (14 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.get_only_seq()** (12 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.mock_existing_seq_lookup()** (12 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_temporary_seq_id_is_replaced_and_child_links_are_rewritten()** (11 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **UUID** (10 connections)
- **._run()** (10 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **TestVerifyProtocol** (10 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_existing_id_is_kept_when_already_matching()** (9 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- *... and 169 more nodes in this community*

## Relationships

- [Upload/ETL Result Model](Upload-ETL_Result_Model.md) (88 shared connections)
- [Seqdb Upload Batch Processing](Seqdb_Upload_Batch_Processing.md) (9 shared connections)
- [Identifiers Validation Mixin](Identifiers_Validation_Mixin.md) (9 shared connections)
- [Seqdb Domain Models (Sample/Classification)](Seqdb_Domain_Models_Sample-Classification.md) (7 shared connections)
- [Commondb Upload Test Suite](Commondb_Upload_Test_Suite.md) (7 shared connections)
- [Omopdb Upload Test Suite](Omopdb_Upload_Test_Suite.md) (4 shared connections)
- [Commondb Organization Domain Models](Commondb_Organization_Domain_Models.md) (3 shared connections)
- [ETL Result Logging](ETL_Result_Logging.md) (3 shared connections)
- [Case Upload Batch Model](Case_Upload_Batch_Model.md) (2 shared connections)
- [Seqdb Distance Calculation Tests](Seqdb_Distance_Calculation_Tests.md) (2 shared connections)
- [Case Upload Tests](Case_Upload_Tests.md) (1 shared connections)
- [Case Data Serialization](Case_Data_Serialization.md) (1 shared connections)

## Source Files

- `gen_epix/commondb/domain/model/upload.py`
- `test/commondb/unit/upload/test_commondb_upload.py`
- `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- `test/seqdb/unit/services/seq/upload/test_seqdb_upload_verify_batch_refdata.py`

## Audit Trail

- EXTRACTED: 647 (99%)
- INFERRED: 5 (1%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*