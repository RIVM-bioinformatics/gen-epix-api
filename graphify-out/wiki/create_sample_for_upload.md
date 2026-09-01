# .create_sample_for_upload

> 32 nodes

## Key Concepts

- **.create_sample_for_upload()** (67 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **_verify_sample_refdata()** (24 connections) — `gen_epix/seqdb/services/seq/upload_verify_batch.py`
- **TestVerifyReferenceData** (17 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_verify_refdata_allele_profile_length_mismatch()** (7 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_verify_refdata_skipped_samples_ignored()** (7 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_locus_allele_id_map_encoded_in_locus_set_order()** (6 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_verify_refdata_extra_alleles_warning()** (6 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_verify_refdata_missing_new_alleles()** (6 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_verify_refdata_multiple_samples_no_profiles()** (5 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_verify_refdata_no_allele_profiles()** (5 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_verify_refdata_successful_allele_profiles()** (5 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_verify_refdata_with_empty_allele_profiles_list()** (5 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_verify_refdata_empty_batch_alternative()** (4 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_verify_refdata_empty_samples()** (3 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_verify_refdata_allele_profile_format_not_implemented()** (2 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.test_verify_refdata_assertion_error_no_allele_data()** (2 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **Test that _verify_batch_sample_refdata succeeds with empty samples.** (2 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **SeqTaxonomy** (1 connections)
- **Verify and complete reference data.** (1 connections) — `gen_epix/seqdb/services/seq/upload_verify_batch.py`
- **Test the _verify_batch_sample_refdata function.** (1 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **Test successful verification when no allele profiles are provided.** (1 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **Test that _verify_refdata fails when new alleles are missing from batch.** (1 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **Helper to create a SampleForUpload with default or specified properties.** (1 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **Test that _verify_refdata gives warning for superfluous alleles in batch.** (1 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **Test that _verify_refdata ignores samples with FAILED/SKIPPED status.** (1 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- *... and 7 more nodes in this community*

## Relationships

- [.create_command_and_result_for_samples](create_command_and_result_for_samples.md) (39 shared connections)
- [_verify_children_seq_classifications](_verify_children_seq_classifications.md) (12 shared connections)
- [.create_seq_for_upload](create_seq_for_upload.md) (11 shared connections)
- [test_seqdb_upload.py](test_seqdb_upload.py.md) (8 shared connections)
- [commondb/domain/literal.py](commondb-domain-literal.py.md) (6 shared connections)
- [BaseUnitOfWork](BaseUnitOfWork.md) (5 shared connections)
- [Seqdb Upload Unit Tests (Base Case)](Seqdb_Upload_Unit_Tests_Base_Case.md) (4 shared connections)
- [SeqProfileForUpload](SeqProfileForUpload.md) (2 shared connections)
- [entity.py](entity.py.md) (1 shared connections)

## Source Files

- `gen_epix/seqdb/services/seq/upload_verify_batch.py`
- `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`

## Audit Trail

- EXTRACTED: 138 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*