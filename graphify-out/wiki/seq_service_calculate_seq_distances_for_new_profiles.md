# seq_service_calculate_seq_distances_for_new_profiles

> 39 nodes · cohesion 0.15

## Key Concepts

- **seq_service_calculate_seq_distances_for_new_profiles()** (30 connections) — `gen_epix/seqdb/services/seq/calculate_seq_distance.py`
- **_CrudRecorder** (23 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **_setup_distance_mocks()** (23 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **_make_crud_side_effect()** (22 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **_make_seq_distance_protocol_for_locus_set()** (19 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **_make_allele_profile()** (18 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **_make_seq_distance()** (16 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **.test_batch_upload_all_inter_batch_pairs_stored_in_both_maps()** (9 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **.test_batch_upload_intra_batch_pair_over_threshold_not_stored()** (9 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **.test_allele_profiles_distance_over_threshold_creates_new_with_empty_map()** (8 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **.test_mlva_profiles_distance_ignores_missing_loci_and_stores_distance()** (8 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **.test_mlva_profiles_unsupported_existing_profile_format_raises()** (8 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **.test_mlva_profiles_unsupported_new_profile_format_raises()** (8 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **.test_new_profile_without_id_raises()** (8 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **.test_fresh_timestamp_proceeds_normally()** (8 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **.test_none_timestamp_skips_check()** (8 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **.test_stale_timestamp_raises_concurrent_error()** (8 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **.test_gate_selects_variant_by_n_new()** (8 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **.test_chunked_existing_profiles_updates_both_and_maintains_symmetry()** (8 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **.test_missing_profile_creates_distance()** (8 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **.test_single_new_profile_skips_intra_batch_loop()** (7 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **.test_no_missing_profiles_returns_empty()** (7 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **.test_no_profiles_returns_empty_and_only_reads_protocols()** (6 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **.test_kmer_profiles_raises_not_implemented()** (4 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **SeqDistance** (3 connections)
- *... and 14 more nodes in this community*

## Relationships

- [test_seqdb_calculate_seq_distance.py](test_seqdb_calculate_seq_distance.py.md) (51 shared connections)
- [TestNumpyAlleleIntegration](TestNumpyAlleleIntegration.md) (12 shared connections)
- [calculate_seq_distance.py](calculate_seq_distance.py.md) (4 shared connections)
- [crud_seq_profile.py](crud_seq_profile.py.md) (2 shared connections)
- [CalculateSeqDistancesForNewProfilesCommand](CalculateSeqDistancesForNewProfilesCommand.md) (2 shared connections)
- [BaseSeqService](BaseSeqService.md) (2 shared connections)
- [seq_service_update_seq_distances](seq_service_update_seq_distances.md) (2 shared connections)
- [composite.py](composite.py.md) (1 shared connections)
- [seqdb/domain/model/__init__.py](seqdb-domain-model-__init__.py.md) (1 shared connections)
- [validate_int_enum_value](validate_int_enum_value.md) (1 shared connections)

## Source Files

- `gen_epix/seqdb/services/seq/calculate_seq_distance.py`
- `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`

## Audit Trail

- EXTRACTED: 188 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*