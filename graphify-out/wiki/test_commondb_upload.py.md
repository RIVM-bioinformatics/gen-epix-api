# test_commondb_upload.py

> 46 nodes · cohesion 0.07

## Key Concepts

- **test_commondb_upload.py** (53 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **upload/model.py** (29 connections) — `test/commondb/unit/upload/model.py`
- **.create_command_for_parents()** (13 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **Child1ForUpload** (8 connections) — `test/commondb/unit/upload/model.py`
- **._make_child_parent_id_mismatch_cmd()** (8 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **ParentBatchUploader** (7 connections) — `test/commondb/unit/upload/model.py`
- **UploadParentsCommand** (7 connections) — `test/commondb/unit/upload/model.py`
- **TestRetrieveParentIdByIntraChildLinkedId** (7 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **TestVerificationAttributionAndDryRun** (7 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **Child2** (6 connections) — `test/commondb/unit/upload/model.py`
- **Child2ForUpload** (5 connections) — `test/commondb/unit/upload/model.py`
- **.verify_refdata()** (5 connections) — `test/commondb/unit/upload/model.py`
- **ParentBatchUploadResult** (5 connections) — `test/commondb/unit/upload/model.py`
- **.test_reads_distinct_ids_and_returns_child_parent_mapping()** (5 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_returns_empty_and_skips_query_when_no_linked_ids()** (5 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **.test_uses_none_user_id_when_command_has_no_user()** (5 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **._validate_ref1_fields()** (4 connections) — `test/commondb/unit/upload/model.py`
- **.test_child_failure_propagates_to_parent_status()** (4 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **Child2Identifier** (3 connections) — `test/commondb/unit/upload/model.py`
- **ParentBatchForUpload** (3 connections) — `test/commondb/unit/upload/model.py`
- **ParentIdentifier** (3 connections) — `test/commondb/unit/upload/model.py`
- **Ref1** (3 connections) — `test/commondb/unit/upload/model.py`
- **Ref2** (3 connections) — `test/commondb/unit/upload/model.py`
- **.test_resolve_status_reports_failed_when_any_descendant_failed()** (3 connections) — `test/commondb/unit/upload/test_commondb_upload.py`
- **Child1** (2 connections) — `test/commondb/unit/upload/model.py`
- *... and 21 more nodes in this community*

## Relationships

- [.create_parent_for_upload](create_parent_for_upload.md) (14 shared connections)
- [BaseUnitOfWork](BaseUnitOfWork.md) (10 shared connections)
- [.create_child2_for_upload](create_child2_for_upload.md) (9 shared connections)
- [BaseUploadTestCase](BaseUploadTestCase.md) (9 shared connections)
- [.create_child1_for_upload](create_child1_for_upload.md) (7 shared connections)
- [CrudOperation](CrudOperation.md) (6 shared connections)
- [commondb/domain/enum.py](commondb-domain-enum.py.md) (6 shared connections)
- [TestDuplicateIds](TestDuplicateIds.md) (5 shared connections)
- [BaseService](BaseService.md) (3 shared connections)
- [UUID](UUID.md) (3 shared connections)
- [TestUploadEdgeCases](TestUploadEdgeCases.md) (3 shared connections)
- [commondb/domain/literal.py](commondb-domain-literal.py.md) (2 shared connections)

## Source Files

- `test/commondb/unit/upload/model.py`
- `test/commondb/unit/upload/test_commondb_upload.py`

## Audit Trail

- EXTRACTED: 157 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*