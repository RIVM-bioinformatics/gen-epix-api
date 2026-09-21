# User Invitation & Management

> 70 nodes · cohesion 0.04

## Key Concepts

- **EndpointTestClient** (25 connections) — `gen_epix/commondb/test/endpoint_test_client.py`
- **.__init__()** (19 connections) — `gen_epix/commondb/test/endpoint_test_client.py`
- **InviteUserCommand** (12 connections) — `gen_epix/commondb/domain/command/organization.py`
- **RegisterInvitedUserCommand** (12 connections) — `gen_epix/commondb/domain/command/organization.py`
- **UpdateUserCommand** (12 connections) — `gen_epix/commondb/domain/command/organization.py`
- **._content_to_obj()** (10 connections) — `gen_epix/commondb/test/endpoint_test_client.py`
- **Any** (10 connections)
- **AnonymizeUserCommand** (8 connections) — `gen_epix/commondb/domain/command/organization.py`
- **Response** (8 connections)
- **.get_headers()** (6 connections) — `gen_epix/commondb/test/endpoint_test_client.py`
- **.handle_crud_command()** (6 connections) — `gen_epix/commondb/test/endpoint_test_client.py`
- **.handle_get_identity_providers()** (6 connections) — `gen_epix/commondb/test/endpoint_test_client.py`
- **.handle_invite_user()** (6 connections) — `gen_epix/commondb/test/endpoint_test_client.py`
- **.handle_register_invited_user()** (6 connections) — `gen_epix/commondb/test/endpoint_test_client.py`
- **.handle_retrieve_invite_user_constraints()** (6 connections) — `gen_epix/commondb/test/endpoint_test_client.py`
- **.handle_update_user()** (6 connections) — `gen_epix/commondb/test/endpoint_test_client.py`
- **.register_handler()** (6 connections) — `gen_epix/commondb/test/endpoint_test_client.py`
- **.handle()** (5 connections) — `gen_epix/commondb/test/endpoint_test_client.py`
- **.anonymize_user()** (4 connections) — `gen_epix/commondb/domain/service/organization.py`
- **.invite_user()** (4 connections) — `gen_epix/commondb/domain/service/organization.py`
- **.register_invited_user()** (4 connections) — `gen_epix/commondb/domain/service/organization.py`
- **.update_user()** (4 connections) — `gen_epix/commondb/domain/service/organization.py`
- **User** (4 connections)
- **.anonymize_user()** (4 connections) — `gen_epix/commondb/services/organization.py`
- **.invite_user()** (4 connections) — `gen_epix/commondb/services/organization.py`
- *... and 45 more nodes in this community*

## Relationships

- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (19 shared connections)
- [Geographic Region Commands](Geographic_Region_Commands.md) (11 shared connections)
- [Seqdb Sequence Retrieval Commands](Seqdb_Sequence_Retrieval_Commands.md) (7 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (4 shared connections)
- [Commondb Client](Commondb_Client.md) (4 shared connections)
- [Organization & ABAC Models](Organization_&_ABAC_Models.md) (4 shared connections)
- [Seqdb Sequence Commands](Seqdb_Sequence_Commands.md) (3 shared connections)
- [Organization Contacts Retrieval](Organization_Contacts_Retrieval.md) (2 shared connections)
- [Integration Test Client](Integration_Test_Client.md) (2 shared connections)
- [Role Mapping Generator](Role_Mapping_Generator.md) (1 shared connections)
- [User & Person Commands](User_&_Person_Commands.md) (1 shared connections)
- [Sample Retrieval Commands](Sample_Retrieval_Commands.md) (1 shared connections)

## Source Files

- `gen_epix/commondb/domain/command/organization.py`
- `gen_epix/commondb/domain/service/organization.py`
- `gen_epix/commondb/services/client.py`
- `gen_epix/commondb/services/organization.py`
- `gen_epix/commondb/test/endpoint_test_client.py`

## Audit Trail

- EXTRACTED: 160 (99%)
- INFERRED: 2 (1%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*