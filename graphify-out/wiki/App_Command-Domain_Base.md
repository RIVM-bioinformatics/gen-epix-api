# App Command/Domain Base

> 65 nodes · cohesion 0.05

## Key Concepts

- **RemoteApp** (44 connections) — `gen_epix/fastapp/remote_app.py`
- **Command** (13 connections)
- **Any** (10 connections)
- **.__init__()** (9 connections) — `gen_epix/fastapp/remote_app.py`
- **.request()** (9 connections) — `gen_epix/fastapp/remote_app.py`
- **.stream()** (9 connections) — `gen_epix/fastapp/remote_app.py`
- **._execute_crud_operation()** (8 connections) — `gen_epix/fastapp/remote_app.py`
- **.get_client()** (8 connections) — `gen_epix/fastapp/remote_app.py`
- **TestInitAndProperties** (7 connections) — `test/fastapp/unit/test_fastapp_remote_app.py`
- **.create_generated_crud_route_handler()** (6 connections) — `gen_epix/fastapp/remote_app.py`
- **.get_headers()** (6 connections) — `gen_epix/fastapp/remote_app.py`
- **.register_generated_crud_route()** (6 connections) — `gen_epix/fastapp/remote_app.py`
- **.register_policy()** (6 connections) — `gen_epix/fastapp/remote_app.py`
- **.unregister_policy()** (6 connections) — `gen_epix/fastapp/remote_app.py`
- **._classify_exists_id_type()** (5 connections) — `gen_epix/fastapp/remote_app.py`
- **._content_to_obj()** (5 connections) — `gen_epix/fastapp/remote_app.py`
- **._exists_some_via_get()** (5 connections) — `gen_epix/fastapp/remote_app.py`
- **.get_route()** (5 connections) — `gen_epix/fastapp/remote_app.py`
- **._initialize_ssl_context()** (5 connections) — `gen_epix/fastapp/remote_app.py`
- **.register_route()** (5 connections) — `gen_epix/fastapp/remote_app.py`
- **.apply_handler()** (4 connections) — `gen_epix/fastapp/remote_app.py`
- **.get_timeout()** (4 connections) — `gen_epix/fastapp/remote_app.py`
- **.unregister_route()** (4 connections) — `gen_epix/fastapp/remote_app.py`
- **CrudCommand** (3 connections)
- **.protocol()** (3 connections) — `gen_epix/fastapp/remote_app.py`
- *... and 40 more nodes in this community*

## Relationships

- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (14 shared connections)
- [Casedb ABAC & Filter Logic](Casedb_ABAC_&_Filter_Logic.md) (5 shared connections)
- [Remote App Test Base](Remote_App_Test_Base.md) (5 shared connections)
- [ABAC Base Policies](ABAC_Base_Policies.md) (4 shared connections)
- [Domain Exception Classes](Domain_Exception_Classes.md) (4 shared connections)
- [OAuth Client Model](OAuth_Client_Model.md) (2 shared connections)
- [Commondb Remote App Client](Commondb_Remote_App_Client.md) (1 shared connections)
- [Core App Base Class](Core_App_Base_Class.md) (1 shared connections)
- [CRUD Endpoint Generator](CRUD_Endpoint_Generator.md) (1 shared connections)
- [FastApp Domain Registry Core](FastApp_Domain_Registry_Core.md) (1 shared connections)
- [App & Abac Service Setup](App_&_Abac_Service_Setup.md) (1 shared connections)
- [CRUD Endpoint Generation Helpers](CRUD_Endpoint_Generation_Helpers.md) (1 shared connections)

## Source Files

- `gen_epix/fastapp/remote_app.py`
- `test/fastapp/unit/test_fastapp_remote_app.py`

## Audit Trail

- EXTRACTED: 136 (95%)
- INFERRED: 7 (5%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*