# Seq Distance Calculation Tests

> 24 nodes · cohesion 0.12

## Key Concepts

- **test_seqdb_calculate_seq_distance.py** (49 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **UUID** (9 connections)
- **BaseCalculateSeqDistanceTestCase** (8 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **_make_seq_distance_protocol_for_snp()** (8 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **_make_snp_profile_for_upload()** (8 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **TestCalculateSeqDistancesBatchInvariant** (8 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **.test_existing_seq_distances_empty_skips_read_some_and_creates_new()** (8 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **.test_protocol_not_applicable_skips_distance_calculation()** (8 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **seqdb/domain/literal.py** (7 connections) — `gen_epix/seqdb/domain/literal.py`
- **_make_nextclade_content()** (7 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **._make_batch_allele_profiles()** (7 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **_mock_uow()** (4 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **.test_snp_distance_identical_mismatch_n_and_gap()** (4 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **._setup()** (4 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **.setup_method()** (3 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **_s16()** (3 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **_iterable()** (2 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **Provide seqdb functionality for domain.literal.** (1 connections) — `gen_epix/seqdb/domain/literal.py`
- **fixture** (1 connections)
- **ndarray** (1 connections)
- **Return (existing_profiles, new_profiles, existing_ids, new_ids).** (1 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **Return an (n_loci,) S16 array where every locus has the same UUID byte.** (1 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **Identical profiles are zero-distance and Nextclade states mismatch.** (1 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **_crud()** (1 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`

## Relationships

- [New Profile Distance Tests](New_Profile_Distance_Tests.md) (38 shared connections)
- [Sequence Distance Calculation](Sequence_Distance_Calculation.md) (7 shared connections)
- [Role Generation & Hierarchy](Role_Generation_&_Hierarchy.md) (6 shared connections)
- [Numpy Allele Distance Tests](Numpy_Allele_Distance_Tests.md) (6 shared connections)
- [Allele Hamming Distance Kernels](Allele_Hamming_Distance_Kernels.md) (5 shared connections)
- [Seq Distance Update Tests](Seq_Distance_Update_Tests.md) (4 shared connections)
- [Sample Batch Upload](Sample_Batch_Upload.md) (3 shared connections)
- [SQLAlchemy Case Repository](SQLAlchemy_Case_Repository.md) (3 shared connections)
- [Commondb Base Models](Commondb_Base_Models.md) (2 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (2 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (2 shared connections)
- [Organization & ABAC Models](Organization_&_ABAC_Models.md) (2 shared connections)

## Source Files

- `gen_epix/seqdb/domain/literal.py`
- `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`

## Audit Trail

- EXTRACTED: 117 (97%)
- INFERRED: 4 (3%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*