# Seqdb Test Client

> 32 nodes · cohesion 0.16

## Key Concepts

- **SeqdbTestClient** (61 connections) — `test/seqdb/seqdb_test_client.py`
- **User** (16 connections)
- **._create_protocol()** (16 connections) — `test/seqdb/seqdb_test_client.py`
- **Protocol** (13 connections)
- **.create_read_set()** (9 connections) — `test/seqdb/seqdb_test_client.py`
- **.create_seq()** (9 connections) — `test/seqdb/seqdb_test_client.py`
- **UUID** (6 connections)
- **._get_obj_id()** (6 connections) — `test/seqdb/seqdb_test_client.py`
- **._build_nextclade_fields_from_alignment()** (5 connections) — `test/seqdb/seqdb_test_client.py`
- **.create_file()** (5 connections) — `test/seqdb/seqdb_test_client.py`
- **.create_sample()** (5 connections) — `test/seqdb/seqdb_test_client.py`
- **.create_seq_distance_protocol()** (5 connections) — `test/seqdb/seqdb_test_client.py`
- **.generate_random_nextclade_snp_batch()** (5 connections) — `test/seqdb/seqdb_test_client.py`
- **.create_assembly_protocol()** (4 connections) — `test/seqdb/seqdb_test_client.py`
- **.create_ast_protocol()** (4 connections) — `test/seqdb/seqdb_test_client.py`
- **.create_kmer_detection_protocol()** (4 connections) — `test/seqdb/seqdb_test_client.py`
- **.create_locus_detection_protocol()** (4 connections) — `test/seqdb/seqdb_test_client.py`
- **.create_mlva_detection_protocol()** (4 connections) — `test/seqdb/seqdb_test_client.py`
- **.create_pcr_protocol()** (4 connections) — `test/seqdb/seqdb_test_client.py`
- **.create_seq_classification_protocol()** (4 connections) — `test/seqdb/seqdb_test_client.py`
- **.create_sequencing_protocol()** (4 connections) — `test/seqdb/seqdb_test_client.py`
- **.create_snp_detection_protocol()** (4 connections) — `test/seqdb/seqdb_test_client.py`
- **.create_taxonomy_protocol()** (4 connections) — `test/seqdb/seqdb_test_client.py`
- **Sample** (3 connections)
- **Model** (2 connections)
- *... and 7 more nodes in this community*

## Relationships

- [Sequence Generation Settings](Sequence_Generation_Settings.md) (8 shared connections)
- [App Composition & Startup](App_Composition_&_Startup.md) (7 shared connections)
- [Seq Dict Repository](Seq_Dict_Repository.md) (5 shared connections)
- [Commondb Enums & Demo Data](Commondb_Enums_&_Demo_Data.md) (4 shared connections)
- [Seq Distance Generation Script](Seq_Distance_Generation_Script.md) (4 shared connections)
- [Sample Batch Uploader Tests](Sample_Batch_Uploader_Tests.md) (4 shared connections)
- [Distance Optimization Benchmarks](Distance_Optimization_Benchmarks.md) (3 shared connections)
- [File Creation Command](File_Creation_Command.md) (3 shared connections)
- [Seqdb Enums](Seqdb_Enums.md) (3 shared connections)
- [Sample Retrieval Tests](Sample_Retrieval_Tests.md) (2 shared connections)
- [Seq SA Repository](Seq_SA_Repository.md) (2 shared connections)
- [Seq Distance Performance Tests](Seq_Distance_Performance_Tests.md) (2 shared connections)

## Source Files

- `test/seqdb/seqdb_test_client.py`

## Audit Trail

- EXTRACTED: 111 (83%)
- INFERRED: 23 (17%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*