# Seqdb Sequence Retrieval Commands

> 191 nodes · cohesion 0.02

## Key Concepts

- **App** (214 connections) — `gen_epix/fastapp/app.py`
- **Command** (181 connections) — `gen_epix/commondb/domain/command/base.py`
- **.create_log_message()** (18 connections) — `gen_epix/fastapp/app.py`
- **test_fastapp_app_cache.py** (14 connections) — `test/fastapp/unit/test_fastapp_app_cache.py`
- **.__init__()** (13 connections) — `gen_epix/fastapp/app.py`
- **Any** (13 connections)
- **PolicyDecisionPoint** (13 connections) — `gen_epix/fastapp/pdp.py`
- **TestCrudEndpointSetCreation** (10 connections) — `test/fastapp/unit/api/test_crud_endpoint_set.py`
- **.handle()** (9 connections) — `gen_epix/fastapp/app.py`
- **BaseRemoteService** (9 connections) — `gen_epix/fastapp/services/remote/service.py`
- **TestCrudEndpointSetFlags** (9 connections) — `test/fastapp/unit/api/test_crud_endpoint_set.py`
- **._execute_command()** (8 connections) — `gen_epix/fastapp/app.py`
- **TestCrudEndpointSetValidation** (8 connections) — `test/fastapp/unit/api/test_crud_endpoint_set.py`
- **RetrieveGeneticSequenceFastaByIdCommand** (6 connections) — `gen_epix/casedb/domain/command/seqdb.py`
- **._get_command_handler()** (6 connections) — `gen_epix/fastapp/app.py`
- **.register_listener()** (6 connections) — `gen_epix/fastapp/app.py`
- **.unregister_listener()** (6 connections) — `gen_epix/fastapp/app.py`
- **.apply()** (6 connections) — `gen_epix/fastapp/pdp.py`
- **.get_policies()** (6 connections) — `gen_epix/fastapp/pdp.py`
- **_Command** (6 connections) — `test/fastapp/unit/test_fastapp_app_cache.py`
- **command/seqdb.py** (5 connections) — `gen_epix/casedb/domain/command/seqdb.py`
- **.create_static_log_message()** (5 connections) — `gen_epix/fastapp/app.py`
- **._handle_initial_command()** (5 connections) — `gen_epix/fastapp/app.py`
- **.register_policy()** (5 connections) — `gen_epix/fastapp/app.py`
- **._summarise_command_object_for_log()** (5 connections) — `gen_epix/fastapp/app.py`
- *... and 166 more nodes in this community*

## Relationships

- [CRUD Endpoint Generation](CRUD_Endpoint_Generation.md) (59 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (29 shared connections)
- [FastApp HTTP Client](FastApp_HTTP_Client.md) (28 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (26 shared connections)
- [Domain & Entity Registry](Domain_&_Entity_Registry.md) (20 shared connections)
- [Application Log Items](Application_Log_Items.md) (17 shared connections)
- [Domain Registry & ABAC Policies](Domain_Registry_&_ABAC_Policies.md) (13 shared connections)
- [Geographic Region Commands](Geographic_Region_Commands.md) (10 shared connections)
- [Casedb Service Wiring](Casedb_Service_Wiring.md) (7 shared connections)
- [User Invitation & Management](User_Invitation_&_Management.md) (7 shared connections)
- [Organization Admin Policy](Organization_Admin_Policy.md) (6 shared connections)
- [Casedb ABAC & Geo Endpoints](Casedb_ABAC_&_Geo_Endpoints.md) (6 shared connections)

## Source Files

- `gen_epix/casedb/domain/command/seqdb.py`
- `gen_epix/casedb/domain/service/seqdb.py`
- `gen_epix/casedb/policies/case_abac_policy.py`
- `gen_epix/casedb/services/seqdb/service.py`
- `gen_epix/commondb/domain/command/base.py`
- `gen_epix/commondb/domain/policy/permission.py`
- `gen_epix/commondb/domain/service/rbac.py`
- `gen_epix/commondb/services/abac.py`
- `gen_epix/commondb/services/organization.py`
- `gen_epix/commondb/services/rbac.py`
- `gen_epix/commondb/services/system.py`
- `gen_epix/fastapp/app.py`
- `gen_epix/fastapp/domain/domain.py`
- `gen_epix/fastapp/pdp.py`
- `gen_epix/fastapp/service.py`
- `gen_epix/fastapp/services/remote/__init__.py`
- `gen_epix/fastapp/services/remote/service.py`
- `test/fastapp/unit/api/test_crud_endpoint_set.py`
- `test/fastapp/unit/test_fastapp_app_cache.py`

## Audit Trail

- EXTRACTED: 582 (89%)
- INFERRED: 72 (11%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*