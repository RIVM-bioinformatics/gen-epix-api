# Auth Test Clients & Mocks

> 57 nodes · cohesion 0.06

## Key Concepts

- **AuthTestClient** (25 connections) — `test/fastapp/auth_test_client.py`
- **TestOauthIdpClientIntrospection** (18 connections) — `test/fastapp/unit/auth/test_fastapp_oauth_idp_client_introspection.py`
- **auth_test_client.py** (15 connections) — `test/fastapp/auth_test_client.py`
- **MockJWKAndToken** (11 connections) — `test/fastapp/unit/auth/mock_jwk_and_token.py`
- **TestAuth** (11 connections) — `test/fastapp/unit/auth/test_fastapp_auth.py`
- **TestOidcClientCredentials** (11 connections) — `test/fastapp/unit/auth/test_fastapp_auth.py`
- **test/fastapp/user_manager.py** (11 connections) — `test/fastapp/user_manager.py`
- **test_fastapp_auth.py** (8 connections) — `test/fastapp/unit/auth/test_fastapp_auth.py`
- **._cache()** (8 connections) — `test/fastapp/unit/auth/test_fastapp_oauth_idp_client_introspection.py`
- **patch** (6 connections)
- **._now()** (6 connections) — `test/fastapp/unit/auth/test_fastapp_oauth_idp_client_introspection.py`
- **.oauth_idp_client()** (5 connections) — `test/fastapp/unit/auth/test_fastapp_auth.py`
- **.get_test_client()** (4 connections) — `test/fastapp/auth_test_client.py`
- **._get_token()** (4 connections) — `test/fastapp/unit/auth/mock_jwk_and_token.py`
- **get_test_client()** (4 connections) — `test/fastapp/unit/auth/test_fastapp_auth.py`
- **.test_custom_parameters()** (4 connections) — `test/fastapp/unit/auth/test_fastapp_auth.py`
- **.test_http_error_with_retries()** (4 connections) — `test/fastapp/unit/auth/test_fastapp_auth.py`
- **.test_invalid_response_format()** (4 connections) — `test/fastapp/unit/auth/test_fastapp_auth.py`
- **.test_missing_token_endpoint()** (4 connections) — `test/fastapp/unit/auth/test_fastapp_auth.py`
- **.test_network_failure()** (4 connections) — `test/fastapp/unit/auth/test_fastapp_auth.py`
- **.test_successful_token_retrieval()** (4 connections) — `test/fastapp/unit/auth/test_fastapp_auth.py`
- **mock_jwk_and_token.py** (3 connections) — `test/fastapp/unit/auth/mock_jwk_and_token.py`
- **.test_invalid_claims()** (3 connections) — `test/fastapp/unit/auth/test_fastapp_auth.py`
- **.test_invalid_jwk()** (3 connections) — `test/fastapp/unit/auth/test_fastapp_auth.py`
- **._enable_introspection()** (3 connections) — `test/fastapp/unit/auth/test_fastapp_oauth_idp_client_introspection.py`
- *... and 32 more nodes in this community*

## Relationships

- [Auth Protocols & Structured Logging](Auth_Protocols_&_Structured_Logging.md) (21 shared connections)
- [FastApp Test Fixtures](FastApp_Test_Fixtures.md) (5 shared connections)
- [RBAC Service Tests](RBAC_Service_Tests.md) (5 shared connections)
- [Auth Claim Utilities](Auth_Claim_Utilities.md) (5 shared connections)
- [Authentication Service Base](Authentication_Service_Base.md) (2 shared connections)
- [Seqdb Sequence Retrieval Commands](Seqdb_Sequence_Retrieval_Commands.md) (2 shared connections)
- [Command Exception Handling](Command_Exception_Handling.md) (2 shared connections)
- [Domain Registry & ABAC Policies](Domain_Registry_&_ABAC_Policies.md) (2 shared connections)
- [Auth Exception Middleware](Auth_Exception_Middleware.md) (1 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (1 shared connections)
- [OAuth Client Model](OAuth_Client_Model.md) (1 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (1 shared connections)

## Source Files

- `test/fastapp/auth_test_client.py`
- `test/fastapp/unit/auth/mock_jwk_and_token.py`
- `test/fastapp/unit/auth/test_fastapp_auth.py`
- `test/fastapp/unit/auth/test_fastapp_oauth_idp_client_introspection.py`
- `test/fastapp/user_manager.py`

## Audit Trail

- EXTRACTED: 131 (90%)
- INFERRED: 14 (10%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*