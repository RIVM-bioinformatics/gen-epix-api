# .create_read_set_for_upload

> 17 nodes · cohesion 0.16

## Key Concepts

- **.create_read_set_for_upload()** (10 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **TestCaseUploadSeqdbBridge** (9 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.create_seq_for_upload()** (8 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **TestGetUploadSamplesCommandNoCaseGuard** (7 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_get_upload_samples_command_builds_seqdb_batch()** (5 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_upload_samples_maps_results_to_case_and_upload_result()** (5 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_get_upload_samples_command_accepts_sample_id_without_external_id()** (4 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_upload_samples_returns_false_when_seqdb_result_has_failures()** (4 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.create_read_set_for_upload_sample_id_only()** (3 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **ReadSetForUpload** (3 connections)
- **.test_get_upload_samples_command_returns_none_without_children()** (3 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_read_set_without_case_returns_failure_and_marks_result_failed()** (3 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_seq_without_case_returns_failure_and_marks_result_failed()** (3 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_upload_samples_aborts_early_when_no_case()** (3 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **SeqForUpload** (2 connections)
- **Tests for the has_case guard added to _get_upload_samples_command.** (1 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **Tests for the casedb-to-seqdb upload bridge in CaseBatchUploader.** (1 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`

## Relationships

- [.create_case_for_upload](create_case_for_upload.md) (19 shared connections)
- [test_casedb_upload.py](test_casedb_upload.py.md) (9 shared connections)
- [IdentifierForUpload](IdentifierForUpload.md) (2 shared connections)

## Source Files

- `test/casedb/unit/services/case/upload/test_casedb_upload.py`

## Audit Trail

- EXTRACTED: 52 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*