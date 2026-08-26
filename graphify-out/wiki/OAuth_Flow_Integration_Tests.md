# OAuth Flow Integration Tests

> 43 nodes · cohesion 0.08

## Key Concepts

- **ServerManager** (44 connections) — `test/test_client/server_manager.py`
- **test_client_credential_flow.py** (11 connections) — `test/end_to_end/client_credential_flow/test_client_credential_flow.py`
- **ServerType** (9 connections) — `test/test_client/enum.py`
- **server_manager.py** (9 connections) — `test/test_client/server_manager.py`
- **start_server.py** (8 connections) — `test/test_client/oauth/start_server.py`
- **start_server()** (7 connections) — `test/test_client/oauth/start_server.py`
- **test_authorization_code_flow.py** (6 connections) — `test/test_client/end_to_end/auth_code_flow/test_authorization_code_flow.py`
- **.start_oauth_server()** (6 connections) — `test/test_client/server_manager.py`
- **requestor_app()** (5 connections) — `test/end_to_end/client_credential_flow/test_client_credential_flow.py`
- **.stop()** (5 connections) — `test/test_client/server_manager.py`
- **oauth_server()** (4 connections) — `test/end_to_end/client_credential_flow/test_client_credential_flow.py`
- **receiver_app()** (4 connections) — `test/end_to_end/client_credential_flow/test_client_credential_flow.py`
- **oauth_server()** (4 connections) — `test/test_client/end_to_end/auth_code_flow/test_authorization_code_flow.py`
- **Enum** (4 connections)
- **fixture** (3 connections)
- **ServerTypeSet** (3 connections) — `test/test_client/enum.py`
- **main()** (3 connections) — `test/test_client/oauth/start_server.py`
- **setup_logging()** (3 connections) — `test/test_client/oauth/start_server.py`
- **Any** (3 connections)
- **._create_process_kwargs()** (3 connections) — `test/test_client/server_manager.py`
- **.__exit__()** (3 connections) — `test/test_client/server_manager.py`
- **.__init__()** (3 connections) — `test/test_client/server_manager.py`
- **.start()** (3 connections) — `test/test_client/server_manager.py`
- **.start_uvicorn_server()** (3 connections) — `test/test_client/server_manager.py`
- **._wait_for_server()** (3 connections) — `test/test_client/server_manager.py`
- *... and 18 more nodes in this community*

## Relationships

- [App Composition & Startup](App_Composition_&_Startup.md) (13 shared connections)
- [OIDC Requestor Test App](OIDC_Requestor_Test_App.md) (12 shared connections)
- [Commondb Enums & Demo Data](Commondb_Enums_&_Demo_Data.md) (9 shared connections)
- [Casedb CaseSet CRUD & Tests](Casedb_CaseSet_CRUD_&_Tests.md) (1 shared connections)
- [HTTP Exception Classes](HTTP_Exception_Classes.md) (1 shared connections)
- [CLI Test Runner](CLI_Test_Runner.md) (1 shared connections)

## Source Files

- `test/end_to_end/client_credential_flow/test_client_credential_flow.py`
- `test/test_client/end_to_end/auth_code_flow/test_authorization_code_flow.py`
- `test/test_client/enum.py`
- `test/test_client/oauth/start_server.py`
- `test/test_client/server_manager.py`

## Audit Trail

- EXTRACTED: 104 (95%)
- INFERRED: 5 (5%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*