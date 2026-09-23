# Role Mapping Generator

> 40 nodes · cohesion 0.06

## Key Concepts

- **RoleGenerator** (17 connections) — `gen_epix/commondb/domain/policy/permission.py`
- **test/test_client/util.py** (17 connections) — `test/test_client/util.py`
- **get_test_client()** (16 connections) — `test/commondb/test_client/util.py`
- **get_test_root_output_dir()** (13 connections) — `test/test_client/util.py`
- **TestStartup** (9 connections) — `test/casedb/performance/startup/test_casedb_startup_performance.py`
- **get_test_name()** (9 connections) — `test/test_client/util.py`
- **TestRead** (8 connections) — `test/casedb/performance/repository/test_casedb_repository_performance.py`
- **get_test_output_dir()** (7 connections) — `test/test_client/util.py`
- **parse_stats()** (6 connections) — `gen_epix/commondb/test/util.py`
- **.get_test_client()** (6 connections) — `test/seqdb/seqdb_test_client.py`
- **Enum** (5 connections)
- **.map_from_common_role_permission_sets()** (5 connections) — `gen_epix/commondb/domain/policy/permission.py`
- **.get_role_map()** (4 connections) — `gen_epix/commondb/domain/policy/permission.py`
- **.get_role_set_map()** (4 connections) — `gen_epix/commondb/domain/policy/permission.py`
- **.map_from_common_role_hierarchy()** (4 connections) — `gen_epix/commondb/domain/policy/permission.py`
- **Any** (4 connections)
- **Path** (4 connections)
- **.finalize_outputs()** (3 connections) — `test/casedb/performance/startup/test_casedb_startup_performance.py`
- **.test_startup_cprofile()** (3 connections) — `test/casedb/performance/startup/test_casedb_startup_performance.py`
- **test/fastapp/util.py** (3 connections) — `test/fastapp/util.py`
- **.finalize_outputs()** (2 connections) — `test/casedb/performance/repository/test_casedb_repository_performance.py`
- **.test_tear_down()** (2 connections) — `test/casedb/performance/startup/test_casedb_startup_performance.py`
- **.finalize_outputs()** (2 connections) — `test/casedb/performance/user_journey/test_casedb_user_journey_performance.py`
- **.finalize_outputs()** (2 connections) — `test/fastapp/performance/repository/test_fastapp_repository_performance.py`
- **generate_hex_strings()** (2 connections) — `test/test_client/util.py`
- *... and 15 more nodes in this community*

## Relationships

- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (30 shared connections)
- [FastAPI App Composition](FastAPI_App_Composition.md) (14 shared connections)
- [FastApp Test Fixtures](FastApp_Test_Fixtures.md) (9 shared connections)
- [Role Generation & Hierarchy](Role_Generation_&_Hierarchy.md) (4 shared connections)
- [Commondb ABAC Policies](Commondb_ABAC_Policies.md) (2 shared connections)
- [Domain Registry & ABAC Policies](Domain_Registry_&_ABAC_Policies.md) (2 shared connections)
- [Repository Fixture Tests](Repository_Fixture_Tests.md) (2 shared connections)
- [Casedb Endpoint Test Client](Casedb_Endpoint_Test_Client.md) (2 shared connections)
- [Protocol Creation Tests](Protocol_Creation_Tests.md) (2 shared connections)
- [Seqdb Sequence Retrieval Commands](Seqdb_Sequence_Retrieval_Commands.md) (1 shared connections)
- [Regex & Passthrough Filters](Regex_&_Passthrough_Filters.md) (1 shared connections)
- [User Invitation & Management](User_Invitation_&_Management.md) (1 shared connections)

## Source Files

- `gen_epix/commondb/domain/policy/permission.py`
- `gen_epix/commondb/test/util.py`
- `test/casedb/performance/repository/test_casedb_repository_performance.py`
- `test/casedb/performance/startup/test_casedb_startup_performance.py`
- `test/casedb/performance/user_journey/test_casedb_user_journey_performance.py`
- `test/commondb/test_client/util.py`
- `test/fastapp/performance/repository/test_fastapp_repository_performance.py`
- `test/fastapp/util.py`
- `test/seqdb/seqdb_test_client.py`
- `test/test_client/util.py`

## Audit Trail

- EXTRACTED: 112 (90%)
- INFERRED: 12 (10%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*