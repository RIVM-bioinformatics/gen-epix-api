# Core App Base Class

> 121 nodes · cohesion 0.04

## Key Concepts

- **App** (126 connections) — `gen_epix/fastapp/app.py`
- **LogItem** (31 connections) — `gen_epix/fastapp/log.py`
- **test_fastapp_app_log_summarise.py** (26 connections) — `test/fastapp/unit/test_fastapp_app_log_summarise.py`
- **BaseLogItem** (20 connections) — `gen_epix/fastapp/log.py`
- **.create_log_message()** (18 connections) — `gen_epix/fastapp/app.py`
- **Command** (18 connections)
- **scenario_ids** (15 connections)
- **test_fastapp_app_cache.py** (14 connections) — `test/fastapp/unit/test_fastapp_app_cache.py`
- **Any** (13 connections)
- **.__init__()** (12 connections) — `gen_epix/fastapp/app.py`
- **.handle()** (8 connections) — `gen_epix/fastapp/app.py`
- **_Command** (8 connections) — `test/fastapp/unit/test_fastapp_app_cache.py`
- **._execute_command()** (7 connections) — `gen_epix/fastapp/app.py`
- **HandleNoResponseMiddleware** (7 connections) — `gen_epix/fastapp/middleware/handle_no_response.py`
- **test_create_log_message_uses_configured_threshold_and_sample_size()** (7 connections) — `test/fastapp/unit/test_fastapp_app_log_summarise.py`
- **test_create_log_message_with_large_command_stays_under_16384_bytes()** (7 connections) — `test/fastapp/unit/test_fastapp_app_log_summarise.py`
- **test_create_log_message_with_summarization_disabled_keeps_full_list()** (7 connections) — `test/fastapp/unit/test_fastapp_app_log_summarise.py`
- **.register_listener()** (6 connections) — `gen_epix/fastapp/app.py`
- **_LargeListCommand** (6 connections) — `test/fastapp/unit/test_fastapp_app_log_summarise.py`
- **_make_user()** (6 connections) — `test/fastapp/unit/test_fastapp_app_log_summarise.py`
- **._get_command_handler()** (5 connections) — `gen_epix/fastapp/app.py`
- **.register_policy()** (5 connections) — `gen_epix/fastapp/app.py`
- **.unregister_listener()** (5 connections) — `gen_epix/fastapp/app.py`
- **.unregister_policy()** (5 connections) — `gen_epix/fastapp/app.py`
- **Hashable** (5 connections)
- *... and 96 more nodes in this community*

## Relationships

- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (45 shared connections)
- [ABAC Base Policies](ABAC_Base_Policies.md) (6 shared connections)
- [App Composition & Service Wiring](App_Composition_&_Service_Wiring.md) (5 shared connections)
- [Auth Exception Middleware](Auth_Exception_Middleware.md) (4 shared connections)
- [Organization Service](Organization_Service.md) (3 shared connections)
- [Upload/ETL Result Model](Upload-ETL_Result_Model.md) (3 shared connections)
- [Mock IDP Client](Mock_IDP_Client.md) (3 shared connections)
- [OAuth IDP Client](OAuth_IDP_Client.md) (3 shared connections)
- [Token Introspection Manager](Token_Introspection_Manager.md) (3 shared connections)
- [Commondb Auth Tests](Commondb_Auth_Tests.md) (2 shared connections)
- [Commondb Upload Test Suite](Commondb_Upload_Test_Suite.md) (2 shared connections)
- [Omopdb Upload Test Suite](Omopdb_Upload_Test_Suite.md) (2 shared connections)

## Source Files

- `gen_epix/fastapp/app.py`
- `gen_epix/fastapp/log.py`
- `gen_epix/fastapp/middleware/handle_no_response.py`
- `test/fastapp/unit/test_fastapp_app_cache.py`
- `test/fastapp/unit/test_fastapp_app_log_summarise.py`

## Audit Trail

- EXTRACTED: 291 (80%)
- INFERRED: 73 (20%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*