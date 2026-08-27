# App Composition & Startup

> 178 nodes · cohesion 0.02

## Key Concepts

- **AppCfg** (56 connections) — `gen_epix/commondb/config/cfg.py`
- **seqdb_test_client.py** (36 connections) — `test/seqdb/seqdb_test_client.py`
- **test_casedb_seqdb_connection.py** (31 connections) — `test/end_to_end/casedb_seqdb_connection/test_casedb_seqdb_connection.py`
- **create_fast_api()** (30 connections) — `gen_epix/commondb/app_setup.py`
- **start_all_services.py** (30 connections) — `test/test_client/start_all_services.py`
- **AppComposer** (26 connections) — `gen_epix/commondb/env.py`
- **app_setup.py** (25 connections) — `gen_epix/commondb/app_setup.py`
- **BaseAppCfg** (25 connections) — `gen_epix/commondb/config/cfg.py`
- **AppComposer** (22 connections) — `gen_epix/casedb/env.py`
- **omopdb_test_client.py** (22 connections) — `test/omopdb/omopdb_test_client.py`
- **get_test_client()** (17 connections) — `test/commondb/test_client/util.py`
- **test/test_client/util.py** (17 connections) — `test/test_client/util.py`
- **cfg.py** (16 connections) — `gen_epix/commondb/config/cfg.py`
- **get_test_root_output_dir()** (16 connections) — `test/test_client/util.py`
- **seqdb/env.py** (14 connections) — `gen_epix/seqdb/env.py`
- **get_test_name()** (14 connections) — `test/test_client/util.py`
- **casedb/env.py** (13 connections) — `gen_epix/casedb/env.py`
- **omopdb/env.py** (12 connections) — `gen_epix/omopdb/env.py`
- **get_test_output_dir()** (12 connections) — `test/test_client/util.py`
- **casedb/app.py** (11 connections) — `gen_epix/casedb/app.py`
- **omopdb/app.py** (11 connections) — `gen_epix/omopdb/app.py`
- **seqdb/app.py** (11 connections) — `gen_epix/seqdb/app.py`
- **AppComposer** (11 connections) — `gen_epix/seqdb/env.py`
- **.get_test_client()** (10 connections) — `test/casedb/casedb_test_client.py`
- **commondb/app.py** (9 connections) — `gen_epix/commondb/app.py`
- *... and 153 more nodes in this community*

## Relationships

- [Commondb Enums & Demo Data](Commondb_Enums_&_Demo_Data.md) (58 shared connections)
- [ABAC API Routers](ABAC_API_Routers.md) (23 shared connections)
- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (14 shared connections)
- [ABAC Base Policies](ABAC_Base_Policies.md) (13 shared connections)
- [OAuth Flow Integration Tests](OAuth_Flow_Integration_Tests.md) (13 shared connections)
- [App & Abac Service Setup](App_&_Abac_Service_Setup.md) (10 shared connections)
- [Auth Exception Middleware](Auth_Exception_Middleware.md) (9 shared connections)
- [Test Utilities & Setup](Test_Utilities_&_Setup.md) (9 shared connections)
- [Seqdb Test Client](Seqdb_Test_Client.md) (7 shared connections)
- [Project Utility Functions](Project_Utility_Functions.md) (5 shared connections)
- [App Composition & Service Wiring](App_Composition_&_Service_Wiring.md) (5 shared connections)
- [API Exception Handling](API_Exception_Handling.md) (5 shared connections)

## Source Files

- `gen_epix/casedb/app.py`
- `gen_epix/casedb/domain/policy/permission.py`
- `gen_epix/casedb/env.py`
- `gen_epix/commondb/app.py`
- `gen_epix/commondb/app_setup.py`
- `gen_epix/commondb/config/__init__.py`
- `gen_epix/commondb/config/cfg.py`
- `gen_epix/commondb/env.py`
- `gen_epix/fastapp/api/openapi.py`
- `gen_epix/omopdb/app.py`
- `gen_epix/omopdb/env.py`
- `gen_epix/seqdb/app.py`
- `gen_epix/seqdb/env.py`
- `gen_epix/util.py`
- `run.py`
- `test/casedb/casedb_test_client.py`
- `test/casedb/performance/repository/test_casedb_repository_performance.py`
- `test/commondb/test_client/util.py`
- `test/end_to_end/casedb_seqdb_connection/envvar.py`
- `test/end_to_end/casedb_seqdb_connection/test_casedb_seqdb_connection.py`

## Audit Trail

- EXTRACTED: 543 (93%)
- INFERRED: 38 (7%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*