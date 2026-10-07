# FastAPI App Composition

> 254 nodes · cohesion 0.01

## Key Concepts

- **AppCfg** (49 connections) — `gen_epix/commondb/config/cfg.py`
- **ServerManager** (42 connections) — `test/test_client/server_manager.py`
- **AppComposer** (38 connections) — `gen_epix/commondb/env.py`
- **seqdb_test_client.py** (37 connections) — `test/seqdb/seqdb_test_client.py`
- **test_casedb_seqdb_connection.py** (33 connections) — `test/end_to_end/casedb_seqdb_connection/test_casedb_seqdb_connection.py`
- **start_all_services.py** (30 connections) — `test/test_client/start_all_services.py`
- **app_setup.py** (26 connections) — `gen_epix/commondb/app_setup.py`
- **create_fast_api()** (26 connections) — `gen_epix/commondb/app_setup.py`
- **BaseAppCfg** (22 connections) — `gen_epix/commondb/config/cfg.py`
- **seqdb/api/router.py** (22 connections) — `gen_epix/seqdb/api/router.py`
- **ServerType** (19 connections) — `test/test_client/enum.py`
- **create_routers()** (17 connections) — `gen_epix/seqdb/api/router.py`
- **cfg.py** (16 connections) — `gen_epix/commondb/config/cfg.py`
- **seqdb/env.py** (15 connections) — `gen_epix/seqdb/env.py`
- **casedb/env.py** (14 connections) — `gen_epix/casedb/env.py`
- **.__init__()** (14 connections) — `gen_epix/commondb/env.py`
- **omopdb/app.py** (12 connections) — `gen_epix/omopdb/app.py`
- **seqdb/app.py** (12 connections) — `gen_epix/seqdb/app.py`
- **AppComposer** (12 connections) — `gen_epix/seqdb/env.py`
- **._init_service()** (11 connections) — `gen_epix/commondb/env.py`
- **AppComposer** (11 connections) — `gen_epix/omopdb/env.py`
- **seqdb_server()** (11 connections) — `test/end_to_end/casedb_seqdb_connection/test_casedb_seqdb_connection.py`
- **test_client_credential_flow.py** (11 connections) — `test/end_to_end/client_credential_flow/test_client_credential_flow.py`
- **commondb/app.py** (10 connections) — `gen_epix/commondb/app.py`
- **.set_log_level()** (10 connections) — `gen_epix/commondb/config/cfg.py`
- *... and 229 more nodes in this community*

## Relationships

- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (77 shared connections)
- [Casedb ABAC & Geo Endpoints](Casedb_ABAC_&_Geo_Endpoints.md) (20 shared connections)
- [Role Mapping Generator](Role_Mapping_Generator.md) (14 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (12 shared connections)
- [OIDC Client Test App](OIDC_Client_Test_App.md) (12 shared connections)
- [Auth Exception Middleware](Auth_Exception_Middleware.md) (7 shared connections)
- [Casedb Service Wiring](Casedb_Service_Wiring.md) (5 shared connections)
- [Seqdb File Commands & Enums](Seqdb_File_Commands_&_Enums.md) (5 shared connections)
- [Organization & ABAC Models](Organization_&_ABAC_Models.md) (5 shared connections)
- [App Config Reading Tests](App_Config_Reading_Tests.md) (4 shared connections)
- [Casedb Endpoint Test Client](Casedb_Endpoint_Test_Client.md) (4 shared connections)
- [Organization Contacts Retrieval](Organization_Contacts_Retrieval.md) (3 shared connections)

## Source Files

- `gen_epix/casedb/app.py`
- `gen_epix/casedb/env.py`
- `gen_epix/commondb/app.py`
- `gen_epix/commondb/app_setup.py`
- `gen_epix/commondb/config/__init__.py`
- `gen_epix/commondb/config/cfg.py`
- `gen_epix/commondb/config/settings_manager.py`
- `gen_epix/commondb/env.py`
- `gen_epix/commondb/test/test_client.py`
- `gen_epix/omopdb/app.py`
- `gen_epix/omopdb/env.py`
- `gen_epix/seqdb/api/router.py`
- `gen_epix/seqdb/app.py`
- `gen_epix/seqdb/env.py`
- `gen_epix/util.py`
- `run.py`
- `test/casedb/casedb_test_client.py`
- `test/casedb/integration/content/test_casedb_content.py`
- `test/casedb/performance/repository/test_casedb_repository_performance.py`
- `test/casedb/performance/startup/test_casedb_startup_performance.py`

## Audit Trail

- EXTRACTED: 610 (90%)
- INFERRED: 69 (10%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*