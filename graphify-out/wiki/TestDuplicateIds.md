# TestDuplicateIds

> 17 nodes

## Key Concepts

- **TestDuplicateIds** (11 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **._make_parent()** (10 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **._verify_only_cmd()** (8 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **._make_child1()** (7 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **ParentForUpload** (6 connections)
- **.test_duplicate_child_across_two_parents_both_parents_failed()** (5 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_duplicate_child_within_one_parent_parent_failed()** (5 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_non_duplicate_batch_unaffected()** (5 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_duplicate_parent_ids_both_failed_other_unaffected()** (4 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **Duplicate-ID detection converts per-item hard failures into soft FAILED results.** (1 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **Construct a Child1ForUpload bypassing Pydantic validators (for dup-ID tests).** (1 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **Construct a ParentForUpload bypassing Pydantic validators.** (1 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **Build an UploadParentsCommand bypassing all Pydantic batch validators.** (1 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **Duplicate parent UUID → both occurrences FAILED, distinct parent unaffected.** (1 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **Two children with the same UUID inside one parent → parent FAILED.** (1 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **Same child UUID in two distinct parents → both parents FAILED, message names…** (1 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **Batch with fully distinct IDs produces no FAILED results and no duplicate codes.** (1 connections) — `test/commondb/unit/upload/test_commondb_upload.py`

## Relationships

- [test_commondb_upload.py](test_commondb_upload.py.md) (5 shared connections)
- [.create_parent_for_upload](create_parent_for_upload.md) (4 shared connections)
- [Commondb Upload Unit Tests (Base Case)](Commondb_Upload_Unit_Tests_Base_Case.md) (2 shared connections)
- [Commondb Upload Unit Tests (2-Child Provisioning)](Commondb_Upload_Unit_Tests_2-Child_Provisioning.md) (2 shared connections)

## Source Files

- `test/commondb/unit/upload/test_commondb_upload.py`

## Audit Trail

- EXTRACTED: 41 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*