# Seq Distance Data Generation

> 23 nodes · cohesion 0.19

## Key Concepts

- **generate_seq_distances.py** (20 connections) — `test/seqdb/performance/generate_seq_distances.py`
- **create_seq_distance_database()** (16 connections) — `test/seqdb/performance/generate_seq_distances.py`
- **get_allele_profiles()** (8 connections) — `test/seqdb/performance/generate_seq_distances.py`
- **get_seq_distances()** (8 connections) — `test/seqdb/performance/generate_seq_distances.py`
- **DistanceMatrix** (6 connections) — `test/seqdb/seqdb_test_client.py`
- **get_seqs()** (5 connections) — `test/seqdb/performance/generate_seq_distances.py`
- **get_allele_profile_ids()** (4 connections) — `test/seqdb/performance/generate_seq_distances.py`
- **get_sample()** (4 connections) — `test/seqdb/performance/generate_seq_distances.py`
- **get_seq_distance_protocol()** (4 connections) — `test/seqdb/performance/generate_seq_distances.py`
- **Protocol** (4 connections)
- **Sample** (4 connections)
- **UUID** (4 connections)
- **.calculate_distance_matrix_from_allele_profiles()** (4 connections) — `test/seqdb/seqdb_test_client.py`
- **get_data_collection()** (3 connections) — `test/seqdb/performance/generate_seq_distances.py`
- **get_locus_detection_protocol()** (3 connections) — `test/seqdb/performance/generate_seq_distances.py`
- **get_locus_set()** (3 connections) — `test/seqdb/performance/generate_seq_distances.py`
- **LocusSet** (3 connections)
- **SeqProfile** (3 connections)
- **DataCollection** (2 connections)
- **Seq** (2 connections)
- **Any** (1 connections)
- **SeqDistance** (1 connections)
- **SeqProfile** (1 connections)

## Relationships

- [Sample Batch Upload Model](Sample_Batch_Upload_Model.md) (6 shared connections)
- [Protocol Creation Tests](Protocol_Creation_Tests.md) (3 shared connections)
- [FastAPI App Composition](FastAPI_App_Composition.md) (2 shared connections)
- [Seq Repository Queries](Seq_Repository_Queries.md) (2 shared connections)
- [Case Upload Batch Models](Case_Upload_Batch_Models.md) (1 shared connections)
- [Seqdb File Commands & Enums](Seqdb_File_Commands_&_Enums.md) (1 shared connections)
- [Organization & ABAC Models](Organization_&_ABAC_Models.md) (1 shared connections)
- [Reference Data Access Filters](Reference_Data_Access_Filters.md) (1 shared connections)

## Source Files

- `test/seqdb/performance/generate_seq_distances.py`
- `test/seqdb/seqdb_test_client.py`

## Audit Trail

- EXTRACTED: 62 (95%)
- INFERRED: 3 (5%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*