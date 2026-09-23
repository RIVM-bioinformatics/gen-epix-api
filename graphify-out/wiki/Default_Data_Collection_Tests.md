# Default Data Collection Tests

> 8 nodes · cohesion 0.25

## Key Concepts

- **TestSetDefaultCreatedInDataCollectionId** (8 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_error_when_no_default_and_case_needs_one()** (4 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_existing_case_created_in_dc_id_preserved()** (4 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_new_case_with_explicit_created_in_dc_id_unchanged()** (4 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **Tests for default_created_in_data_collection_id behavior. NOTE: Direct unit…** (1 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **When new case has NULL_ID and no default, should add error.** (1 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **When case explicitly sets created_in_data_collection_id, don't override.** (1 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **Existing cases should not be modified by default setting.** (1 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`

## Relationships

- [Case Upload ABAC Tests](Case_Upload_ABAC_Tests.md) (6 shared connections)
- [Case Upload Tests](Case_Upload_Tests.md) (3 shared connections)
- [Sample Batch Upload](Sample_Batch_Upload.md) (1 shared connections)

## Source Files

- `test/casedb/unit/services/case/upload/test_casedb_upload.py`

## Audit Trail

- EXTRACTED: 16 (94%)
- INFERRED: 1 (6%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*