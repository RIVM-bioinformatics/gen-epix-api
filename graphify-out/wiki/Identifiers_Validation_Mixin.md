# Identifiers Validation Mixin

> 58 nodes · cohesion 0.05

## Key Concepts

- **SeqProfileForUpload** (25 connections) — `gen_epix/seqdb/domain/model/seq/upload.py`
- **IdentifiersMixin** (18 connections) — `gen_epix/commondb/domain/model/upload.py`
- **SeqClassificationForUpload** (13 connections) — `gen_epix/seqdb/domain/model/seq/upload.py`
- **UUID** (12 connections)
- **._validate_content()** (9 connections) — `gen_epix/seqdb/domain/model/seq/profile.py`
- **Self** (8 connections)
- **._validate_snp_profile()** (7 connections) — `gen_epix/seqdb/domain/model/seq/profile.py`
- **SeqForUpload** (7 connections) — `gen_epix/seqdb/domain/model/seq/upload.py`
- **._validate_kmer_profile()** (6 connections) — `gen_epix/seqdb/domain/model/seq/profile.py`
- **._validate_mlva_profile()** (6 connections) — `gen_epix/seqdb/domain/model/seq/profile.py`
- **._validate_allele_profile_upload()** (6 connections) — `gen_epix/seqdb/domain/model/seq/upload.py`
- **._validate_mlva_profile_upload()** (6 connections) — `gen_epix/seqdb/domain/model/seq/upload.py`
- **ValidateRefDataIdCodeMixin** (6 connections) — `gen_epix/seqdb/domain/model/seq/upload.py`
- **._raise_no_computable_hash()** (5 connections) — `gen_epix/seqdb/domain/model/seq/profile.py`
- **._validate_allele_profile()** (5 connections) — `gen_epix/seqdb/domain/model/seq/profile.py`
- **._validate_exactly_one_representation()** (5 connections) — `gen_epix/seqdb/domain/model/seq/upload.py`
- **._validate_identifiers()** (4 connections) — `gen_epix/commondb/domain/model/upload.py`
- **.get_allele_ids()** (4 connections) — `gen_epix/seqdb/domain/model/seq/profile.py`
- **.get_kmer_profile_hash()** (4 connections) — `gen_epix/seqdb/domain/model/seq/profile.py`
- **.get_mlva_profile_hash()** (4 connections) — `gen_epix/seqdb/domain/model/seq/profile.py`
- **.get_ordered_allele_ids_representation()** (4 connections) — `gen_epix/seqdb/domain/model/seq/profile.py`
- **.get_snp_profile_hash()** (4 connections) — `gen_epix/seqdb/domain/model/seq/profile.py`
- **._validate_format_for_seq_profile_type()** (4 connections) — `gen_epix/seqdb/domain/model/seq/profile.py`
- **._validate_locus_profile()** (4 connections) — `gen_epix/seqdb/domain/model/seq/profile.py`
- **._validate_kmer_profile_upload()** (4 connections) — `gen_epix/seqdb/domain/model/seq/upload.py`
- *... and 33 more nodes in this community*

## Relationships

- [Seqdb Domain Models (Sample/Classification)](Seqdb_Domain_Models_Sample-Classification.md) (29 shared connections)
- [Seqdb Upload Test Suite](Seqdb_Upload_Test_Suite.md) (9 shared connections)
- [Commondb Organization Domain Models](Commondb_Organization_Domain_Models.md) (5 shared connections)
- [Omopdb Upload Test Suite](Omopdb_Upload_Test_Suite.md) (5 shared connections)
- [Upload/ETL Result Model](Upload-ETL_Result_Model.md) (3 shared connections)
- [Seqdb Upload Batch Processing](Seqdb_Upload_Batch_Processing.md) (2 shared connections)
- [Case Upload Batch Model](Case_Upload_Batch_Model.md) (2 shared connections)
- [Sequence Profile Parsing](Sequence_Profile_Parsing.md) (2 shared connections)
- [Case Upload Validation](Case_Upload_Validation.md) (1 shared connections)
- [Commondb Upload Test Suite](Commondb_Upload_Test_Suite.md) (1 shared connections)
- [Sample Upload Tests](Sample_Upload_Tests.md) (1 shared connections)

## Source Files

- `gen_epix/commondb/domain/model/upload.py`
- `gen_epix/seqdb/domain/model/seq/profile.py`
- `gen_epix/seqdb/domain/model/seq/upload.py`

## Audit Trail

- EXTRACTED: 144 (98%)
- INFERRED: 3 (2%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*