# AuthTestClient

> 42 nodes

## Key Concepts

- **AuthTestClient** (24 connections) — `test/fastapp/auth_test_client.py`
- **auth_test_client.py** (15 connections) — `test/fastapp/auth_test_client.py`
- **MockJWKAndToken** (11 connections) — `test/fastapp/unit/auth/mock_jwk_and_token.py`
- **TestAuth** (11 connections) — `test/fastapp/unit/auth/test_fastapp_auth.py`
- **TestOidcClientCredentials** (11 connections) — `test/fastapp/unit/auth/test_fastapp_auth.py`
- **test_fastapp_auth.py** (8 connections) — `test/fastapp/unit/auth/test_fastapp_auth.py`
- **patch** (6 connections)
- **.__init__()** (5 connections) — `test/fastapp/auth_test_client.py`
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
- **.test_invalid_claims()** (3 connections) — `test/fastapp/unit/auth/test_fastapp_auth.py`
- **.test_invalid_jwk()** (3 connections) — `test/fastapp/unit/auth/test_fastapp_auth.py`
- **mock_jwk_and_token.py** (3 connections) — `test/fastapp/unit/auth/mock_jwk_and_token.py`
- **.edit_claim()** (2 connections) — `test/fastapp/unit/auth/mock_jwk_and_token.py`
- **.edit_jwk()** (2 connections) — `test/fastapp/unit/auth/mock_jwk_and_token.py`
- **.__init__()** (2 connections) — `test/fastapp/unit/auth/mock_jwk_and_token.py`
- **.test_idp_retry_handling_preserves_existing_clients()** (2 connections) — `test/fastapp/unit/auth/test_fastapp_auth.py`
- *... and 17 more nodes in this community*

## Relationships

- [OauthIdpClient](OauthIdpClient.md) (9 shared connections)
- [CrudOperation](CrudOperation.md) (5 shared connections)
- [TokenIntrospectionManager](TokenIntrospectionManager.md) (4 shared connections)
- [App](App.md) (3 shared connections)
- [auth/__init__.py](auth-__init__.py.md) (2 shared connections)
- [TestOauthIdpClientIntrospection](TestOauthIdpClientIntrospection.md) (2 shared connections)
- [InMemoryOrganizationRepository](InMemoryOrganizationRepository.md) (2 shared connections)
- [FastApp UserManager Test Double](FastApp_UserManager_Test_Double.md) (2 shared connections)
- [AuthService](AuthService.md) (2 shared connections)
- [test_fastapp_rbac_service.py](test_fastapp_rbac_service.py.md) (2 shared connections)
- [casedb/domain/enum.py](casedb-domain-enum.py.md) (1 shared connections)
- [AuthEnv](AuthEnv.md) (1 shared connections)

## Source Files

- `test/fastapp/auth_test_client.py`
- `test/fastapp/unit/auth/mock_jwk_and_token.py`
- `test/fastapp/unit/auth/test_fastapp_auth.py`

## Audit Trail

- EXTRACTED: 95 (90%)
- INFERRED: 11 (10%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*