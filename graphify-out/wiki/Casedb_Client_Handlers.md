# Casedb Client Handlers

> 25 nodes · cohesion 0.26

## Key Concepts

- **CasedbClient** (48 connections) — `gen_epix/casedb/services/client.py`
- **Any** (21 connections)
- **TestNonCrudHandlers** (21 connections) — `test/casedb/unit/client/test_casedb_client.py`
- **_mock_response()** (20 connections) — `test/casedb/unit/client/test_casedb_client.py`
- **.test_case_type_set_case_type_update_association()** (4 connections) — `test/casedb/unit/client/test_casedb_client.py`
- **.test_col_set_col_update_association()** (4 connections) — `test/casedb/unit/client/test_casedb_client.py`
- **.test_create_case_set()** (4 connections) — `test/casedb/unit/client/test_casedb_client.py`
- **.test_create_file_for_read_set()** (4 connections) — `test/casedb/unit/client/test_casedb_client.py`
- **.test_create_file_for_seq()** (4 connections) — `test/casedb/unit/client/test_casedb_client.py`
- **.test_disease_etiological_agent_update_association()** (4 connections) — `test/casedb/unit/client/test_casedb_client.py`
- **.test_retrieve_case_rights()** (4 connections) — `test/casedb/unit/client/test_casedb_client.py`
- **.test_retrieve_case_set_rights()** (4 connections) — `test/casedb/unit/client/test_casedb_client.py`
- **.test_retrieve_case_stats_by_case_set()** (4 connections) — `test/casedb/unit/client/test_casedb_client.py`
- **.test_retrieve_case_stats_by_case_type()** (4 connections) — `test/casedb/unit/client/test_casedb_client.py`
- **.test_retrieve_cases_by_id()** (4 connections) — `test/casedb/unit/client/test_casedb_client.py`
- **.test_retrieve_complete_case_type()** (4 connections) — `test/casedb/unit/client/test_casedb_client.py`
- **.test_retrieve_is_own_cases()** (4 connections) — `test/casedb/unit/client/test_casedb_client.py`
- **.test_retrieve_phylogenetic_tree_by_cases()** (4 connections) — `test/casedb/unit/client/test_casedb_client.py`
- **.test_retrieve_protocols_assembly()** (4 connections) — `test/casedb/unit/client/test_casedb_client.py`
- **.test_retrieve_protocols_sequencing()** (4 connections) — `test/casedb/unit/client/test_casedb_client.py`
- **.test_retrieve_similar_cases()** (4 connections) — `test/casedb/unit/client/test_casedb_client.py`
- **.test_update_case_created_in_data_collection()** (4 connections) — `test/casedb/unit/client/test_casedb_client.py`
- **.retrieve_case_rights()** (3 connections) — `gen_epix/casedb/services/client.py`
- **.test_retrieve_genetic_sequence_fasta_by_case()** (3 connections) — `test/casedb/unit/client/test_casedb_client.py`
- **.retrieve_genetic_sequence_fasta_by_case()** (2 connections) — `gen_epix/casedb/services/client.py`

## Relationships

- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (8 shared connections)
- [Case Ownership & File Commands](Case_Ownership_&_File_Commands.md) (4 shared connections)
- [Case Access Rights](Case_Access_Rights.md) (3 shared connections)
- [Case Statistics](Case_Statistics.md) (2 shared connections)
- [API Test Fixtures](API_Test_Fixtures.md) (2 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (1 shared connections)
- [Commondb Client](Commondb_Client.md) (1 shared connections)
- [Case Query Retrieval](Case_Query_Retrieval.md) (1 shared connections)
- [Case Type Set Association](Case_Type_Set_Association.md) (1 shared connections)
- [Column Set Association](Column_Set_Association.md) (1 shared connections)
- [Complete Case Type Retrieval](Complete_Case_Type_Retrieval.md) (1 shared connections)
- [Case Set Creation](Case_Set_Creation.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/services/client.py`
- `test/casedb/unit/client/test_casedb_client.py`

## Audit Trail

- EXTRACTED: 108 (97%)
- INFERRED: 3 (3%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*