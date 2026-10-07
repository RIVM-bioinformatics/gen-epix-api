# Case Upload ABAC Tests

> 27 nodes · cohesion 0.23

## Key Concepts

- **.create_case_for_upload()** (43 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.create_command_and_result()** (42 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **TestVerifyAbacRights** (20 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **._call()** (17 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **._make_abac()** (14 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **UUID** (9 connections)
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
- **.test_dc_absent_from_abacs_denies_all_col_access()** (4 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_has_samples_false_when_no_children_fields_set()** (3 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_has_samples_false_with_empty_read_sets_and_seqs()** (3 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_upsert_batch_skips_seqdb_upload_when_no_samples()** (3 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_get_upload_samples_command_returns_none_without_children()** (3 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_existing_case_includes_dc_links_from_db()** (3 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_mixed_batch_queries_db_only_for_existing_cases()** (3 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_new_case_uses_only_created_in_dc_and_skips_db_query()** (3 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- *... and 2 more nodes in this community*

## Relationships

- [Casedb-Seqdb Upload Bridge](Casedb-Seqdb_Upload_Bridge.md) (21 shared connections)
- [Case Upload Tests](Case_Upload_Tests.md) (16 shared connections)
- [Case Data Collection Updates](Case_Data_Collection_Updates.md) (6 shared connections)
- [Default Data Collection Tests](Default_Data_Collection_Tests.md) (6 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (5 shared connections)
- [Case Content Upsert Tests](Case_Content_Upsert_Tests.md) (4 shared connections)
- [Data Collection ID Handling](Data_Collection_ID_Handling.md) (4 shared connections)
- [Case Upload Validation](Case_Upload_Validation.md) (2 shared connections)
- [Case Upload RBAC Tests](Case_Upload_RBAC_Tests.md) (1 shared connections)
- [Sample Batch Upload](Sample_Batch_Upload.md) (1 shared connections)

## Source Files

- `test/casedb/unit/services/case/upload/test_casedb_upload.py`

## Audit Trail

- EXTRACTED: 146 (99%)
- INFERRED: 2 (1%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*