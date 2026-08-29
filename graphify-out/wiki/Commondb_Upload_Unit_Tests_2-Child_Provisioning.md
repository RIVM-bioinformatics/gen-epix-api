# Commondb Upload Unit Tests (2-Child Provisioning)

> 11 nodes

## Key Concepts

- **UUID** (12 connections)
- **.test_2_4_parent_with_both_children()** (10 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **Test2ChildObjectProvision** (8 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_2_2_parent_with_child1_only()** (8 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_2_3_parent_with_child2_only()** (8 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.create_ref2()** (6 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **Create a test Ref2 object.** (1 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **Test scenarios related to providing different combinations of child objects.** (1 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **Test 2.2: Parent with Child1 objects only.** (1 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **Test 2.3: Parent with Child2 objects only.** (1 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **Test 2.4: Parent with both Child1 and Child2 objects.** (1 connections) — `test/commondb/unit/upload/test_commondb_upload.py`

## Relationships

- [.create_parent_for_upload](create_parent_for_upload.md) (15 shared connections)
- [.create_child1_for_upload](create_child1_for_upload.md) (6 shared connections)
- [.create_child2_for_upload](create_child2_for_upload.md) (5 shared connections)
- [Commondb Upload Unit Tests (Base Case)](Commondb_Upload_Unit_Tests_Base_Case.md) (3 shared connections)
- [test_commondb_upload.py](test_commondb_upload.py.md) (3 shared connections)
- [TestDuplicateIds](TestDuplicateIds.md) (2 shared connections)
- [Test6Identifiers](Test6Identifiers.md) (1 shared connections)

## Source Files

- `test/commondb/unit/upload/test_commondb_upload.py`

## Audit Trail

- EXTRACTED: 46 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*