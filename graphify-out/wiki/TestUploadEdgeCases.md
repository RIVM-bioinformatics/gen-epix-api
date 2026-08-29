# TestUploadEdgeCases

> 10 nodes

## Key Concepts

- **TestUploadEdgeCases** (8 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_existing_identifiers_with_different_internal_ids_fail()** (7 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_verify_link_id_same_service_allows_none_user()** (6 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_inconsistent_child_parent_ids_fail()** (5 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_create_identifiers_skips_null_id_internal_id()** (4 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **Focused edge-case tests for upload consistency and null semantics.** (1 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **Multiple existing identifiers for one parent must resolve to one internal ID.** (1 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **Same-service link verification should support user=None without crashing.** (1 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **Different non-null parent IDs across children in one parent should fail.** (1 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **NULL_ID internal_id should be treated as unresolved and skipped.** (1 connections) — `test/commondb/unit/upload/test_commondb_upload.py`

## Relationships

- [.create_parent_for_upload](create_parent_for_upload.md) (4 shared connections)
- [.create_child1_for_upload](create_child1_for_upload.md) (4 shared connections)
- [test_commondb_upload.py](test_commondb_upload.py.md) (3 shared connections)
- [Commondb Upload Unit Tests (Base Case)](Commondb_Upload_Unit_Tests_Base_Case.md) (2 shared connections)
- [.create_child2_for_upload](create_child2_for_upload.md) (2 shared connections)
- [BaseUnitOfWork](BaseUnitOfWork.md) (1 shared connections)
- [Test6Identifiers](Test6Identifiers.md) (1 shared connections)

## Source Files

- `test/commondb/unit/upload/test_commondb_upload.py`

## Audit Trail

- EXTRACTED: 26 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*