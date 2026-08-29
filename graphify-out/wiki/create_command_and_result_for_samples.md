# .create_command_and_result_for_samples

> 50 nodes

## Key Concepts

- **.create_command_and_result_for_samples()** (67 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.create_seq_profile_for_upload()** (33 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **_verify_children_seq_profiles()** (30 connections) — `gen_epix/seqdb/services/seq/upload_verify_batch.py`
- **.get_only_allele_profile_result()** (26 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **TestVerifyChildrenSeqProfiles** (24 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.mock_existing_seq_profile_lookup()** (18 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.get_only_allele_profile()** (17 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_allele_profiles_exist_with_error_on_exists()** (9 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_content_hash_mismatch_with_seq_id_adds_natural_key_error()** (9 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_content_hash_mismatch_without_seq_id_adds_unknown_seq_error()** (9 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_existing_id_is_kept_when_already_matching()** (9 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_fallback_from_none_seq_id_can_resolve_existing_seq_profile()** (9 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_no_existing_seq_profiles_for_sample_is_noop()** (9 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_null_id_content_hash_with_seq_id_skips_mismatch_error()** (9 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_null_id_content_hash_without_seq_id_skips_mismatch_error()** (9 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_null_id_seq_id_does_not_use_fallback()** (9 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_sample_marked_new_is_ignored()** (9 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_seq_id_linked_to_other_sample_adds_error()** (9 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_skipped_seq_profile_result_is_ignored()** (9 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_temporary_seq_profile_id_is_replaced()** (9 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_concurrent_modification_does_not_raise()** (8 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_locus_code_map_code_sets_id()** (8 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_calculate_distances_false_skips_distance_calculation()** (7 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_locus_code_map_code_does_not_exist()** (7 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_locus_code_map_id_code_mismatch()** (7 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- *... and 25 more nodes in this community*

## Relationships

- [.create_sample_for_upload](create_sample_for_upload.md) (39 shared connections)
- [_verify_children_seq_classifications](_verify_children_seq_classifications.md) (15 shared connections)
- [.create_seq_for_upload](create_seq_for_upload.md) (13 shared connections)
- [test_seqdb_upload.py](test_seqdb_upload.py.md) (12 shared connections)
- [Seqdb Upload Unit Tests (Base Case)](Seqdb_Upload_Unit_Tests_Base_Case.md) (9 shared connections)
- [BaseUnitOfWork](BaseUnitOfWork.md) (8 shared connections)
- [commondb/domain/literal.py](commondb-domain-literal.py.md) (4 shared connections)
- [SeqProfileForUpload](SeqProfileForUpload.md) (3 shared connections)
- [entity.py](entity.py.md) (2 shared connections)
- [UuidSetFilter](UuidSetFilter.md) (1 shared connections)
- [seqdb/domain/model/__init__.py](seqdb-domain-model-__init__.py.md) (1 shared connections)
- [commondb/domain/enum.py](commondb-domain-enum.py.md) (1 shared connections)

## Source Files

- `gen_epix/seqdb/services/seq/upload_verify_batch.py`
- `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`

## Audit Trail

- EXTRACTED: 264 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*