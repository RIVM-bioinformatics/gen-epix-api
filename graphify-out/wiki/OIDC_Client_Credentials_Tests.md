# OIDC Client Credentials Tests

> 16 nodes · cohesion 0.17

## Key Concepts

- **TestOidcClientCredentials** (11 connections) — `test/fastapp/unit/auth/test_fastapp_auth.py`
- **patch** (6 connections)
- **.test_custom_parameters()** (4 connections) — `test/fastapp/unit/auth/test_fastapp_auth.py`
- **.test_http_error_with_retries()** (4 connections) — `test/fastapp/unit/auth/test_fastapp_auth.py`
- **.test_invalid_response_format()** (4 connections) — `test/fastapp/unit/auth/test_fastapp_auth.py`
- **.test_missing_token_endpoint()** (4 connections) — `test/fastapp/unit/auth/test_fastapp_auth.py`
- **.test_network_failure()** (4 connections) — `test/fastapp/unit/auth/test_fastapp_auth.py`
- **.test_successful_token_retrieval()** (4 connections) — `test/fastapp/unit/auth/test_fastapp_auth.py`
- **scenario_ids** (2 connections)
- **Test the OidcClient retrieve_jwt_with_client_credentials_flow method.** (1 connections) — `test/fastapp/unit/auth/test_fastapp_auth.py`
- **Test successful JWT token retrieval with client credentials flow.** (1 connections) — `test/fastapp/unit/auth/test_fastapp_auth.py`
- **Test that HTTP errors trigger retries and eventually raise…** (1 connections) — `test/fastapp/unit/auth/test_fastapp_auth.py`
- **Test that missing token endpoint raises ServiceUnavailableError.** (1 connections) — `test/fastapp/unit/auth/test_fastapp_auth.py`
- **Test handling of invalid response format (missing access_token).** (1 connections) — `test/fastapp/unit/auth/test_fastapp_auth.py`
- **Test handling of network failures during token retrieval.** (1 connections) — `test/fastapp/unit/auth/test_fastapp_auth.py`
- **Test that custom headers, max_retries, and base_delay are properly used.** (1 connections) — `test/fastapp/unit/auth/test_fastapp_auth.py`

## Relationships

- [OAuth IDP Client](OAuth_IDP_Client.md) (6 shared connections)
- [IDP Retry Handling Tests](IDP_Retry_Handling_Tests.md) (4 shared connections)

## Source Files

- `test/fastapp/unit/auth/test_fastapp_auth.py`

## Audit Trail

- EXTRACTED: 29 (97%)
- INFERRED: 1 (3%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*