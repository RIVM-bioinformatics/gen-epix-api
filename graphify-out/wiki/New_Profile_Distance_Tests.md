# New Profile Distance Tests

> 42 nodes · cohesion 0.13

## Key Concepts

- **seq_service_calculate_seq_distances_for_new_profiles()** (31 connections) — `gen_epix/seqdb/services/seq/calculate_seq_distance.py`
- **_setup_distance_mocks()** (26 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **_make_crud_side_effect()** (25 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **_CrudRecorder** (24 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **_make_seq_distance_protocol_for_locus_set()** (19 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **TestCalculateSeqDistancesForNewProfiles** (19 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **_make_seq_distance()** (17 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **._run_snp_distance()** (12 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **.test_batch_upload_all_inter_batch_pairs_stored_in_both_maps()** (9 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **.test_batch_upload_intra_batch_pair_over_threshold_not_stored()** (9 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **.test_snp_profiles_updates_existing_and_creates_new_seq_distances()** (9 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **.test_allele_profiles_distance_over_threshold_creates_new_with_empty_map()** (8 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **.test_mlva_profiles_distance_ignores_missing_loci_and_stores_distance()** (8 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **.test_mlva_profiles_unsupported_existing_profile_format_raises()** (8 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **.test_mlva_profiles_unsupported_new_profile_format_raises()** (8 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **.test_new_profile_without_id_raises()** (8 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **.test_fresh_timestamp_proceeds_normally()** (8 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **.test_none_timestamp_skips_check()** (8 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **.test_stale_timestamp_raises_concurrent_error()** (8 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **_make_mlva_profile()** (7 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **.test_single_new_profile_skips_intra_batch_loop()** (7 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **TestConcurrentModificationCheck** (7 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **.test_no_profiles_returns_empty_and_only_reads_protocols()** (6 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **Protocol** (4 connections)
- **.test_kmer_profiles_raises_not_implemented()** (4 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- *... and 17 more nodes in this community*

## Relationships

- [Seq Distance Calculation Tests](Seq_Distance_Calculation_Tests.md) (38 shared connections)
- [Seq Distance Update Tests](Seq_Distance_Update_Tests.md) (17 shared connections)
- [Numpy Allele Distance Tests](Numpy_Allele_Distance_Tests.md) (14 shared connections)
- [Sequence Distance Calculation](Sequence_Distance_Calculation.md) (5 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (3 shared connections)
- [Sequence Profile CRUD](Sequence_Profile_CRUD.md) (2 shared connections)
- [SQLAlchemy Case Repository](SQLAlchemy_Case_Repository.md) (2 shared connections)
- [Sample Batch Upload](Sample_Batch_Upload.md) (2 shared connections)
- [Exists Filters](Exists_Filters.md) (1 shared connections)
- [Seqdb Locus & Protocol CRUD](Seqdb_Locus_&_Protocol_CRUD.md) (1 shared connections)
- [Seqdb Sequence Commands](Seqdb_Sequence_Commands.md) (1 shared connections)
- [Seq Service Interface](Seq_Service_Interface.md) (1 shared connections)

## Source Files

- `gen_epix/seqdb/services/seq/calculate_seq_distance.py`
- `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`

## Audit Trail

- EXTRACTED: 194 (95%)
- INFERRED: 10 (5%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*