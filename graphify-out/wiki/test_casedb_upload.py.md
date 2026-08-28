# test_casedb_upload.py

> 28 nodes · cohesion 0.13

## Key Concepts

- **test_casedb_upload.py** (51 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **BaseUploadTestCase** (31 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **scenario_ids** (18 connections)
- **TestSetDefaultCreatedInDataCollectionId** (7 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **TestCaseDataCollectionIdHandling** (6 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **TestCaseForUploadContentSerialization** (6 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **TestExistingCaseDataCollectionMutability** (6 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.setup_method()** (5 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **TestCaseContentUpsertPersistence** (5 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **TestCaseServiceUploadCasesFeatureFlag** (5 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **TestUpsertBatchContentDeletionDelta** (5 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **_to_casedb_role_set()** (5 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **TestCaseCohortUploadUpdates** (4 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **TestCaseContentUploadUpdates** (4 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **TestUpsertBatchCaseDate** (4 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **TestCaseDateMutability** (3 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **_mock_uow()** (2 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_case_for_upload_preserves_none_content_value()** (2 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_plain_case_also_serializes_none_content_value()** (2 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **Unit tests for casedb case upload functionality.** (1 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **Tests for existing case data collection handling, including NULL_ID edge case.…** (1 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **Map commondb role enums to casedb role strings with CASEDB_ prefix.** (1 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **Base test case with common fixtures and utility methods.** (1 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **LSP-3647 regression: CaseBatchUploader.upsert_batch merges incoming content…** (1 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **LSP-3645: a None content value signals "delete this key" and must survive…** (1 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- *... and 3 more nodes in this community*

## Relationships

- [.create_case_for_upload](create_case_for_upload.md) (16 shared connections)
- [.create_uploader](create_uploader.md) (10 shared connections)
- [.create_case](create_case.md) (9 shared connections)
- [.create_read_set_for_upload](create_read_set_for_upload.md) (9 shared connections)
- [commondb/domain/enum.py](commondb-domain-enum.py.md) (6 shared connections)
- [BaseCaseService](BaseCaseService.md) (4 shared connections)
- [BaseUnitOfWork](BaseUnitOfWork.md) (4 shared connections)
- [TestVerifyUserRights](TestVerifyUserRights.md) (4 shared connections)
- [UploadCasesCommand](UploadCasesCommand.md) (3 shared connections)
- [CrudOperation](CrudOperation.md) (3 shared connections)
- [TestGetCaseDataCollections](TestGetCaseDataCollections.md) (3 shared connections)
- [CaseTypeAccessAbac](CaseTypeAccessAbac.md) (2 shared connections)

## Source Files

- `test/casedb/unit/services/case/upload/test_casedb_upload.py`

## Audit Trail

- EXTRACTED: 129 (98%)
- INFERRED: 2 (2%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*