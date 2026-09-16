# Numpy Allele Distance Tests

> 22 nodes · cohesion 0.13

## Key Concepts

- **_make_allele_profile()** (18 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **TestNumpyAlleleIntegration** (15 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **._run_allele_numpy_calc()** (13 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **.test_gate_selects_variant_by_n_new()** (8 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **._allele_protocol()** (7 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **.test_all_three_paths_produce_identical_distance_maps()** (5 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **.test_flag_validation_error()** (5 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **.test_decode_profile_numpy_returns_s16_array()** (4 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **.test_calculate_and_store_distances_int32_vocab()** (3 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **.test_calculate_and_store_distances_numpy_batch()** (3 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **.test_calculate_distance_pair_numpy_branch()** (3 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **parametrize** (2 connections)
- **Unit tests for all new numpy ALLELE distance code paths (LSP-3529).** (1 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **Run _calculate_and_store_distances directly for ALLELE profiles. Returns…** (1 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **_decode_profile with use_numpy_allele=True returns (n_loci,) S16 array; null…** (1 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **The isinstance(np.ndarray) branch in…** (1 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **Each invalid variant-flag combination raises ValueError.** (1 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **numpy_batch path stores correct cross and intra-batch distances.** (1 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **int32_vocab path produces identical distances to numpy_batch.** (1 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **Gate chooses use_batch_new_profiles below _INT32_VOCAB_GATE and use_int32_vocab…** (1 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **Python loop, numpy_batch, and int32_vocab must produce identical distance maps…** (1 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **_crud()** (1 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`

## Relationships

- [New Profile Distance Tests](New_Profile_Distance_Tests.md) (14 shared connections)
- [Seq Distance Calculation Tests](Seq_Distance_Calculation_Tests.md) (6 shared connections)
- [Sequence Distance Calculation](Sequence_Distance_Calculation.md) (6 shared connections)
- [Seq Distance Update Tests](Seq_Distance_Update_Tests.md) (6 shared connections)
- [Seq Upload & SQL Models](Seq_Upload_&_SQL_Models.md) (1 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (1 shared connections)

## Source Files

- `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`

## Audit Trail

- EXTRACTED: 63 (97%)
- INFERRED: 2 (3%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*