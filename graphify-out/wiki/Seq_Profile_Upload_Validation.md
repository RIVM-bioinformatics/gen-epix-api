# Seq Profile Upload Validation

> 26 nodes · cohesion 0.13

## Key Concepts

- **SeqProfileForUpload** (23 connections) — `gen_epix/seqdb/domain/model/seq/upload.py`
- **Self** (8 connections)
- **ValidateRefDataIdCodeMixin** (7 connections) — `gen_epix/seqdb/domain/model/seq/upload.py`
- **._validate_exactly_one_representation()** (6 connections) — `gen_epix/seqdb/domain/model/seq/upload.py`
- **._validate_allele_profile_upload()** (5 connections) — `gen_epix/seqdb/domain/model/seq/upload.py`
- **._validate_mlva_profile_upload()** (5 connections) — `gen_epix/seqdb/domain/model/seq/upload.py`
- **._validate_content()** (4 connections) — `gen_epix/seqdb/domain/model/seq/upload.py`
- **._require_locus_code_map()** (4 connections) — `gen_epix/seqdb/domain/model/seq/upload.py`
- **._validate_kmer_profile_upload()** (4 connections) — `gen_epix/seqdb/domain/model/seq/upload.py`
- **._validate_model()** (4 connections) — `gen_epix/seqdb/domain/model/seq/upload.py`
- **._validate_refdata()** (4 connections) — `gen_epix/seqdb/domain/model/seq/upload.py`
- **model_validator** (3 connections)
- **Validate and normalize an allele-profile upload representation. Returns: The…** (3 connections) — `gen_epix/seqdb/domain/model/seq/upload.py`
- **._get_representation_list()** (3 connections) — `gen_epix/seqdb/domain/model/seq/upload.py`
- **._validate_locus_profile_upload()** (3 connections) — `gen_epix/seqdb/domain/model/seq/upload.py`
- **._validate_snp_profile_upload()** (3 connections) — `gen_epix/seqdb/domain/model/seq/upload.py`
- **Represents a sequence profile record intended for upload. Equal to a…** (1 connections) — `gen_epix/seqdb/domain/model/seq/upload.py`
- **Format representation names for a validation error message.** (1 connections) — `gen_epix/seqdb/domain/model/seq/upload.py`
- **Require exactly one named profile representation. Args: representations:…** (1 connections) — `gen_epix/seqdb/domain/model/seq/upload.py`
- **Require a locus code map for a map-based profile representation. Args:…** (1 connections) — `gen_epix/seqdb/domain/model/seq/upload.py`
- **Require non-empty content for a locus profile upload. Returns: The validated…** (1 connections) — `gen_epix/seqdb/domain/model/seq/upload.py`
- **Require content or an aligned sequence for an SNP profile upload. Returns: The…** (1 connections) — `gen_epix/seqdb/domain/model/seq/upload.py`
- **Apply validation for the selected sequence-profile type.** (1 connections) — `gen_epix/seqdb/domain/model/seq/upload.py`
- **Encapsulates the requirement to identify upload reference data by an ID or a…** (1 connections) — `gen_epix/seqdb/domain/model/seq/upload.py`
- **Reserve post-validation for future classification-content verification.** (1 connections) — `gen_epix/seqdb/domain/model/seq/upload.py`
- *... and 1 more nodes in this community*

## Relationships

- [Sequence Sample Upload Models](Sequence_Sample_Upload_Models.md) (6 shared connections)
- [Seq Upload & SQL Models](Seq_Upload_&_SQL_Models.md) (3 shared connections)
- [Sample Batch Upload](Sample_Batch_Upload.md) (2 shared connections)
- [Case Upload Batch Models](Case_Upload_Batch_Models.md) (2 shared connections)
- [Organization & ABAC Models](Organization_&_ABAC_Models.md) (1 shared connections)
- [Commondb Base Models](Commondb_Base_Models.md) (1 shared connections)
- [Sample Upload Model Tests](Sample_Upload_Model_Tests.md) (1 shared connections)
- [Upload Identifier Models](Upload_Identifier_Models.md) (1 shared connections)

## Source Files

- `gen_epix/seqdb/domain/model/seq/upload.py`

## Audit Trail

- EXTRACTED: 58 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*