# Parent Identifier Upload Tests

> 37 nodes · cohesion 0.08

## Key Concepts

- **.upload_batch()** (68 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.expectBatchFailed()** (19 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.get_parent_identifier_from_for_upload()** (12 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **Test3ReferenceDataLinks** (12 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_6_2_1_2_2_existing_identifier_different_parent_fails()** (9 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_3_1_2_ref_id_provided_and_found_succeeds()** (8 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_3_2_2_ref_code_provided_and_found_sets_id()** (8 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_3_3_1_ref_id_and_code_mismatch_fails()** (8 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_3_3_2_ref_id_and_code_match_succeeds()** (8 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_4_2_1_child_parent_id_parent_not_exists_fails()** (8 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_6_2_2_new_identifier_new_parent()** (8 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_6_2_3_1_multiple_identifiers_some_existing_different_parent()** (8 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_3_1_1_ref_id_provided_not_found_fails()** (7 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_3_2_1_ref_code_provided_not_found_fails()** (7 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_3_4_1_child2_null_id_no_code_provided_fails()** (7 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_existing_identifiers_with_different_internal_ids_fail()** (7 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_7_1_on_exists_error_with_existing_object_fails()** (6 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_7_6_on_new_error_with_new_id_fails()** (6 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_dry_run_and_real_run_report_same_failure()** (5 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **Test 6.2.1.2.2: Existing Identifier with different parent ID - should fail.** (1 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **Test 6.2.2: New Identifier for new parent - should succeed.** (1 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **Test 6.2.3.1: Multiple Identifiers, some existing for different parent - should…** (1 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **Test 7.1: on_exists=ERROR with existing object - should fail.** (1 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **Test 7.6: on_new=ERROR with new object having provided ID - should fail.** (1 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **Multiple existing identifiers for one parent must resolve to one internal ID.** (1 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- *... and 12 more nodes in this community*

## Relationships

- [Upload Field Mutability Tests](Upload_Field_Mutability_Tests.md) (66 shared connections)
- [Child Identifier Upload Tests](Child_Identifier_Upload_Tests.md) (22 shared connections)
- [Parent-Child Upload Models](Parent-Child_Upload_Models.md) (13 shared connections)
- [Parent Upload Edge Cases](Parent_Upload_Edge_Cases.md) (13 shared connections)
- [Reference Data Resolution Tests](Reference_Data_Resolution_Tests.md) (10 shared connections)
- [Batch Upload Tests](Batch_Upload_Tests.md) (2 shared connections)
- [ETL Batch Result Models](ETL_Batch_Result_Models.md) (1 shared connections)
- [Upload Identifier Models](Upload_Identifier_Models.md) (1 shared connections)
- [Sample Batch Upload](Sample_Batch_Upload.md) (1 shared connections)

## Source Files

- `test/commondb/unit/upload/test_commondb_upload.py`

## Audit Trail

- EXTRACTED: 184 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*