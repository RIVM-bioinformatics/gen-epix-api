# Data Collection ID Handling

> 6 nodes · cohesion 0.33

## Key Concepts

- **TestCaseDataCollectionIdHandling** (6 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_batch_with_multiple_different_data_collection_ids()** (4 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_new_case_with_explicit_data_collection_id()** (4 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **Batch can contain cases from different DCs.** (1 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **Tests for handling cases with different created_in_data_collection_id values.** (1 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **New case with explicit DC ID should use that DC for ABAC.** (1 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`

## Relationships

- [Case Upload ABAC Tests](Case_Upload_ABAC_Tests.md) (4 shared connections)
- [Case Upload Tests](Case_Upload_Tests.md) (3 shared connections)

## Source Files

- `test/casedb/unit/services/case/upload/test_casedb_upload.py`

## Audit Trail

- EXTRACTED: 12 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*