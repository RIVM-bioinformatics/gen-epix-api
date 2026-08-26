# Case Upload Feature Tests

> 34 nodes · cohesion 0.17

## Key Concepts

- **.create_case_for_upload()** (43 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.create_command_and_result()** (42 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **TestVerifyAbacRights** (19 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **._call()** (17 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **._make_abac()** (14 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **UUID** (9 connections)
- **TestGetCaseDataCollections** (8 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_unauthorized_read_set_col_adds_issue_with_none_orig_value()** (6 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_unauthorized_seq_col_adds_issue_with_none_orig_value()** (6 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **TestCaseServiceUploadCasesFeatureFlag** (5 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_col_access_cached_for_repeated_data_collection()** (5 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_existing_case_skips_creation_check()** (5 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_inaccessible_col_adds_unknown_col_issue_and_removes_from_content()** (5 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_new_case_in_allowed_private_dc_succeeds()** (5 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_new_case_in_dc_without_add_case_fails()** (5 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_new_case_in_non_private_dc_fails()** (5 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_read_only_col_adds_unauthorized_issue_and_removes_from_content()** (5 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_write_access_is_union_across_multiple_data_collections()** (5 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_writeable_col_causes_no_data_issue()** (5 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_batch_with_multiple_different_data_collection_ids()** (4 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_upload_cases_delegates_when_upload_feature_enabled()** (4 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_upload_cases_raises_when_upload_feature_disabled()** (4 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_dc_absent_from_abacs_denies_all_col_access()** (4 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_has_samples_false_when_no_children_fields_set()** (3 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_has_samples_false_with_empty_read_sets_and_seqs()** (3 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- *... and 9 more nodes in this community*

## Relationships

- [Case Upload Bridge Tests](Case_Upload_Bridge_Tests.md) (26 shared connections)
- [Case Upload Tests](Case_Upload_Tests.md) (19 shared connections)
- [Default Data Collection Tests](Default_Data_Collection_Tests.md) (6 shared connections)
- [Case Batch Upload](Case_Batch_Upload.md) (6 shared connections)
- [Case Data Collection ABAC Tests](Case_Data_Collection_ABAC_Tests.md) (3 shared connections)
- [Case Access Rights](Case_Access_Rights.md) (3 shared connections)
- [Case Upload Validation](Case_Upload_Validation.md) (2 shared connections)
- [CaseBatchUploader RBAC Tests](CaseBatchUploader_RBAC_Tests.md) (1 shared connections)

## Source Files

- `test/casedb/unit/services/case/upload/test_casedb_upload.py`

## Audit Trail

- EXTRACTED: 160 (99%)
- INFERRED: 1 (1%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*