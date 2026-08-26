# Case Upload Tests

> 40 nodes · cohesion 0.09

## Key Concepts

- **test_casedb_upload.py** (51 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **scenario_ids** (18 connections)
- **.create_case()** (12 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.create_uploader()** (9 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.update_case()** (8 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **TestExistingContentKeyNormalization** (7 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **TestCaseForUploadContentSerialization** (6 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **TestExistingCaseDataCollectionMutability** (6 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **._run_upsert_with_existing_key()** (6 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.create_org_user()** (5 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_upload_case_cohort_updates()** (5 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_upload_case_content_updates()** (5 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **TestCaseContentUpsertPersistence** (5 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_upsert_batch_update_does_not_persist_none_content_values()** (5 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_existing_case_preserves_created_in_data_collection_id()** (5 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **TestUpsertBatchContentDeletionDelta** (5 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **parametrize** (4 connections)
- **TestCaseCohortUploadUpdates** (4 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **TestCaseContentUploadUpdates** (4 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_upsert_batch_create_does_not_persist_none_content_values()** (4 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_existing_case_with_different_created_in_data_collection_id_fails()** (4 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **TestUpsertBatchCaseDate** (4 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_calculated_case_date_preserved_for_existing_case()** (4 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_content_deletion_delta_is_restored_before_generic_upsert()** (4 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **datetime** (3 connections)
- *... and 15 more nodes in this community*

## Relationships

- [Case Upload Bridge Tests](Case_Upload_Bridge_Tests.md) (20 shared connections)
- [Case Upload Feature Tests](Case_Upload_Feature_Tests.md) (19 shared connections)
- [CaseBatchUploader RBAC Tests](CaseBatchUploader_RBAC_Tests.md) (7 shared connections)
- [Casedb Case CRUD Commands](Casedb_Case_CRUD_Commands.md) (6 shared connections)
- [Upload/ETL Result Model](Upload-ETL_Result_Model.md) (4 shared connections)
- [Case Batch Upload](Case_Batch_Upload.md) (3 shared connections)
- [Commondb Enums & Demo Data](Commondb_Enums_&_Demo_Data.md) (3 shared connections)
- [Case Access Rights](Case_Access_Rights.md) (2 shared connections)
- [Casedb CaseSet CRUD & Tests](Casedb_CaseSet_CRUD_&_Tests.md) (2 shared connections)
- [Commondb Organization Domain Models](Commondb_Organization_Domain_Models.md) (2 shared connections)
- [Default Data Collection Tests](Default_Data_Collection_Tests.md) (2 shared connections)
- [Case Data Collection ABAC Tests](Case_Data_Collection_ABAC_Tests.md) (2 shared connections)

## Source Files

- `test/casedb/unit/services/case/upload/test_casedb_upload.py`

## Audit Trail

- EXTRACTED: 147 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*