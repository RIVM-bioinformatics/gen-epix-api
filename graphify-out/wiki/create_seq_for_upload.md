# .create_seq_for_upload

> 32 nodes

## Key Concepts

- **.create_seq_for_upload()** (20 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **_verify_children_seqs()** (19 connections) — `gen_epix/seqdb/services/seq/upload_verify_batch.py`
- **.get_only_seq_result()** (15 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **TestVerifyChildrenSeqs** (14 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.get_only_seq()** (12 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.mock_existing_seq_lookup()** (12 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_temporary_seq_id_is_replaced_and_child_links_are_rewritten()** (11 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_existing_id_is_kept_when_already_matching()** (9 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_fallback_from_none_read_sets_can_resolve_existing_seq()** (9 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_hash_mismatch_with_read_sets_adds_natural_key_error()** (9 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_hash_mismatch_without_read_sets_adds_unknown_read_set_error()** (9 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_no_existing_seqs_for_sample_is_noop()** (9 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_read_set_linked_to_other_sample_adds_error()** (9 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_sample_marked_new_is_ignored()** (9 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_skipped_seq_result_is_ignored()** (9 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_invalid_seq_protocol_type_adds_error()** (7 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **SeqForUpload** (4 connections)
- **A pre-skipped seq result should not be re-validated.** (3 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_read_set2_only_does_not_use_fallback()** (2 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **Test the _verify_children_seqs function.** (2 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **Verify Seq specific rules: 1. Replace protocol code by ID when only code is…** (1 connections) — `gen_epix/seqdb/services/seq/upload_verify_batch.py`
- **Helper to create a SeqForUpload with default or specified properties.** (1 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **A non-ASSEMBLY protocol for Seq should be flagged with code a4c9e18b.** (1 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **When sample is new, seq conflict checks are skipped.** (1 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **No matching seq rows means function leaves the seq untouched.** (1 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- *... and 7 more nodes in this community*

## Relationships

- [test_seqdb_upload.py](test_seqdb_upload.py.md) (13 shared connections)
- [.create_command_and_result_for_samples](create_command_and_result_for_samples.md) (13 shared connections)
- [.create_sample_for_upload](create_sample_for_upload.md) (11 shared connections)
- [Seqdb Upload Unit Tests (Base Case)](Seqdb_Upload_Unit_Tests_Base_Case.md) (7 shared connections)
- [BaseUnitOfWork](BaseUnitOfWork.md) (5 shared connections)
- [commondb/domain/literal.py](commondb-domain-literal.py.md) (3 shared connections)
- [_verify_children_seq_classifications](_verify_children_seq_classifications.md) (2 shared connections)
- [UuidSetFilter](UuidSetFilter.md) (1 shared connections)
- [Seq Domain Model](Seq_Domain_Model.md) (1 shared connections)
- [entity.py](entity.py.md) (1 shared connections)

## Source Files

- `gen_epix/seqdb/services/seq/upload_verify_batch.py`
- `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`

## Audit Trail

- EXTRACTED: 131 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*