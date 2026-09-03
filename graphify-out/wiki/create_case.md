# .create_case

> 12 nodes

## Key Concepts

- **.create_case()** (12 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **UUID** (9 connections)
- **.update_case()** (8 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_upload_case_cohort_updates()** (5 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_upload_case_content_updates()** (5 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_existing_case_preserves_created_in_data_collection_id()** (5 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_existing_case_with_different_created_in_data_collection_id_fails()** (4 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **parametrize** (4 connections)
- **datetime** (3 connections)
- **Case** (2 connections)
- **Existing case should maintain its created_in_data_collection_id.** (1 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **Existing cases must not be changed to a different created_in_data_collection_id.** (1 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`

## Relationships

- [test_casedb_upload.py](test_casedb_upload.py.md) (9 shared connections)
- [.create_case_for_upload](create_case_for_upload.md) (8 shared connections)
- [.create_uploader](create_uploader.md) (4 shared connections)
- [BaseUnitOfWork](BaseUnitOfWork.md) (1 shared connections)
- [TestVerifyUserRights](TestVerifyUserRights.md) (1 shared connections)

## Source Files

- `test/casedb/unit/services/case/upload/test_casedb_upload.py`

## Audit Trail

- EXTRACTED: 41 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*