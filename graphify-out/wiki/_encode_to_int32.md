# _encode_to_int32

> 15 nodes

## Key Concepts

- **_encode_to_int32()** (8 connections) — `gen_epix/seqdb/services/seq/calculate_seq_distance.py`
- **_hamming_allele_numpy_batch()** (8 connections) — `gen_epix/seqdb/services/seq/calculate_seq_distance.py`
- **_hamming_allele_int32_batch()** (7 connections) — `gen_epix/seqdb/services/seq/calculate_seq_distance.py`
- **_hamming_allele_numpy()** (7 connections) — `gen_epix/seqdb/services/seq/calculate_seq_distance.py`
- **TestNumpyAlleleKernels** (6 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **.test_hamming_allele_int32_batch_matches_numpy_batch()** (4 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **.test_int32_and_numpy_batch_produce_same_distances_as_python_loop()** (4 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **ndarray** (4 connections)
- **.test_hamming_allele_numpy_batch_matches_per_pair()** (3 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **.test_encode_to_int32_shared_token_gets_same_code()** (2 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **.test_hamming_allele_numpy_identity_mismatch_null()** (2 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **Hamming distances from one existing int32 profile to all M new int32 profiles.…** (1 connections) — `gen_epix/seqdb/services/seq/calculate_seq_distance.py`
- **Hamming distance between two (n_loci,) S16 allele arrays. S16 is a no-uint128…** (1 connections) — `gen_epix/seqdb/services/seq/calculate_seq_distance.py`
- **Hamming distances from one existing S16 profile to all M new profiles.…** (1 connections) — `gen_epix/seqdb/services/seq/calculate_seq_distance.py`
- **Build a shared vocabulary from new + chunk S16 matrices and encode both to…** (1 connections) — `gen_epix/seqdb/services/seq/calculate_seq_distance.py`

## Relationships

- [calculate_seq_distance.py](calculate_seq_distance.py.md) (8 shared connections)
- [test_seqdb_calculate_seq_distance.py](test_seqdb_calculate_seq_distance.py.md) (5 shared connections)

## Source Files

- `gen_epix/seqdb/services/seq/calculate_seq_distance.py`
- `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`

## Audit Trail

- EXTRACTED: 36 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*