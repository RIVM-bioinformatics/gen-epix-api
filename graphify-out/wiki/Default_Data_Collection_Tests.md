# Default Data Collection Tests

> 8 nodes · cohesion 0.25

## Key Concepts

- **TestSetDefaultCreatedInDataCollectionId** (7 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_error_when_no_default_and_case_needs_one()** (4 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_existing_case_created_in_dc_id_preserved()** (4 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_new_case_with_explicit_created_in_dc_id_unchanged()** (4 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **Tests for default_created_in_data_collection_id behavior. NOTE: Direct unit…** (1 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **When new case has NULL_ID and no default, should add error.** (1 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **When case explicitly sets created_in_data_collection_id, don't override.** (1 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **Existing cases should not be modified by default setting.** (1 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`

## Relationships

- [Case Upload Feature Tests](Case_Upload_Feature_Tests.md) (6 shared connections)
- [Case Upload Tests](Case_Upload_Tests.md) (2 shared connections)
- [Case Upload Bridge Tests](Case_Upload_Bridge_Tests.md) (1 shared connections)

## Source Files

- `test/casedb/unit/services/case/upload/test_casedb_upload.py`

## Audit Trail

- EXTRACTED: 16 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*