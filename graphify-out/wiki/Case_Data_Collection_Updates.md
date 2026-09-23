# Case Data Collection Updates

> 16 nodes · cohesion 0.17

## Key Concepts

- **.create_case()** (12 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.update_case()** (9 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **TestExistingCaseDataCollectionMutability** (7 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_upload_case_cohort_updates()** (6 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **TestCaseCohortUploadUpdates** (5 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **TestCaseContentUploadUpdates** (5 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_upload_case_content_updates()** (5 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_existing_case_preserves_created_in_data_collection_id()** (5 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **parametrize** (4 connections)
- **.test_existing_case_with_different_created_in_data_collection_id_fails()** (4 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **datetime** (3 connections)
- **Case** (2 connections)
- **Tests for existing case data collection handling, including NULL_ID edge case.…** (1 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **Existing case should maintain its created_in_data_collection_id.** (1 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **Existing cases must not be changed to a different created_in_data_collection_id.** (1 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **_resolve()** (1 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`

## Relationships

- [Case Upload Tests](Case_Upload_Tests.md) (15 shared connections)
- [Case Upload ABAC Tests](Case_Upload_ABAC_Tests.md) (6 shared connections)
- [Sample Batch Upload](Sample_Batch_Upload.md) (3 shared connections)
- [Case Content Upsert Tests](Case_Content_Upsert_Tests.md) (2 shared connections)
- [ETL Batch Result Models](ETL_Batch_Result_Models.md) (1 shared connections)
- [Casedb-Seqdb Upload Bridge](Casedb-Seqdb_Upload_Bridge.md) (1 shared connections)
- [Case Upload RBAC Tests](Case_Upload_RBAC_Tests.md) (1 shared connections)

## Source Files

- `test/casedb/unit/services/case/upload/test_casedb_upload.py`

## Audit Trail

- EXTRACTED: 46 (92%)
- INFERRED: 4 (8%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*