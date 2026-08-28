# OIDCProvider

> 39 nodes

## Key Concepts

- **OIDCProvider** (20 connections) — `test/test_client/oauth/oidc_provider.py`
- **TestOIDCProviderIntegration** (11 connections) — `test/test_client/oauth/test_oidc_provider.py`
- **Any** (6 connections)
- **.setup_method()** (4 connections) — `test/test_client/oauth/test_oidc_provider.py`
- **.create_discovery_document()** (3 connections) — `test/test_client/oauth/oidc_provider.py`
- **.create_id_token()** (3 connections) — `test/test_client/oauth/oidc_provider.py`
- **.create_jwks_response()** (3 connections) — `test/test_client/oauth/oidc_provider.py`
- **.create_logout_response()** (3 connections) — `test/test_client/oauth/oidc_provider.py`
- **.create_userinfo_response()** (3 connections) — `test/test_client/oauth/oidc_provider.py`
- **.__init__()** (3 connections) — `test/test_client/oauth/oidc_provider.py`
- **.validate_id_token()** (3 connections) — `test/test_client/oauth/oidc_provider.py`
- **.extract_claims_from_scope()** (2 connections) — `test/test_client/oauth/oidc_provider.py`
- **.get_supported_algorithms()** (2 connections) — `test/test_client/oauth/oidc_provider.py`
- **.validate_nonce()** (2 connections) — `test/test_client/oauth/oidc_provider.py`
- **.test_claims_extraction_and_userinfo_integration()** (2 connections) — `test/test_client/oauth/test_oidc_provider.py`
- **.test_discovery_and_jwks_integration()** (2 connections) — `test/test_client/oauth/test_oidc_provider.py`
- **.test_end_to_end_id_token_workflow()** (2 connections) — `test/test_client/oauth/test_oidc_provider.py`
- **.test_logout_workflow_integration()** (2 connections) — `test/test_client/oauth/test_oidc_provider.py`
- **.test_nonce_validation_and_id_token_integration()** (2 connections) — `test/test_client/oauth/test_oidc_provider.py`
- **.test_userinfo_scope_based_claims_integration()** (2 connections) — `test/test_client/oauth/test_oidc_provider.py`
- **Create an OpenID Connect ID Token.** (1 connections) — `test/test_client/oauth/oidc_provider.py`
- **Validate and decode an ID token.** (1 connections) — `test/test_client/oauth/oidc_provider.py`
- **OpenID Connect provider implementation.** (1 connections) — `test/test_client/oauth/oidc_provider.py`
- **Create userinfo endpoint response based on scopes.** (1 connections) — `test/test_client/oauth/oidc_provider.py`
- **Initialize OIDC provider with JWKS manager.** (1 connections) — `test/test_client/oauth/oidc_provider.py`
- *... and 14 more nodes in this community*

## Relationships

- [JWKSManager](JWKSManager.md) (7 shared connections)
- [.setup_method](setup_method.md) (1 shared connections)
- [Client](Client.md) (1 shared connections)
- [server.py](server.py.md) (1 shared connections)
- [TestOIDCProvider](TestOIDCProvider.md) (1 shared connections)

## Source Files

- `test/test_client/oauth/oidc_provider.py`
- `test/test_client/oauth/test_oidc_provider.py`

## Audit Trail

- EXTRACTED: 51 (93%)
- INFERRED: 4 (7%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*