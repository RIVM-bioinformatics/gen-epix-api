# .create_child2_for_upload

> 30 nodes · cohesion 0.12

## Key Concepts

- **.create_child2_for_upload()** (27 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.create_identifier_for_upload()** (27 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **Test9Child2Identifiers** (16 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.get_child2_identifier_from_for_upload()** (10 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_9_2_1_1_existing_identifier_null_child2_sets_id()** (10 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_9_2_1_2_1_existing_identifier_same_child2_succeeds()** (10 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_9_2_3_1_multiple_identifiers_some_existing_same_child2()** (10 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_9_2_1_2_2_existing_identifier_different_child2_fails()** (9 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_9_2_3_1_multiple_identifiers_some_existing_different_child2()** (9 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_9_2_2_new_identifier_new_child2()** (8 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_9_2_3_2_multiple_identifiers_all_new_different_issuer()** (8 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_9_3_1_identifier_issuer_id_not_found()** (8 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_9_3_2_identifier_issuer_code_not_found()** (8 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_9_3_3_identifier_issuer_id_and_code_mismatch()** (8 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_9_2_3_2_multiple_identifiers_all_new_same_issuer()** (4 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **Test scenarios related to Identifiers for Child2 objects.** (1 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **Test 9.2.1.1: Existing Identifier with NULL child2 ID - should set child2 ID.** (1 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **Test 9.2.1.2.1: Existing Identifier with same child2 ID - should succeed.** (1 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **Test 9.2.1.2.2: Existing Identifier with different child2 ID - should fail.** (1 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **Test 9.2.2: New Identifier for new child2 - should succeed.** (1 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **Test 9.2.3.1: Multiple Identifiers, some existing for same child2 - should…** (1 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **Test 9.2.3.1: Multiple Identifiers, some existing for different child2 - should…** (1 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **Test 9.2.3.2: Multiple Identifiers all new but same issuer - should fail.** (1 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **Test 9.2.3.2: Multiple Identifiers all new and different issuer - should…** (1 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **Test 9.3.1: Identifier issuer ID (any except NULL_ID) provided and not found -…** (1 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- *... and 5 more nodes in this community*

## Relationships

- [.create_parent_for_upload](create_parent_for_upload.md) (42 shared connections)
- [.create_child1_for_upload](create_child1_for_upload.md) (11 shared connections)
- [test_commondb_upload.py](test_commondb_upload.py.md) (9 shared connections)
- [UUID](UUID.md) (5 shared connections)
- [BaseUploadTestCase](BaseUploadTestCase.md) (5 shared connections)
- [Test6Identifiers](Test6Identifiers.md) (4 shared connections)
- [IdentifierForUpload](IdentifierForUpload.md) (3 shared connections)
- [TestUploadEdgeCases](TestUploadEdgeCases.md) (2 shared connections)

## Source Files

- `test/commondb/unit/upload/test_commondb_upload.py`

## Audit Trail

- EXTRACTED: 134 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*