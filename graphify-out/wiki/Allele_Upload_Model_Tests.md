# Allele Upload Model Tests

> 10 nodes · cohesion 0.20

## Key Concepts

- **scenario_ids** (8 connections)
- **TestModelAlleleForUpload** (6 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **.test_id_equals_hash()** (2 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **.test_inheritance_from_seqdb_allele()** (2 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **.test_invalid_id_mismatches_hash()** (2 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **.test_valid_with_locus_id()** (2 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **Test ValidationError when id doesn't match computed seq_hash.** (1 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **Test valid AlleleForUpload with locus_id.** (1 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **Test that AlleleForUpload inherits seqdb.Allele properties.** (1 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **Test that id must equal seq_hash when both are provided.** (1 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`

## Relationships

- [Upload Model Validation Tests](Upload_Model_Validation_Tests.md) (2 shared connections)
- [Sample Upload Batch Tests](Sample_Upload_Batch_Tests.md) (2 shared connections)
- [Sequence Model Validation Tests](Sequence_Model_Validation_Tests.md) (1 shared connections)
- [Sample Upload Model Tests](Sample_Upload_Model_Tests.md) (1 shared connections)
- [Seq Model Tests](Seq_Model_Tests.md) (1 shared connections)
- [Allele Profile Upload Tests](Allele_Profile_Upload_Tests.md) (1 shared connections)

## Source Files

- `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`

## Audit Trail

- EXTRACTED: 17 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*