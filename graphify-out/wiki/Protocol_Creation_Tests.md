# Protocol Creation Tests

> 56 nodes · cohesion 0.08

## Key Concepts

- **SeqdbTestClient** (101 connections) — `test/seqdb/seqdb_test_client.py`
- **TestCreate** (53 connections) — `test/seqdb/integration/build_db/create.py`
- **skipif** (20 connections)
- **._build_nextclade_fields_from_alignment()** (5 connections) — `test/seqdb/seqdb_test_client.py`
- **.generate_random_nextclade_snp_batch()** (5 connections) — `test/seqdb/seqdb_test_client.py`
- **.test_create_assembly_protocol_raise()** (3 connections) — `test/seqdb/integration/build_db/create.py`
- **.test_create_ast_protocol_raise()** (3 connections) — `test/seqdb/integration/build_db/create.py`
- **.test_create_data_collection_raise()** (3 connections) — `test/seqdb/integration/build_db/create.py`
- **.test_create_file_raise()** (3 connections) — `test/seqdb/integration/build_db/create.py`
- **.test_create_kmer_detection_protocol_raise()** (3 connections) — `test/seqdb/integration/build_db/create.py`
- **.test_create_locus_detection_protocol_raise()** (3 connections) — `test/seqdb/integration/build_db/create.py`
- **.test_create_mlva_detection_protocol_raise()** (3 connections) — `test/seqdb/integration/build_db/create.py`
- **.test_create_object_already_exists()** (3 connections) — `test/seqdb/integration/build_db/create.py`
- **.test_create_object_invalid_reference()** (3 connections) — `test/seqdb/integration/build_db/create.py`
- **.test_create_org_admin_policy_raise()** (3 connections) — `test/seqdb/integration/build_db/create.py`
- **.test_create_organization_raise()** (3 connections) — `test/seqdb/integration/build_db/create.py`
- **.test_create_pcr_protocol_raise()** (3 connections) — `test/seqdb/integration/build_db/create.py`
- **.test_create_read_set_raise()** (3 connections) — `test/seqdb/integration/build_db/create.py`
- **.test_create_sample_raise()** (3 connections) — `test/seqdb/integration/build_db/create.py`
- **.test_create_seq_classification_protocol_raise()** (3 connections) — `test/seqdb/integration/build_db/create.py`
- **.test_create_seq_distance_protocol_raise()** (3 connections) — `test/seqdb/integration/build_db/create.py`
- **.test_create_sequencing_protocol_raise()** (3 connections) — `test/seqdb/integration/build_db/create.py`
- **.test_create_snp_detection_protocol_raise()** (3 connections) — `test/seqdb/integration/build_db/create.py`
- **.test_create_taxonomy_protocol_raise()** (3 connections) — `test/seqdb/integration/build_db/create.py`
- **.test_create_user_raise()** (3 connections) — `test/seqdb/integration/build_db/create.py`
- *... and 31 more nodes in this community*

## Relationships

- [Seqdb Protocol Factories](Seqdb_Protocol_Factories.md) (17 shared connections)
- [Seq Repository Queries](Seq_Repository_Queries.md) (9 shared connections)
- [Sample Batch Upload Model](Sample_Batch_Upload_Model.md) (9 shared connections)
- [Organization & ABAC Models](Organization_&_ABAC_Models.md) (5 shared connections)
- [Seq Distance Data Generation](Seq_Distance_Data_Generation.md) (3 shared connections)
- [FastAPI App Composition](FastAPI_App_Composition.md) (3 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (2 shared connections)
- [Role Mapping Generator](Role_Mapping_Generator.md) (2 shared connections)
- [Sample Retrieval Tests](Sample_Retrieval_Tests.md) (2 shared connections)
- [Integration Test Client](Integration_Test_Client.md) (1 shared connections)
- [File & Result Format Enums](File_&_Result_Format_Enums.md) (1 shared connections)
- [Sample Retrieval Commands](Sample_Retrieval_Commands.md) (1 shared connections)

## Source Files

- `test/seqdb/integration/build_db/create.py`
- `test/seqdb/seqdb_test_client.py`

## Audit Trail

- EXTRACTED: 166 (92%)
- INFERRED: 14 (8%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*