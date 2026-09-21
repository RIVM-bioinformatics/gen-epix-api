# Upload Field Mutability Tests

> 64 nodes · cohesion 0.07

## Key Concepts

- **.create_parent_for_upload()** (73 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.expectStatusCount()** (60 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.expectBatchProcessed()** (45 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.get_parent_from_for_upload()** (21 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **Test5FieldMutability** (15 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **Test6Identifiers** (13 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_4_2_2_child_parent_id_matches_succeeds()** (9 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_6_2_1_1_existing_identifier_null_parent_sets_id()** (9 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_6_2_1_2_1_existing_identifier_same_parent_succeeds()** (9 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_6_2_3_1_multiple_identifiers_some_existing_same_parent()** (9 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_update_existing_parent_with_new_children()** (9 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_2_3_parent_with_child2_only()** (8 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_3_4_2_child2_no_id_or_code_succeeds()** (7 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_5_1_1_always_mutable_single_value_field()** (7 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_5_1_2_always_mutable_list_field()** (7 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_5_1_3_1_always_mutable_dict_add_new_key()** (7 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_5_1_3_2_always_mutable_dict_new_key_none_value()** (7 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_5_1_3_3_always_mutable_dict_update_existing_key()** (7 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_5_1_3_4_always_mutable_dict_remove_existing_key()** (7 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_5_2_2_mutable_if_empty_stored_not_empty_new_empty()** (7 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_5_2_3_mutable_if_empty_stored_not_empty_new_not_empty_fails()** (7 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_5_2_4_immutable_uuid_null_id_treated_as_not_specified()** (7 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_6_2_3_2_multiple_identifiers_all_new_different_issuer()** (7 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_7_3_on_exists_update_with_existing_object_updates()** (7 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_1_1_parent_id_not_provided_creates_new_object()** (6 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- *... and 39 more nodes in this community*

## Relationships

- [Parent Identifier Upload Tests](Parent_Identifier_Upload_Tests.md) (66 shared connections)
- [Child Identifier Upload Tests](Child_Identifier_Upload_Tests.md) (38 shared connections)
- [Parent-Child Upload Models](Parent-Child_Upload_Models.md) (25 shared connections)
- [Reference Data Resolution Tests](Reference_Data_Resolution_Tests.md) (17 shared connections)
- [Parent Upload Edge Cases](Parent_Upload_Edge_Cases.md) (12 shared connections)
- [Batch Upload Tests](Batch_Upload_Tests.md) (6 shared connections)
- [Upload Identifier Models](Upload_Identifier_Models.md) (2 shared connections)
- [ETL Batch Result Models](ETL_Batch_Result_Models.md) (1 shared connections)
- [Case Upload Results](Case_Upload_Results.md) (1 shared connections)

## Source Files

- `test/commondb/unit/upload/test_commondb_upload.py`

## Audit Trail

- EXTRACTED: 307 (100%)
- INFERRED: 1 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*