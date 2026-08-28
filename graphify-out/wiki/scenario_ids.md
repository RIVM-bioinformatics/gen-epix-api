# scenario_ids

> 21 nodes · cohesion 0.10

## Key Concepts

- **scenario_ids** (8 connections)
- **TestModelIdentifier** (7 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **TestModelAlleleForUpload** (6 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **.test_id_equals_hash()** (2 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **.test_inheritance_from_seqdb_allele()** (2 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **.test_invalid_id_mismatches_hash()** (2 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **.test_valid_with_locus_id()** (2 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **.test_invalid_missing_both_issuer_fields()** (2 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **.test_max_length_validation()** (2 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **.test_valid_with_both_issuer_fields()** (2 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **.test_valid_with_identifier_issuer_code()** (2 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **.test_valid_with_identifier_issuer_id()** (2 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **Test ValidationError when id doesn't match computed seq_hash.** (1 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **Test valid Identifier with identifier_issuer_code.** (1 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **Test valid Identifier with identifier_issuer_id.** (1 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **Test valid Identifier with both issuer fields.** (1 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **Test ValidationError when both issuer fields are missing.** (1 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **Test field length validation.** (1 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **Test valid AlleleForUpload with locus_id.** (1 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **Test that AlleleForUpload inherits seqdb.Allele properties.** (1 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **Test that id must equal seq_hash when both are provided.** (1 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`

## Relationships

- [seqdb/domain/model/__init__.py](seqdb-domain-model-__init__.py.md) (2 shared connections)
- [TestModelBaseSeq](TestModelBaseSeq.md) (1 shared connections)
- [TestModelSampleBatchForUpload](TestModelSampleBatchForUpload.md) (1 shared connections)
- [._get_allele_profile_for_ids](_get_allele_profile_for_ids.md) (1 shared connections)
- [TestModelSeq](TestModelSeq.md) (1 shared connections)
- [TestModelSeqForUpload](TestModelSeqForUpload.md) (1 shared connections)
- [TestModelSeqProfileForUpload](TestModelSeqProfileForUpload.md) (1 shared connections)

## Source Files

- `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`

## Audit Trail

- EXTRACTED: 28 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*