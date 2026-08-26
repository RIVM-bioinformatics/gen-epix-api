# Receiver App CLI

> 19 nodes · cohesion 0.15

## Key Concepts

- **ReceiverApp** (10 connections) — `test/end_to_end/client_credential_flow/apps/receiver_app.py`
- **receiver_app.py** (9 connections) — `test/end_to_end/client_credential_flow/apps/receiver_app.py`
- **receiver_app_cli.py** (5 connections) — `test/end_to_end/client_credential_flow/apps/receiver_app_cli.py`
- **._lifespan()** (5 connections) — `test/end_to_end/client_credential_flow/apps/receiver_app.py`
- **apps/__init__.py** (4 connections) — `test/end_to_end/client_credential_flow/apps/__init__.py`
- **ReceiverAppCLI** (4 connections) — `test/end_to_end/client_credential_flow/apps/receiver_app_cli.py`
- **.run()** (3 connections) — `test/end_to_end/client_credential_flow/apps/receiver_app_cli.py`
- **FastAPI** (3 connections)
- **.__init__()** (3 connections) — `test/end_to_end/client_credential_flow/apps/receiver_app.py`
- **._setup_routes()** (3 connections) — `test/end_to_end/client_credential_flow/apps/receiver_app.py`
- **main()** (2 connections) — `test/end_to_end/client_credential_flow/apps/receiver_app_cli.py`
- **ReceiverApp CLI Module This module provides a command-line interface for…** (1 connections) — `test/end_to_end/client_credential_flow/apps/receiver_app_cli.py`
- **Command-line interface for ReceiverApp.** (1 connections) — `test/end_to_end/client_credential_flow/apps/receiver_app_cli.py`
- **Start the ReceiverApp server. Args: port: Port to run the server on (default:…** (1 connections) — `test/end_to_end/client_credential_flow/apps/receiver_app_cli.py`
- **Main entry point for the CLI.** (1 connections) — `test/end_to_end/client_credential_flow/apps/receiver_app_cli.py`
- **ReceiverApp Module This module contains the ReceiverApp FastAPI application…** (1 connections) — `test/end_to_end/client_credential_flow/apps/receiver_app.py`
- **FastAPI app that receives and validates access tokens.** (1 connections) — `test/end_to_end/client_credential_flow/apps/receiver_app.py`
- **Initialize OIDC client on startup.** (1 connections) — `test/end_to_end/client_credential_flow/apps/receiver_app.py`
- **Setup FastAPI routes.** (1 connections) — `test/end_to_end/client_credential_flow/apps/receiver_app.py`

## Relationships

- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (5 shared connections)
- [OAuth IDP Client](OAuth_IDP_Client.md) (3 shared connections)
- [OIDC Requestor Test App](OIDC_Requestor_Test_App.md) (1 shared connections)

## Source Files

- `test/end_to_end/client_credential_flow/apps/__init__.py`
- `test/end_to_end/client_credential_flow/apps/receiver_app.py`
- `test/end_to_end/client_credential_flow/apps/receiver_app_cli.py`

## Audit Trail

- EXTRACTED: 32 (94%)
- INFERRED: 2 (6%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*