# Remote App Test Base

> 37 nodes · cohesion 0.10

## Key Concepts

- **DummyCmd** (15 connections) — `test/fastapp/unit/test_fastapp_remote_app.py`
- **BaseRemoteAppTestCase** (11 connections) — `test/fastapp/unit/test_fastapp_remote_app.py`
- **TestHeadersAndApplyHandler** (11 connections) — `test/fastapp/unit/test_fastapp_remote_app.py`
- **.register_route_for()** (10 connections) — `test/fastapp/unit/test_fastapp_remote_app.py`
- **TestGeneratedCrudRoutes** (9 connections) — `test/fastapp/unit/test_fastapp_remote_app.py`
- **TestRouteRegistration** (8 connections) — `test/fastapp/unit/test_fastapp_remote_app.py`
- **set_fake_response()** (7 connections) — `test/fastapp/unit/test_fastapp_remote_app.py`
- **DummyCrud** (5 connections) — `test/fastapp/unit/test_fastapp_remote_app.py`
- **DummyModel** (5 connections) — `test/fastapp/unit/test_fastapp_remote_app.py`
- **scenario_ids** (5 connections)
- **TestAutoRegistration** (5 connections) — `test/fastapp/unit/test_fastapp_remote_app.py`
- **.test_create_generated_crud_handler_all_operations()** (5 connections) — `test/fastapp/unit/test_fastapp_remote_app.py`
- **DummyQueryFilter** (4 connections) — `test/fastapp/unit/test_fastapp_remote_app.py`
- **UnsupportedCrud** (4 connections) — `test/fastapp/unit/test_fastapp_remote_app.py`
- **.setup_method()** (3 connections) — `test/fastapp/unit/test_fastapp_remote_app.py`
- **.test_create_generated_crud_handler_exists_operations()** (3 connections) — `test/fastapp/unit/test_fastapp_remote_app.py`
- **.test_generated_handler_unsupported_return_type_raises()** (3 connections) — `test/fastapp/unit/test_fastapp_remote_app.py`
- **.test_apply_handler_success()** (3 connections) — `test/fastapp/unit/test_fastapp_remote_app.py`
- **.test_apply_handler_wraps_generic_exception()** (3 connections) — `test/fastapp/unit/test_fastapp_remote_app.py`
- **.test_apply_handler_wraps_http_status_error_with_status()** (3 connections) — `test/fastapp/unit/test_fastapp_remote_app.py`
- **.test_apply_handler_wraps_http_status_error_without_response()** (3 connections) — `test/fastapp/unit/test_fastapp_remote_app.py`
- **.test_apply_handler_wraps_request_error()** (3 connections) — `test/fastapp/unit/test_fastapp_remote_app.py`
- **.test_register_route_and_get_route()** (3 connections) — `test/fastapp/unit/test_fastapp_remote_app.py`
- **.test_unregister_route_and_missing()** (3 connections) — `test/fastapp/unit/test_fastapp_remote_app.py`
- **Command** (2 connections)
- *... and 12 more nodes in this community*

## Relationships

- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (18 shared connections)
- [App Command/Domain Base](App_Command-Domain_Base.md) (5 shared connections)
- [FastApp Domain Registry Core](FastApp_Domain_Registry_Core.md) (2 shared connections)
- [Fake HTTP Client Test Double](Fake_HTTP_Client_Test_Double.md) (2 shared connections)
- [Omopdb Remote App Client](Omopdb_Remote_App_Client.md) (1 shared connections)
- [FastApp Entity & Model Core](FastApp_Entity_&_Model_Core.md) (1 shared connections)

## Source Files

- `test/fastapp/unit/test_fastapp_remote_app.py`

## Audit Trail

- EXTRACTED: 82 (88%)
- INFERRED: 11 (12%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*