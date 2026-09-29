# Case Upload Tests

> 35 nodes · cohesion 0.10

## Key Concepts

- **test_casedb_upload.py** (50 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **BaseUploadTestCase** (36 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **scenario_ids** (18 connections)
- **.create_uploader()** (9 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **TestExistingContentKeyNormalization** (8 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **TestGetCaseDataCollections** (8 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **TestCaseForUploadContentSerialization** (6 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **._run_upsert_with_existing_key()** (6 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **TestUpsertBatchContentDeletionDelta** (6 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.create_org_user()** (5 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **TestCaseServiceUploadCasesFeatureFlag** (5 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **TestUpsertBatchCaseDate** (5 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_calculated_timed_at_preserved_for_existing_case()** (5 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **_to_casedb_role_set()** (5 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_upload_cases_delegates_when_upload_feature_enabled()** (4 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_upload_cases_raises_when_upload_feature_disabled()** (4 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_content_deletion_delta_is_restored_before_generic_upsert()** (4 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.setup_method()** (3 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **_mock_uow()** (3 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **TestCaseDateMutability** (3 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_case_for_upload_preserves_none_content_value()** (2 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_plain_case_also_serializes_none_content_value()** (2 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_string_keys_from_sql_repo_are_converted_to_uuid()** (2 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_uuid_keys_from_dict_repo_are_accepted()** (2 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_case_without_case_object_falls_back_to_null_id()** (2 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- *... and 10 more nodes in this community*

## Relationships

- [Case Upload ABAC Tests](Case_Upload_ABAC_Tests.md) (16 shared connections)
- [Case Data Collection Updates](Case_Data_Collection_Updates.md) (15 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (14 shared connections)
- [Casedb-Seqdb Upload Bridge](Casedb-Seqdb_Upload_Bridge.md) (12 shared connections)
- [Sample Batch Upload](Sample_Batch_Upload.md) (7 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (5 shared connections)
- [Case Content Upsert Tests](Case_Content_Upsert_Tests.md) (5 shared connections)
- [Role Generation & Hierarchy](Role_Generation_&_Hierarchy.md) (3 shared connections)
- [SQLAlchemy Case Repository](SQLAlchemy_Case_Repository.md) (3 shared connections)
- [Case Upload RBAC Tests](Case_Upload_RBAC_Tests.md) (3 shared connections)
- [Default Data Collection Tests](Default_Data_Collection_Tests.md) (3 shared connections)
- [Data Collection ID Handling](Data_Collection_ID_Handling.md) (3 shared connections)

## Source Files

- `test/casedb/unit/services/case/upload/test_casedb_upload.py`

## Audit Trail

- EXTRACTED: 143 (92%)
- INFERRED: 13 (8%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*