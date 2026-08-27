# Sample Batch Upload Tests

> 28 nodes · cohesion 0.08

## Key Concepts

- **TestModelSampleBatchForUpload** (18 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **._create_sample_with_seqs()** (12 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **.test_samples_with_seqs_validation_compliance()** (4 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **.test_valid_mixed_samples_with_and_without_seqs()** (4 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **.test_valid_samples_with_different_seq_configurations()** (4 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **.test_valid_with_multiple_samples()** (4 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **.test_computed_field_has_seqs_true_with_empty_seqs_list()** (3 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **.test_valid_minimal()** (3 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **.test_valid_sample_set_with_seqs_and_alleles()** (3 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **.test_valid_with_alleles()** (3 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **.test_valid_with_samples_containing_seqs()** (3 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **.test_read_source_complete_sample_batch1_json()** (2 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **.test_read_source_sample_batch2_json()** (2 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **.test_valid_empty_samples_list()** (2 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **Create a SampleForUpload with specified number of SeqForUpload instances.** (1 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **Test reading sample_batch_for_upload1.json as SampleBatchForUpload model.** (1 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **Test reading sample_batch_for_upload2.json as SampleBatchForUpload model.** (1 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **Test valid SampleBatchForUpload with minimal data.** (1 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **Test valid SampleBatchForUpload with alleles.** (1 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **Test valid SampleBatchForUpload with multiple samples including seqs.** (1 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **Test valid SampleBatchForUpload with empty samples list.** (1 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **Test SampleBatchForUpload where all samples contain SeqForUpload instances.** (1 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **Test SampleBatchForUpload with samples having different seq configurations.** (1 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **Test SampleBatchForUpload with mix of samples with and without seqs.** (1 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **Test SampleBatchForUpload with both sample seqs and reference alleles.** (1 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- *... and 3 more nodes in this community*

## Relationships

- [Sample Upload Tests](Sample_Upload_Tests.md) (8 shared connections)
- [SeqForUpload Model Tests](SeqForUpload_Model_Tests.md) (4 shared connections)
- [Allele Upload Model Tests](Allele_Upload_Model_Tests.md) (1 shared connections)
- [Commondb Upload Test Suite](Commondb_Upload_Test_Suite.md) (1 shared connections)
- [SeqForUpload Test Helpers](SeqForUpload_Test_Helpers.md) (1 shared connections)
- [BaseSeq Model Tests](BaseSeq_Model_Tests.md) (1 shared connections)
- [Seqdb Domain Models (Sample/Classification)](Seqdb_Domain_Models_Sample-Classification.md) (1 shared connections)

## Source Files

- `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`

## Audit Trail

- EXTRACTED: 49 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*