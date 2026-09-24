# Organization Contacts Retrieval

> 65 nodes · cohesion 0.05

## Key Concepts

- **casedb_test_client.py** (47 connections) — `test/casedb/casedb_test_client.py`
- **test_casedb_build.py** (19 connections) — `test/casedb/integration/build_db/test_casedb_build.py`
- **casedb/integration/build_db/update.py** (13 connections) — `test/casedb/integration/build_db/update.py`
- **CasedbEndpointTestClient** (12 connections) — `test/casedb/casedb_endpoint_test_client.py`
- **casedb_endpoint_test_client.py** (11 connections) — `test/casedb/casedb_endpoint_test_client.py`
- **RetrieveOrganizationContactsCommand** (10 connections) — `gen_epix/commondb/domain/command/organization.py`
- **casedb/integration/build_db/create.py** (10 connections) — `test/casedb/integration/build_db/create.py`
- **casedb/integration/build_db/read.py** (9 connections) — `test/casedb/integration/build_db/read.py`
- **OrganizationContacts** (8 connections) — `gen_epix/commondb/domain/model/organization.py`
- **data_access/conftest.py** (8 connections) — `test/casedb/integration/data_access/conftest.py`
- **casedb/integration/build_db/base.py** (7 connections) — `test/casedb/integration/build_db/base.py`
- **casedb/integration/build_db/delete.py** (7 connections) — `test/casedb/integration/build_db/delete.py`
- **define_edge_cases_operational.py** (7 connections) — `test/casedb/integration/data_access/setup/define_edge_cases_operational.py`
- **setup_case_data_operational.py** (7 connections) — `test/casedb/integration/data_access/setup/setup_case_data_operational.py`
- **Any** (6 connections)
- **setup_test_users_and_organizations_operational.py** (6 connections) — `test/casedb/integration/data_access/setup/setup_test_users_and_organizations_operational.py`
- **setup_test_users_and_organizations_reference.py** (6 connections) — `test/casedb/integration/data_access/setup/setup_test_users_and_organizations_reference.py`
- **.handle_case_set_create()** (5 connections) — `test/casedb/casedb_endpoint_test_client.py`
- **.handle_update_case_created_in_data_collection()** (5 connections) — `test/casedb/casedb_endpoint_test_client.py`
- **.handle_update_user_own_organization()** (5 connections) — `test/casedb/casedb_endpoint_test_client.py`
- **Response** (5 connections)
- **setup_case_data_operational()** (5 connections) — `test/casedb/integration/data_access/setup/setup_case_data_operational.py`
- **setup_case_data_reference()** (5 connections) — `test/casedb/integration/data_access/setup/setup_case_data_reference.py`
- **setup_test_users_and_organizations_operational()** (5 connections) — `test/casedb/integration/data_access/setup/setup_test_users_and_organizations_operational.py`
- **setup_test_users_and_organizations_reference()** (5 connections) — `test/casedb/integration/data_access/setup/setup_test_users_and_organizations_reference.py`
- *... and 40 more nodes in this community*

## Relationships

- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (32 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (29 shared connections)
- [Casedb Endpoint Test Client](Casedb_Endpoint_Test_Client.md) (15 shared connections)
- [Seqdb Sequence Retrieval Commands](Seqdb_Sequence_Retrieval_Commands.md) (4 shared connections)
- [Casedb Case API Models](Casedb_Case_API_Models.md) (4 shared connections)
- [Casedb ABAC & Geo Endpoints](Casedb_ABAC_&_Geo_Endpoints.md) (4 shared connections)
- [FastAPI App Composition](FastAPI_App_Composition.md) (3 shared connections)
- [Geographic Region Commands](Geographic_Region_Commands.md) (2 shared connections)
- [User Invitation & Management](User_Invitation_&_Management.md) (2 shared connections)
- [Case Operational Data Models](Case_Operational_Data_Models.md) (2 shared connections)
- [Role Generation & Hierarchy](Role_Generation_&_Hierarchy.md) (2 shared connections)
- [Seqdb File Commands & Enums](Seqdb_File_Commands_&_Enums.md) (2 shared connections)

## Source Files

- `gen_epix/commondb/domain/command/organization.py`
- `gen_epix/commondb/domain/model/organization.py`
- `gen_epix/commondb/domain/service/organization.py`
- `gen_epix/commondb/services/client.py`
- `gen_epix/commondb/services/organization.py`
- `test/casedb/casedb_endpoint_test_client.py`
- `test/casedb/casedb_test_client.py`
- `test/casedb/integration/build_db/base.py`
- `test/casedb/integration/build_db/create.py`
- `test/casedb/integration/build_db/delete.py`
- `test/casedb/integration/build_db/read.py`
- `test/casedb/integration/build_db/test_casedb_build.py`
- `test/casedb/integration/build_db/update.py`
- `test/casedb/integration/data_access/conftest.py`
- `test/casedb/integration/data_access/setup/define_edge_cases_operational.py`
- `test/casedb/integration/data_access/setup/setup_case_data_operational.py`
- `test/casedb/integration/data_access/setup/setup_case_data_reference.py`
- `test/casedb/integration/data_access/setup/setup_test_users_and_organizations_operational.py`
- `test/casedb/integration/data_access/setup/setup_test_users_and_organizations_reference.py`

## Audit Trail

- EXTRACTED: 202 (95%)
- INFERRED: 11 (5%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*