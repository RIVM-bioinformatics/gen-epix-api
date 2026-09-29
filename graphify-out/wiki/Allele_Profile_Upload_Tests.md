# Allele Profile Upload Tests

> 21 nodes · cohesion 0.11

## Key Concepts

- **TestModelSeqProfileForUpload** (15 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **Test valid AlleleProfileForUpload with codes.** (4 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **.test_quality_mixin_inheritance()** (3 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **.test_valid_without_locus_code_map_when_not_needed()** (3 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **Test valid AlleleProfileForUpload with locus_code_map when using allele_ids.** (2 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **.test_invalid_missing_allele_data()** (2 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **.test_invalid_missing_locus_code_map_when_needed()** (2 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **.test_invalid_missing_locus_set_fields()** (2 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **.test_invalid_missing_protocol_fields()** (2 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **.test_json_serialization()** (2 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **.test_valid_with_alleles()** (2 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **.test_valid_with_locus_allele_id_map()** (2 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **.test_valid_with_locus_code_map_when_needed()** (2 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **.test_valid_with_protocol_code_and_locus_set_code()** (2 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **.test_valid_with_protocol_id_and_locus_set_id()** (2 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **Test JSON serialization of AlleleProfileForUpload.** (1 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **Test ValidationError when both protocol fields are missing.** (1 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **Test ValidationError when both locus_set fields are missing.** (1 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **Test ValidationError when all allele data fields are missing.** (1 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **Test ValidationError when locus_code_map is missing but alleles have locus_code.** (1 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`
- **Test that AlleleProfileForUpload inherits QualityMixin properties.** (1 connections) — `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`

## Relationships

- [Sample Upload Model Tests](Sample_Upload_Model_Tests.md) (3 shared connections)
- [Allele Upload Model Tests](Allele_Upload_Model_Tests.md) (1 shared connections)
- [Upload Model Validation Tests](Upload_Model_Validation_Tests.md) (1 shared connections)

## Source Files

- `test/seqdb/unit/domain/models_for_upload/test_seqdb_models_for_upload.py`

## Audit Trail

- EXTRACTED: 29 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*