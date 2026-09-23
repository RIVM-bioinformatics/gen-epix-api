# Parent Upload Edge Cases

> 36 nodes · cohesion 0.09

## Key Concepts

- **.create_child1_for_upload()** (23 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **TestDuplicateIds** (18 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.create_command_for_parents()** (13 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **ParentForUpload** (12 connections) — `test/commondb/unit/upload/model.py`
- **UUID** (12 connections)
- **UploadParentsCommand** (10 connections) — `test/commondb/unit/upload/model.py`
- **._make_parent()** (9 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **._verify_only_cmd()** (8 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **._make_child_parent_id_mismatch_cmd()** (8 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **._make_child1()** (7 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_verify_link_id_same_service_allows_none_user()** (6 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_duplicate_child_across_two_parents_both_parents_failed()** (5 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_duplicate_child_within_one_parent_parent_failed()** (5 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_non_duplicate_batch_unaffected()** (5 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_reads_distinct_ids_and_returns_child_parent_mapping()** (5 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_returns_empty_and_skips_query_when_no_linked_ids()** (5 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_uses_none_user_id_when_command_has_no_user()** (5 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_inconsistent_child_parent_ids_fail()** (5 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_duplicate_parent_ids_both_failed_other_unaffected()** (4 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_child_failure_propagates_to_parent_status()** (4 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **Same-service link verification should support user=None without crashing.** (1 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **Different non-null parent IDs across children in one parent should fail.** (1 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **Duplicate-ID detection converts per-item hard failures into soft FAILED results.** (1 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **Construct a Child1ForUpload bypassing Pydantic validators (for dup-ID tests).** (1 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **Construct a ParentForUpload bypassing Pydantic validators.** (1 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- *... and 11 more nodes in this community*

## Relationships

- [Parent-Child Upload Models](Parent-Child_Upload_Models.md) (30 shared connections)
- [Parent Identifier Upload Tests](Parent_Identifier_Upload_Tests.md) (13 shared connections)
- [Upload Field Mutability Tests](Upload_Field_Mutability_Tests.md) (12 shared connections)
- [Reference Data Resolution Tests](Reference_Data_Resolution_Tests.md) (7 shared connections)
- [Child Identifier Upload Tests](Child_Identifier_Upload_Tests.md) (7 shared connections)
- [Sample Batch Upload](Sample_Batch_Upload.md) (3 shared connections)
- [Child Model Order Derivation](Child_Model_Order_Derivation.md) (1 shared connections)
- [Batch Upload Tests](Batch_Upload_Tests.md) (1 shared connections)
- [Sequence Sample Upload Models](Sequence_Sample_Upload_Models.md) (1 shared connections)

## Source Files

- `test/commondb/unit/upload/model.py`
- `test/commondb/unit/upload/test_commondb_upload.py`

## Audit Trail

- EXTRACTED: 119 (92%)
- INFERRED: 11 (8%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*