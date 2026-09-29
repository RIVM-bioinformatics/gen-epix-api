# Sample Retrieval Commands

> 44 nodes · cohesion 0.06

## Key Concepts

- **SeqdbEndpointTestClient** (11 connections) — `test/seqdb/seqdb_endpoint_test_client.py`
- **RetrieveSampleIdentifiersByIdCommand** (10 connections) — `gen_epix/seqdb/domain/command/seq.py`
- **RetrieveSamplesByIdCommand** (10 connections) — `gen_epix/seqdb/domain/command/seq.py`
- **RetrieveSamplesByQueryCommand** (9 connections) — `gen_epix/seqdb/domain/command/seq.py`
- **seq_service_retrieve_sample_identifiers_by_id()** (6 connections) — `gen_epix/seqdb/services/seq/retrieve_sample.py`
- **seq_service_retrieve_samples_by_id()** (5 connections) — `gen_epix/seqdb/services/seq/retrieve_sample.py`
- **seq_service_retrieve_samples_by_query()** (5 connections) — `gen_epix/seqdb/services/seq/retrieve_sample.py`
- **Any** (5 connections)
- **.handle_update_user_own_organization()** (5 connections) — `test/seqdb/seqdb_endpoint_test_client.py`
- **._validate_seq_ids()** (4 connections) — `gen_epix/seqdb/domain/command/seq.py`
- **UUID** (4 connections)
- **._validate_sample_ids()** (4 connections) — `gen_epix/seqdb/domain/command/seq.py`
- **._validate_sample_ids()** (4 connections) — `gen_epix/seqdb/domain/command/seq.py`
- **.retrieve_sample_identifiers_by_id()** (4 connections) — `gen_epix/seqdb/domain/service/seq.py`
- **.retrieve_samples_by_id()** (4 connections) — `gen_epix/seqdb/domain/service/seq.py`
- **.retrieve_samples_by_query()** (4 connections) — `gen_epix/seqdb/domain/service/seq.py`
- **.retrieve_sample_identifiers_by_id()** (4 connections) — `gen_epix/seqdb/services/seq/service.py`
- **.retrieve_samples_by_id()** (4 connections) — `gen_epix/seqdb/services/seq/service.py`
- **.retrieve_samples_by_query()** (4 connections) — `gen_epix/seqdb/services/seq/service.py`
- **Response** (4 connections)
- **.handle_retrieve_sample_identifiers_by_id()** (4 connections) — `test/seqdb/seqdb_endpoint_test_client.py`
- **.handle_retrieve_sample_ids_by_query()** (4 connections) — `test/seqdb/seqdb_endpoint_test_client.py`
- **.handle_retrieve_samples_by_id()** (4 connections) — `test/seqdb/seqdb_endpoint_test_client.py`
- **.__init__()** (4 connections) — `test/seqdb/seqdb_endpoint_test_client.py`
- **field_validator** (3 connections)
- *... and 19 more nodes in this community*

## Relationships

- [Sample Query Models](Sample_Query_Models.md) (8 shared connections)
- [Seqdb Sequence Commands](Seqdb_Sequence_Commands.md) (7 shared connections)
- [Seq Service Interface](Seq_Service_Interface.md) (6 shared connections)
- [Seqdb Sequence Retrieval Commands](Seqdb_Sequence_Retrieval_Commands.md) (5 shared connections)
- [Phylogenetics & Format Conversion](Phylogenetics_&_Format_Conversion.md) (4 shared connections)
- [Reference Data Access Filters](Reference_Data_Access_Filters.md) (4 shared connections)
- [Seq Upload & SQL Models](Seq_Upload_&_SQL_Models.md) (3 shared connections)
- [Sequence Reference Data Models](Sequence_Reference_Data_Models.md) (3 shared connections)
- [Organization & ABAC Models](Organization_&_ABAC_Models.md) (2 shared connections)
- [FastAPI App Composition](FastAPI_App_Composition.md) (2 shared connections)
- [User Invitation & Management](User_Invitation_&_Management.md) (1 shared connections)
- [Protocol Creation Tests](Protocol_Creation_Tests.md) (1 shared connections)

## Source Files

- `gen_epix/seqdb/domain/command/seq.py`
- `gen_epix/seqdb/domain/service/seq.py`
- `gen_epix/seqdb/services/client.py`
- `gen_epix/seqdb/services/seq/retrieve_sample.py`
- `gen_epix/seqdb/services/seq/service.py`
- `test/seqdb/seqdb_endpoint_test_client.py`

## Audit Trail

- EXTRACTED: 100 (98%)
- INFERRED: 2 (2%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*