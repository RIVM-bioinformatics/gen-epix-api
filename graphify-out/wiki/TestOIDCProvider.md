# TestOIDCProvider

> 10 nodes · cohesion 0.20

## Key Concepts

- **TestOIDCProvider** (40 connections) — `test/test_client/oauth/test_oidc_provider.py`
- **.test_create_id_token_with_nonce()** (2 connections) — `test/test_client/oauth/test_oidc_provider.py`
- **.test_create_logout_response_with_redirect_uri()** (2 connections) — `test/test_client/oauth/test_oidc_provider.py`
- **.test_extract_claims_from_scope_address()** (2 connections) — `test/test_client/oauth/test_oidc_provider.py`
- **.test_extract_claims_from_scope_multiple()** (2 connections) — `test/test_client/oauth/test_oidc_provider.py`
- **Test creating ID token with nonce.** (1 connections) — `test/test_client/oauth/test_oidc_provider.py`
- **Test cases for the OIDCProvider class.** (1 connections) — `test/test_client/oauth/test_oidc_provider.py`
- **Test extracting claims from address scope.** (1 connections) — `test/test_client/oauth/test_oidc_provider.py`
- **Test extracting claims from multiple scopes.** (1 connections) — `test/test_client/oauth/test_oidc_provider.py`
- **Test creating logout response with redirect URI.** (1 connections) — `test/test_client/oauth/test_oidc_provider.py`

## Relationships

- [Test extracting claims from openid scope only.](Test_extracting_claims_from_openid_scope_only.md) (3 shared connections)
- [JWKSManager](JWKSManager.md) (2 shared connections)
- [.test_create_discovery_document_supported_claims](test_create_discovery_document_supported_claims.md) (1 shared connections)
- [.test_create_discovery_document_auth_methods](test_create_discovery_document_auth_methods.md) (1 shared connections)
- [.test_create_discovery_document_signing_algorithms](test_create_discovery_document_signing_algorithms.md) (1 shared connections)
- [.test_create_discovery_document_additional_features](test_create_discovery_document_additional_features.md) (1 shared connections)
- [.test_create_id_token_basic](test_create_id_token_basic.md) (1 shared connections)
- [.test_create_id_token_with_auth_time](test_create_id_token_with_auth_time.md) (1 shared connections)
- [.test_create_id_token_with_additional_claims](test_create_id_token_with_additional_claims.md) (1 shared connections)
- [.test_create_id_token_with_custom_expiry](test_create_id_token_with_custom_expiry.md) (1 shared connections)
- [.test_validate_id_token](test_validate_id_token.md) (1 shared connections)
- [.test_create_userinfo_response_basic](test_create_userinfo_response_basic.md) (1 shared connections)

## Source Files

- `test/test_client/oauth/test_oidc_provider.py`

## Audit Trail

- EXTRACTED: 42 (95%)
- INFERRED: 2 (5%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*