# Seq Distance Update Tests

> 15 nodes · cohesion 0.17

## Key Concepts

- **.test_chunked_existing_profiles_updates_both_and_maintains_symmetry()** (10 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **.test_missing_profile_creates_distance()** (10 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **.test_no_missing_profiles_returns_empty()** (9 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **_run()** (8 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **TestUpdateSeqDistances** (8 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **_crud()** (7 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **.protocol()** (5 connections) — `gen_epix/fastapp/client.py`
- **scenario_ids** (5 connections)
- **_crud()** (2 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **_crud()** (2 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **When all profiles already have distances, returns empty.** (1 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **When a profile is missing a distance, create it and maintain symmetry.** (1 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **With existing_chunk_size=1 and 2 existing profiles, iter_seq_distances is…** (1 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **_crud()** (1 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`
- **_crud()** (1 connections) — `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`

## Relationships

- [New Profile Distance Tests](New_Profile_Distance_Tests.md) (17 shared connections)
- [Numpy Allele Distance Tests](Numpy_Allele_Distance_Tests.md) (6 shared connections)
- [Seq Distance Calculation Tests](Seq_Distance_Calculation_Tests.md) (4 shared connections)
- [Sequence Distance Calculation](Sequence_Distance_Calculation.md) (4 shared connections)
- [FastApp HTTP Client](FastApp_HTTP_Client.md) (2 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (1 shared connections)
- [Sample Batch Upload](Sample_Batch_Upload.md) (1 shared connections)

## Source Files

- `gen_epix/fastapp/client.py`
- `test/seqdb/unit/services/seq/calculate_seq_distance/test_seqdb_calculate_seq_distance.py`

## Audit Trail

- EXTRACTED: 41 (77%)
- INFERRED: 12 (23%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*