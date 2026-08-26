# Sample Upload Tests

> 34 nodes · cohesion 0.08

## Key Concepts

- **._get_allele_profile_for_ids()** (29 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **TestModelSampleForUpload** (18 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **.test_seqs_serialization_structure()** (4 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **.test_valid_sample_without_id_seqs_with_null_ids()** (4 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **.test_valid_seqs_with_different_properties()** (4 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **.test_valid_seqs_with_own_sample_ids()** (4 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **.test_valid_with_multiple_seqs()** (4 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **.test_valid_with_sample_ids()** (4 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **.test_valid_with_seqs_and_identifiers()** (4 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **.test_valid_with_single_seq()** (4 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **.test_computed_field_has_seqs_false()** (3 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **.test_invalid_empty_sample_ids()** (3 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **.test_invalid_missing_sample_identification()** (3 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **.test_valid_with_both_sample_identifiers()** (3 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **.test_valid_with_empty_seqs_list()** (3 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **.test_valid_with_multiple_identifiers()** (3 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **.test_valid_with_optional_fields()** (3 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **.test_valid_with_sample_id()** (3 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **Test that seqs property maintains proper structure for serialization.** (1 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **Test SampleForUpload without id where seqs can have their own sample_ids.** (1 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **Test SampleForUpload without id where seqs also have NULL_ID sample_ids.** (1 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **Test has_seqs computed field returns False when no samples have seqs.** (1 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **Test valid SampleForUpload with sample_id.** (1 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **Test valid SampleForUpload with Identifiers.** (1 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **Test valid SampleForUpload with both sample_id and sample_ids.** (1 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- *... and 9 more nodes in this community*

## Relationships

- [Sample Batch Upload Tests](Sample_Batch_Upload_Tests.md) (8 shared connections)
- [SeqForUpload Model Tests](SeqForUpload_Model_Tests.md) (7 shared connections)
- [Allele Profile Upload Tests](Allele_Profile_Upload_Tests.md) (3 shared connections)
- [Commondb Upload Test Suite](Commondb_Upload_Test_Suite.md) (2 shared connections)
- [SeqForUpload Test Helpers](SeqForUpload_Test_Helpers.md) (2 shared connections)
- [Allele Upload Model Tests](Allele_Upload_Model_Tests.md) (1 shared connections)
- [BaseSeq Model Tests](BaseSeq_Model_Tests.md) (1 shared connections)
- [Identifiers Validation Mixin](Identifiers_Validation_Mixin.md) (1 shared connections)

## Source Files

- `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`

## Audit Trail

- EXTRACTED: 72 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*