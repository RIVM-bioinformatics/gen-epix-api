# Phylogenetics & Format Conversion

> 63 nodes · cohesion 0.06

## Key Concepts

- **SeqdbClient** (43 connections) — `gen_epix/seqdb/services/client.py`
- **TestSeqdbClient** (22 connections) — `test/seqdb/unit/client/test_seqdb_client.py`
- **CalculatePhylogeneticTreeCommand** (17 connections) — `gen_epix/seqdb/domain/command/seq.py`
- **ConvertSeqFormatCommand** (10 connections) — `gen_epix/seqdb/domain/command/seq.py`
- **RetrieveSimilarProfilesCommand** (9 connections) — `gen_epix/seqdb/domain/command/seq.py`
- **UUID** (8 connections)
- **patch** (7 connections)
- **Any** (7 connections)
- **.test_successful_request_with_full_response()** (7 connections) — `test/seqdb/unit/client/test_seqdb_client.py`
- **fixture** (6 connections)
- **TestRetrieveSeqDistanceLastModified** (6 connections) — `test/seqdb/unit/client/test_seqdb_client.py`
- **.test_request_body_construction()** (6 connections) — `test/seqdb/unit/client/test_seqdb_client.py`
- **.test_authentication_headers_included()** (5 connections) — `test/seqdb/unit/client/test_seqdb_client.py`
- **.test_successful_request_without_leaf_ids()** (5 connections) — `test/seqdb/unit/client/test_seqdb_client.py`
- **._validate_state()** (4 connections) — `gen_epix/seqdb/domain/command/seq.py`
- **._validate_formats()** (4 connections) — `gen_epix/seqdb/domain/command/seq.py`
- **.calculate_phylogenetic_tree()** (4 connections) — `gen_epix/seqdb/domain/service/seq.py`
- **.calculate_phylogenetic_tree()** (4 connections) — `gen_epix/seqdb/services/seq/service.py`
- **User** (4 connections)
- **.client()** (4 connections) — `test/seqdb/unit/client/test_seqdb_client.py`
- **.sample_command()** (4 connections) — `test/seqdb/unit/client/test_seqdb_client.py`
- **.test_empty_dict_response_returns_none()** (4 connections) — `test/seqdb/unit/client/test_seqdb_client.py`
- **.test_empty_response_returns_none()** (4 connections) — `test/seqdb/unit/client/test_seqdb_client.py`
- **.test_http_error_propagates()** (4 connections) — `test/seqdb/unit/client/test_seqdb_client.py`
- **.calculate_phylogenetic_tree()** (3 connections) — `gen_epix/seqdb/services/client.py`
- *... and 38 more nodes in this community*

## Relationships

- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (9 shared connections)
- [Seqdb Sequence Commands](Seqdb_Sequence_Commands.md) (8 shared connections)
- [Casedb Service Wiring](Casedb_Service_Wiring.md) (5 shared connections)
- [Sample Retrieval Commands](Sample_Retrieval_Commands.md) (4 shared connections)
- [Seqdb Sequence Retrieval Commands](Seqdb_Sequence_Retrieval_Commands.md) (3 shared connections)
- [Seq Service Interface](Seq_Service_Interface.md) (3 shared connections)
- [Sequence Reference Data Models](Sequence_Reference_Data_Models.md) (3 shared connections)
- [Best Sequence Retrieval](Best_Sequence_Retrieval.md) (3 shared connections)
- [Seqdb API Request Bodies](Seqdb_API_Request_Bodies.md) (2 shared connections)
- [Reference Data Access Filters](Reference_Data_Access_Filters.md) (1 shared connections)
- [Sequence Format Conversion](Sequence_Format_Conversion.md) (1 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (1 shared connections)

## Source Files

- `gen_epix/seqdb/domain/command/seq.py`
- `gen_epix/seqdb/domain/service/seq.py`
- `gen_epix/seqdb/services/client.py`
- `gen_epix/seqdb/services/seq/service.py`
- `test/seqdb/unit/client/test_seqdb_client.py`

## Audit Trail

- EXTRACTED: 153 (95%)
- INFERRED: 8 (5%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*