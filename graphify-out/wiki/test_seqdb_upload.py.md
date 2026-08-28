# test_seqdb_upload.py

> 23 nodes

## Key Concepts

- **test_seqdb_upload.py** (40 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **_verify_protocol()** (17 connections) — `gen_epix/seqdb/services/seq/upload_verify_batch.py`
- **TestVerifyProtocol** (10 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_invalid_type_on_skipped_child_does_not_add_child_error()** (7 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_valid_seq_protocol_type_succeeds_without_errors()** (7 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **scenario_ids** (7 connections)
- **TestConcurrentModificationError** (6 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_no_protocol_ids_returns_verify_link_result()** (6 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_unsupported_child_model_class_raises_not_implemented()** (6 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_user_none_is_forwarded_to_protocol_read()** (6 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **create_allele_profile_base64()** (3 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **Model** (1 connections)
- **Verify that protocols provided by ID or code exist, and resolve codes to IDs.** (1 connections) — `gen_epix/seqdb/services/seq/upload_verify_batch.py`
- **Unit tests for seqdb sample upload functionality. Tests the…** (1 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **# TODO: replace with actual log code rather than log message** (1 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **Test that ConcurrentModificationError in distance calculation is a soft failure.** (1 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **Create a valid allele profile with base64-encoded concatenated UUIDs.** (1 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **Test the _verify_protocol helper.** (1 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **When no protocol IDs are present, no protocol-type query is needed.** (1 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **A protocol with ASSEMBLY type is accepted for Seq children.** (1 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **Skipped children are ignored for per-child error annotation.** (1 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **Protocol lookup should use user_id=None when command user is None.** (1 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **Mapped but unsupported child classes should raise NotImplementedError.** (1 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`

## Relationships

- [.create_seq_for_upload](create_seq_for_upload.md) (13 shared connections)
- [.create_command_and_result_for_samples](create_command_and_result_for_samples.md) (12 shared connections)
- [BaseUnitOfWork](BaseUnitOfWork.md) (10 shared connections)
- [.create_sample_for_upload](create_sample_for_upload.md) (8 shared connections)
- [_verify_children_seq_classifications](_verify_children_seq_classifications.md) (6 shared connections)
- [Seqdb Upload Unit Tests (Base Case)](Seqdb_Upload_Unit_Tests_Base_Case.md) (4 shared connections)
- [commondb/domain/literal.py](commondb-domain-literal.py.md) (4 shared connections)
- [commondb/domain/enum.py](commondb-domain-enum.py.md) (4 shared connections)
- [seqdb/domain/enum.py](seqdb-domain-enum.py.md) (2 shared connections)
- [CrudOperation](CrudOperation.md) (2 shared connections)
- [ParentUploadResult](ParentUploadResult.md) (1 shared connections)
- [App](App.md) (1 shared connections)

## Source Files

- `gen_epix/seqdb/services/seq/upload_verify_batch.py`
- `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`

## Audit Trail

- EXTRACTED: 99 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*