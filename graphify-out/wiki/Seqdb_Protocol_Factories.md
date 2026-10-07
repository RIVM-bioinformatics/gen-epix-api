# Seqdb Protocol Factories

> 24 nodes · cohesion 0.19

## Key Concepts

- **User** (16 connections)
- **._create_protocol()** (16 connections) — `test/seqdb/seqdb_test_client.py`
- **Protocol** (13 connections)
- **.create_read_set()** (9 connections) — `test/seqdb/seqdb_test_client.py`
- **.create_seq()** (9 connections) — `test/seqdb/seqdb_test_client.py`
- **UUID** (6 connections)
- **._get_obj_id()** (6 connections) — `test/seqdb/seqdb_test_client.py`
- **.create_sample()** (5 connections) — `test/seqdb/seqdb_test_client.py`
- **.create_seq_distance_protocol()** (5 connections) — `test/seqdb/seqdb_test_client.py`
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
- **DataCollection** (1 connections)
- **ReadSet** (1 connections)
- **Seq** (1 connections)

## Relationships

- [Protocol Creation Tests](Protocol_Creation_Tests.md) (17 shared connections)
- [File & Result Format Enums](File_&_Result_Format_Enums.md) (5 shared connections)
- [Protocol & Profile Type Enums](Protocol_&_Profile_Type_Enums.md) (2 shared connections)
- [Sample Batch Upload Model](Sample_Batch_Upload_Model.md) (1 shared connections)
- [FastAPI App Composition](FastAPI_App_Composition.md) (1 shared connections)
- [Role Mapping Generator](Role_Mapping_Generator.md) (1 shared connections)

## Source Files

- `test/seqdb/seqdb_test_client.py`

## Audit Trail

- EXTRACTED: 80 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*