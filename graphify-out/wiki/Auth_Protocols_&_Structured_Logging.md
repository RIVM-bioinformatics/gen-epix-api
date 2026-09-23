# Auth Protocols & Structured Logging

> 179 nodes · cohesion 0.02

## Key Concepts

- **OauthIdpClient** (82 connections) — `gen_epix/fastapp/services/auth/oauth_idp_client.py`
- **OidcServerCfg** (38 connections) — `gen_epix/fastapp/services/auth/model.py`
- **.create_client()** (38 connections) — `test/fastapp/unit/services/auth/test_fastapp_oauth_idp_client.py`
- **TokenIntrospectionManager** (30 connections) — `gen_epix/fastapp/services/auth/token_introspection_manager.py`
- **commondb/services/client.py** (28 connections) — `gen_epix/commondb/services/client.py`
- **auth/model.py** (27 connections) — `gen_epix/fastapp/services/auth/model.py`
- **IdentityProvider** (27 connections) — `gen_epix/fastapp/services/auth/model.py`
- **oauth_idp_client.py** (27 connections) — `gen_epix/fastapp/services/auth/oauth_idp_client.py`
- **IdpClient** (23 connections) — `gen_epix/fastapp/services/auth/idp_client.py`
- **test_fastapp_oauth_idp_client.py** (23 connections) — `test/fastapp/unit/services/auth/test_fastapp_oauth_idp_client.py`
- **AuthProtocol** (21 connections) — `gen_epix/fastapp/enum.py`
- **BaseLogItem** (20 connections) — `gen_epix/fastapp/log.py`
- **BaseOauthIdpClientTestCase** (17 connections) — `test/fastapp/unit/services/auth/test_fastapp_oauth_idp_client.py`
- **mock_idp_client.py** (16 connections) — `gen_epix/fastapp/services/auth/mock_idp_client.py`
- **OAuthFlow** (15 connections) — `gen_epix/fastapp/enum.py`
- **idp_client.py** (13 connections) — `gen_epix/fastapp/services/auth/idp_client.py`
- **token_introspection_manager.py** (12 connections) — `gen_epix/fastapp/services/auth/token_introspection_manager.py`
- **TestClaimsFromJwt** (12 connections) — `test/fastapp/unit/services/auth/test_fastapp_oauth_idp_client.py`
- **TestInitAndConfig** (12 connections) — `test/fastapp/unit/services/auth/test_fastapp_oauth_idp_client.py`
- **log.py** (11 connections) — `gen_epix/fastapp/log.py`
- **.__init__()** (10 connections) — `gen_epix/commondb/services/client.py`
- **.__init__()** (10 connections) — `gen_epix/fastapp/services/auth/oauth_idp_client.py`
- **test_fastapp_oauth_idp_client_introspection.py** (10 connections) — `test/fastapp/unit/auth/test_fastapp_oauth_idp_client_introspection.py`
- **TestCall** (10 connections) — `test/fastapp/unit/services/auth/test_fastapp_oauth_idp_client.py`
- **TestJwkFetching** (10 connections) — `test/fastapp/unit/services/auth/test_fastapp_oauth_idp_client.py`
- *... and 154 more nodes in this community*

## Relationships

- [Authentication Service Base](Authentication_Service_Base.md) (43 shared connections)
- [JWT Claims Extraction](JWT_Claims_Extraction.md) (28 shared connections)
- [Auth Test Clients & Mocks](Auth_Test_Clients_&_Mocks.md) (21 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (19 shared connections)
- [Commondb Client](Commondb_Client.md) (19 shared connections)
- [Application Log Items](Application_Log_Items.md) (12 shared connections)
- [Mock IDP Client](Mock_IDP_Client.md) (9 shared connections)
- [Token Introspection Cache](Token_Introspection_Cache.md) (9 shared connections)
- [Command Exception Handling](Command_Exception_Handling.md) (6 shared connections)
- [OIDC Client Test App](OIDC_Client_Test_App.md) (6 shared connections)
- [Receiver App CLI](Receiver_App_CLI.md) (6 shared connections)
- [FastApp HTTP Client](FastApp_HTTP_Client.md) (5 shared connections)

## Source Files

- `gen_epix/commondb/services/client.py`
- `gen_epix/fastapp/enum.py`
- `gen_epix/fastapp/log.py`
- `gen_epix/fastapp/services/auth/idp_client.py`
- `gen_epix/fastapp/services/auth/mock_idp_client.py`
- `gen_epix/fastapp/services/auth/model.py`
- `gen_epix/fastapp/services/auth/oauth_idp_client.py`
- `gen_epix/fastapp/services/auth/service.py`
- `gen_epix/fastapp/services/auth/token_introspection_manager.py`
- `test/end_to_end/client_credential_flow/apps/__init__.py`
- `test/end_to_end/client_credential_flow/apps/receiver_app.py`
- `test/end_to_end/client_credential_flow/apps/requestor_app.py`
- `test/fastapp/unit/auth/test_fastapp_oauth_idp_client_introspection.py`
- `test/fastapp/unit/auth/test_fastapp_oauth_idp_client_introspection_endpoint.py`
- `test/fastapp/unit/services/auth/test_fastapp_idp_client.py`
- `test/fastapp/unit/services/auth/test_fastapp_oauth_idp_client.py`

## Audit Trail

- EXTRACTED: 496 (87%)
- INFERRED: 74 (13%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*