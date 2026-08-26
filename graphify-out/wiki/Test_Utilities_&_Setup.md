# Test Utilities & Setup

> 40 nodes · cohesion 0.08

## Key Concepts

- **test_casedb_custom.py** (20 connections) — `test/casedb/custom/test_casedb_custom.py`
- **test/util.py** (15 connections) — `gen_epix/commondb/test/util.py`
- **.get_user()** (9 connections) — `test/casedb/custom/test_casedb_custom.py`
- **TestManual** (8 connections) — `test/casedb/custom/test_casedb_custom.py`
- **set_log_level()** (7 connections) — `gen_epix/commondb/test/util.py`
- **Env** (7 connections)
- **TestStartup** (7 connections) — `test/casedb/performance/startup/test_casedb_startup_performance.py`
- **create_root_user_from_claims()** (6 connections) — `gen_epix/commondb/test/util.py`
- **parse_stats()** (6 connections) — `gen_epix/commondb/test/util.py`
- **.test_retrieve_cases_by_query()** (6 connections) — `test/casedb/custom/test_casedb_custom.py`
- **get_test_client()** (5 connections) — `test/casedb/custom/test_casedb_custom.py`
- **skip** (5 connections)
- **get_test_client()** (5 connections) — `test/casedb/integration/content/test_casedb_content.py`
- **._set_log_level()** (4 connections) — `gen_epix/commondb/test/test_client.py`
- **get_existing_root_user()** (4 connections) — `gen_epix/commondb/test/util.py`
- **.test_read_organization_access_case_policy()** (4 connections) — `test/casedb/custom/test_casedb_custom.py`
- **.test_read_organization_admin_policy()** (4 connections) — `test/casedb/custom/test_casedb_custom.py`
- **.test_read_user_case_policy()** (4 connections) — `test/casedb/custom/test_casedb_custom.py`
- **.test_retrieve_phylogenetic_tree()** (4 connections) — `test/casedb/custom/test_casedb_custom.py`
- **Env** (3 connections)
- **.test_retrieve_is_own_cases()** (3 connections) — `test/casedb/integration/content/test_casedb_content.py`
- **.finalize_outputs()** (3 connections) — `test/casedb/performance/startup/test_casedb_startup_performance.py`
- **.test_startup_cprofile()** (3 connections) — `test/casedb/performance/startup/test_casedb_startup_performance.py`
- **App** (2 connections)
- **Dynaconf** (2 connections)
- *... and 15 more nodes in this community*

## Relationships

- [Commondb Enums & Demo Data](Commondb_Enums_&_Demo_Data.md) (13 shared connections)
- [App Composition & Startup](App_Composition_&_Startup.md) (9 shared connections)
- [Casedb ABAC & Filter Logic](Casedb_ABAC_&_Filter_Logic.md) (7 shared connections)
- [Integration Test Client Helpers](Integration_Test_Client_Helpers.md) (4 shared connections)
- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (3 shared connections)
- [Casedb Test Client Helpers](Casedb_Test_Client_Helpers.md) (2 shared connections)
- [Upload/ETL Result Model](Upload-ETL_Result_Model.md) (1 shared connections)
- [Fastapp Repository Performance Tests](Fastapp_Repository_Performance_Tests.md) (1 shared connections)
- [Casedb CaseSet CRUD & Tests](Casedb_CaseSet_CRUD_&_Tests.md) (1 shared connections)
- [Casedb Domain CRUD Commands](Casedb_Domain_CRUD_Commands.md) (1 shared connections)
- [Case Domain Enums](Case_Domain_Enums.md) (1 shared connections)
- [Case Data Serialization](Case_Data_Serialization.md) (1 shared connections)

## Source Files

- `gen_epix/commondb/test/test_client.py`
- `gen_epix/commondb/test/util.py`
- `test/casedb/custom/test_casedb_custom.py`
- `test/casedb/integration/content/test_casedb_content.py`
- `test/casedb/performance/startup/test_casedb_startup_performance.py`

## Audit Trail

- EXTRACTED: 98 (93%)
- INFERRED: 7 (7%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*