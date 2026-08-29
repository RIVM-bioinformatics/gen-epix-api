# .create_case_for_upload

> 36 nodes

## Key Concepts

- **.create_case_for_upload()** (43 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.create_command_and_result()** (42 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **TestVerifyAbacRights** (19 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **._call()** (17 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **._make_abac()** (14 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **TestCaseBatchHasSamples** (8 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_has_samples_true_when_case_has_children()** (6 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_unauthorized_read_set_col_adds_issue_with_none_orig_value()** (6 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_unauthorized_seq_col_adds_issue_with_none_orig_value()** (6 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
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
- **.test_new_case_with_explicit_data_collection_id()** (4 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_upload_cases_delegates_when_upload_feature_enabled()** (4 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_upload_cases_raises_when_upload_feature_disabled()** (4 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_error_when_no_default_and_case_needs_one()** (4 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_existing_case_created_in_dc_id_preserved()** (4 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_new_case_with_explicit_created_in_dc_id_unchanged()** (4 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- *... and 11 more nodes in this community*

## Relationships

- [.create_read_set_for_upload](create_read_set_for_upload.md) (19 shared connections)
- [test_casedb_upload.py](test_casedb_upload.py.md) (16 shared connections)
- [.create_case](create_case.md) (8 shared connections)
- [TestGetCaseDataCollections](TestGetCaseDataCollections.md) (7 shared connections)
- [UploadCasesCommand](UploadCasesCommand.md) (6 shared connections)
- [.create_uploader](create_uploader.md) (4 shared connections)
- [CaseTypeAccessAbac](CaseTypeAccessAbac.md) (3 shared connections)
- [CaseForUpload](CaseForUpload.md) (2 shared connections)
- [TestVerifyUserRights](TestVerifyUserRights.md) (1 shared connections)

## Source Files

- `test/casedb/unit/services/case/upload/test_casedb_upload.py`

## Audit Trail

- EXTRACTED: 159 (99%)
- INFERRED: 1 (1%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*