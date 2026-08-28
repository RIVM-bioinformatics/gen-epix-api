# _verify_children_seq_classifications

> 39 nodes · cohesion 0.13

## Key Concepts

- **_verify_children_seq_classifications()** (22 connections) — `gen_epix/seqdb/services/seq/upload_verify_batch.py`
- **.create_seq_classification_for_upload()** (19 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **TestVerifyChildrenSeqClassifications** (15 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.get_only_seq_classification()** (14 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.get_only_seq_classification_result()** (14 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.mock_existing_seq_classification_lookup()** (14 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **._run()** (10 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_existing_id_is_kept_when_already_matching()** (9 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_fallback_from_none_seq_id_can_resolve_existing_seq_classification()** (9 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_no_existing_seq_classifications_for_sample_is_noop()** (9 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_null_id_seq_id_does_not_use_fallback()** (9 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_null_id_seq_id_with_primary_category_mismatch_adds_error()** (9 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_primary_category_mismatch_with_seq_id_adds_natural_key_error()** (9 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_primary_category_mismatch_without_seq_id_adds_unknown_seq_error()** (9 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_sample_marked_new_is_ignored()** (9 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_seq_id_linked_to_other_sample_adds_error()** (9 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_skipped_seq_classification_result_is_ignored()** (9 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_temporary_seq_classification_id_is_replaced()** (9 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **TestVerifyBatchSeqClassifications** (8 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_primary_category_code_not_found()** (4 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_primary_category_code_resolves_to_id()** (4 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_primary_category_id_not_found()** (4 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **A seq_id tied to another sample should fail validation.** (2 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **When id already matches DB id, no replacement info is logged.** (2 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **Current behavior: fallback is gated by seq_id != NULL_ID.** (2 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- *... and 14 more nodes in this community*

## Relationships

- [.create_command_and_result_for_samples](create_command_and_result_for_samples.md) (15 shared connections)
- [.create_sample_for_upload](create_sample_for_upload.md) (12 shared connections)
- [BaseUploadTestCase](BaseUploadTestCase.md) (8 shared connections)
- [test_seqdb_upload.py](test_seqdb_upload.py.md) (6 shared connections)
- [BaseUnitOfWork](BaseUnitOfWork.md) (5 shared connections)
- [commondb/domain/literal.py](commondb-domain-literal.py.md) (4 shared connections)
- [SeqProfileForUpload](SeqProfileForUpload.md) (4 shared connections)
- [.create_seq_for_upload](create_seq_for_upload.md) (2 shared connections)
- [UuidSetFilter](UuidSetFilter.md) (1 shared connections)
- [entity.py](entity.py.md) (1 shared connections)
- [TestNumpyAlleleIntegration](TestNumpyAlleleIntegration.md) (1 shared connections)

## Source Files

- `gen_epix/seqdb/services/seq/upload_verify_batch.py`
- `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`

## Audit Trail

- EXTRACTED: 152 (99%)
- INFERRED: 1 (1%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*