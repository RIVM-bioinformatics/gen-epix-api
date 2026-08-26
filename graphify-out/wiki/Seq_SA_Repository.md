# Seq SA Repository

> 26 nodes · cohesion 0.13

## Key Concepts

- **SeqSARepository** (26 connections) — `gen_epix/seqdb/repositories/seq_sa.py`
- **seq_sa.py** (15 connections) — `gen_epix/seqdb/repositories/seq_sa.py`
- **UUID** (12 connections)
- **TestCalculateSeqDistancesScaleMssql** (10 connections) — `test/seqdb/performance/calculate_seq_distances/test_seqdb_calculate_seq_distances_performance.py`
- **TestCalculateSeqDistancesScale** (9 connections) — `test/seqdb/performance/calculate_seq_distances/test_seqdb_calculate_seq_distances_performance.py`
- **.filter_seq_profiles_by_quality()** (5 connections) — `gen_epix/seqdb/repositories/seq_sa.py`
- **.retrieve_similar_profiles()** (5 connections) — `gen_epix/seqdb/repositories/seq_sa.py`
- **.update_some_seq_distance_content()** (5 connections) — `gen_epix/seqdb/repositories/seq_sa.py`
- **.get_max_seq_distance_modified_at()** (4 connections) — `gen_epix/seqdb/repositories/seq_sa.py`
- **.get_profiles_by_protocol_ids()** (4 connections) — `gen_epix/seqdb/repositories/seq_sa.py`
- **.get_profiles_without_seq_distance()** (4 connections) — `gen_epix/seqdb/repositories/seq_sa.py`
- **.get_sample_ids_modified_in_range()** (4 connections) — `gen_epix/seqdb/repositories/seq_sa.py`
- **.iter_seq_distances()** (4 connections) — `gen_epix/seqdb/repositories/seq_sa.py`
- **datetime** (3 connections)
- **.get_full_samples_by_sample_ids()** (3 connections) — `gen_epix/seqdb/repositories/seq_sa.py`
- **.iter_seq_distance_profile_ids()** (3 connections) — `gen_epix/seqdb/repositories/seq_sa.py`
- **.retrieve_seq_fasta()** (3 connections) — `gen_epix/seqdb/repositories/seq_sa.py`
- **performance** (3 connections)
- **scenario_ids** (3 connections)
- **SeqDistance** (2 connections)
- **SeqProfile** (2 connections)
- **AbstractSet** (1 connections)
- **Any** (1 connections)
- **mssql** (1 connections)
- **Scale test for _calculate_and_store_distances — DICT and SA_SQLITE. All…** (1 connections) — `test/seqdb/performance/calculate_seq_distances/test_seqdb_calculate_seq_distances_performance.py`
- *... and 1 more nodes in this community*

## Relationships

- [Seq Dict Repository](Seq_Dict_Repository.md) (16 shared connections)
- [Casedb Case CRUD Commands](Casedb_Case_CRUD_Commands.md) (11 shared connections)
- [Sample Batch Uploader Tests](Sample_Batch_Uploader_Tests.md) (5 shared connections)
- [Sample Query Retrieval](Sample_Query_Retrieval.md) (3 shared connections)
- [Casedb Repository Implementations](Casedb_Repository_Implementations.md) (2 shared connections)
- [FastApp SA Repository Core](FastApp_SA_Repository_Core.md) (2 shared connections)
- [SA Model Mapping Utils](SA_Model_Mapping_Utils.md) (2 shared connections)
- [Seqdb Enums](Seqdb_Enums.md) (2 shared connections)
- [Seqdb Test Client](Seqdb_Test_Client.md) (2 shared connections)
- [SQLAlchemy Unit of Work](SQLAlchemy_Unit_of_Work.md) (1 shared connections)
- [Commondb Enums & Demo Data](Commondb_Enums_&_Demo_Data.md) (1 shared connections)
- [Commondb Organization Domain Models](Commondb_Organization_Domain_Models.md) (1 shared connections)

## Source Files

- `gen_epix/seqdb/repositories/seq_sa.py`
- `test/seqdb/performance/calculate_seq_distances/test_seqdb_calculate_seq_distances_performance.py`

## Audit Trail

- EXTRACTED: 80 (87%)
- INFERRED: 12 (13%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*