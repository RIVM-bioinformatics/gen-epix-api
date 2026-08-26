# Case Upload Bridge Tests

> 21 nodes · cohesion 0.15

## Key Concepts

- **BaseUploadTestCase** (31 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.create_read_set_for_upload()** (10 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **TestCaseUploadSeqdbBridge** (9 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.create_seq_for_upload()** (8 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **TestCaseBatchHasSamples** (8 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **TestGetUploadSamplesCommandNoCaseGuard** (7 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_has_samples_true_when_case_has_children()** (6 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_get_upload_samples_command_builds_seqdb_batch()** (5 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_upload_samples_maps_results_to_case_and_upload_result()** (5 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_get_upload_samples_command_accepts_sample_id_without_external_id()** (4 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_upload_samples_returns_false_when_seqdb_result_has_failures()** (4 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.create_read_set_for_upload_sample_id_only()** (3 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **ReadSetForUpload** (3 connections)
- **.test_read_set_without_case_returns_failure_and_marks_result_failed()** (3 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_seq_without_case_returns_failure_and_marks_result_failed()** (3 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_upload_samples_aborts_early_when_no_case()** (3 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **SeqForUpload** (2 connections)
- **Tests for the has_case guard added to _get_upload_samples_command.** (1 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **Tests for CaseBatchForUpload.has_samples (the pure predicate on the batch…** (1 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **Tests for the casedb-to-seqdb upload bridge in CaseBatchUploader.** (1 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **Base test case with common fixtures and utility methods.** (1 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`

## Relationships

- [Case Upload Feature Tests](Case_Upload_Feature_Tests.md) (26 shared connections)
- [Case Upload Tests](Case_Upload_Tests.md) (20 shared connections)
- [CaseBatchUploader RBAC Tests](CaseBatchUploader_RBAC_Tests.md) (2 shared connections)
- [Commondb Upload Test Suite](Commondb_Upload_Test_Suite.md) (2 shared connections)
- [Case Data Collection ABAC Tests](Case_Data_Collection_ABAC_Tests.md) (1 shared connections)
- [Default Data Collection Tests](Default_Data_Collection_Tests.md) (1 shared connections)
- [Casedb Case CRUD Commands](Casedb_Case_CRUD_Commands.md) (1 shared connections)
- [Core App Base Class](Core_App_Base_Class.md) (1 shared connections)

## Source Files

- `test/casedb/unit/services/case/upload/test_casedb_upload.py`

## Audit Trail

- EXTRACTED: 84 (98%)
- INFERRED: 2 (2%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*