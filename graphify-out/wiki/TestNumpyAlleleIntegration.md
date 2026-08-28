# TestNumpyAlleleIntegration

> 25 nodes · cohesion 0.10

## Key Concepts

- **TestNumpyAlleleIntegration** (14 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **._run_allele_numpy_calc()** (11 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **._allele_protocol()** (7 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **_make_user()** (6 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **.test_all_three_paths_produce_identical_distance_maps()** (5 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **.test_flag_validation_error()** (5 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **Protocol** (4 connections)
- **._setup()** (4 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **.test_decode_profile_numpy_returns_s16_array()** (4 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **.setup_method()** (3 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **_mock_uow()** (3 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **.test_calculate_and_store_distances_int32_vocab()** (3 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **.test_calculate_and_store_distances_numpy_batch()** (3 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **.test_calculate_distance_pair_numpy_branch()** (3 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **parametrize** (2 connections)
- **fixture** (1 connections)
- **User** (1 connections)
- **Unit tests for all new numpy ALLELE distance code paths (LSP-3529).** (1 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **Run _calculate_and_store_distances directly for ALLELE profiles. Returns…** (1 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **_decode_profile with use_numpy_allele=True returns (n_loci,) S16 array; null…** (1 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **The isinstance(np.ndarray) branch in…** (1 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **Each invalid variant-flag combination raises ValueError.** (1 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **numpy_batch path stores correct cross and intra-batch distances.** (1 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **int32_vocab path produces identical distances to numpy_batch.** (1 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **Python loop, numpy_batch, and int32_vocab must produce identical distance maps…** (1 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`

## Relationships

- [seq_service_calculate_seq_distances_for_new_profiles](seq_service_calculate_seq_distances_for_new_profiles.md) (12 shared connections)
- [test_seqdb_calculate_seq_distance.py](test_seqdb_calculate_seq_distance.py.md) (7 shared connections)
- [calculate_seq_distance.py](calculate_seq_distance.py.md) (5 shared connections)
- [commondb/domain/enum.py](commondb-domain-enum.py.md) (1 shared connections)
- [Role](Role.md) (1 shared connections)
- [_verify_children_seq_classifications](_verify_children_seq_classifications.md) (1 shared connections)

## Source Files

- `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`

## Audit Trail

- EXTRACTED: 55 (96%)
- INFERRED: 2 (4%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*