# User & Person Commands

> 36 nodes · cohesion 0.07

## Key Concepts

- **UpdateUserOwnOrganizationCommand** (14 connections) — `gen_epix/commondb/domain/command/organization.py`
- **RetrievePersonsByIdCommand** (10 connections) — `gen_epix/omopdb/domain/command/omop.py`
- **RetrievePersonsByQueryCommand** (9 connections) — `gen_epix/omopdb/domain/command/omop.py`
- **PersonQueryResult** (9 connections) — `gen_epix/omopdb/domain/model/omop/non_persistable.py`
- **OmopdbEndpointTestClient** (8 connections) — `test/omopdb/omopdb_endpoint_test_client.py`
- **omop_service_retrieve_persons_by_query()** (5 connections) — `gen_epix/omopdb/services/omop/retrieve_person.py`
- **.handle_update_user_own_organization()** (5 connections) — `test/omopdb/omopdb_endpoint_test_client.py`
- **Any** (5 connections)
- **.update_user_own_organization()** (4 connections) — `gen_epix/commondb/domain/service/abac.py`
- **._validate_person_ids()** (4 connections) — `gen_epix/omopdb/domain/command/omop.py`
- **.retrieve_persons_by_id()** (4 connections) — `gen_epix/omopdb/domain/service/omop.py`
- **.retrieve_persons_by_query()** (4 connections) — `gen_epix/omopdb/domain/service/omop.py`
- **.retrieve_persons_by_id()** (4 connections) — `gen_epix/omopdb/services/omop/service.py`
- **.retrieve_persons_by_query()** (4 connections) — `gen_epix/omopdb/services/omop/service.py`
- **.handle_retrieve_person_ids_by_query()** (4 connections) — `test/omopdb/omopdb_endpoint_test_client.py`
- **.handle_retrieve_persons_by_id()** (4 connections) — `test/omopdb/omopdb_endpoint_test_client.py`
- **.handle_upload_persons()** (4 connections) — `test/omopdb/omopdb_endpoint_test_client.py`
- **.__init__()** (4 connections) — `test/omopdb/omopdb_endpoint_test_client.py`
- **Response** (4 connections)
- **.retrieve_persons_by_id()** (3 connections) — `gen_epix/omopdb/services/client.py`
- **.retrieve_persons_by_query()** (3 connections) — `gen_epix/omopdb/services/client.py`
- **UUID** (2 connections)
- **FastAPI** (2 connections)
- **Represents a request to update the current user's {organization} membership.…** (1 connections) — `gen_epix/commondb/domain/command/organization.py`
- **User** (1 connections)
- *... and 11 more nodes in this community*

## Relationships

- [Case Upload Batch Models](Case_Upload_Batch_Models.md) (8 shared connections)
- [Geographic Region Commands](Geographic_Region_Commands.md) (7 shared connections)
- [Seqdb Sequence Retrieval Commands](Seqdb_Sequence_Retrieval_Commands.md) (5 shared connections)
- [OMOP Clinical Data Models](OMOP_Clinical_Data_Models.md) (5 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (4 shared connections)
- [OMOP DB HTTP Client](OMOP_DB_HTTP_Client.md) (2 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (1 shared connections)
- [Seqdb Sequence Commands](Seqdb_Sequence_Commands.md) (1 shared connections)
- [Reference Data Access Filters](Reference_Data_Access_Filters.md) (1 shared connections)
- [Case Date Derivation](Case_Date_Derivation.md) (1 shared connections)
- [Commondb Client](Commondb_Client.md) (1 shared connections)
- [Organization Contacts Retrieval](Organization_Contacts_Retrieval.md) (1 shared connections)

## Source Files

- `gen_epix/commondb/domain/command/organization.py`
- `gen_epix/commondb/domain/service/abac.py`
- `gen_epix/omopdb/domain/command/omop.py`
- `gen_epix/omopdb/domain/model/omop/non_persistable.py`
- `gen_epix/omopdb/domain/service/omop.py`
- `gen_epix/omopdb/services/client.py`
- `gen_epix/omopdb/services/omop/retrieve_person.py`
- `gen_epix/omopdb/services/omop/service.py`
- `test/omopdb/omopdb_endpoint_test_client.py`

## Audit Trail

- EXTRACTED: 84 (97%)
- INFERRED: 3 (3%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*