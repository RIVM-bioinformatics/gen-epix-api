# OIDC Provider & JWKS

> 47 nodes · cohesion 0.05

## Key Concepts

- **OIDCProvider** (20 connections) — `test/test_client/oauth/oidc_provider.py`
- **TestOIDCProviderIntegration** (11 connections) — `test/test_client/oauth/test_oidc_provider.py`
- **test_oidc_provider.py** (8 connections) — `test/test_client/oauth/test_oidc_provider.py`
- **jwks.py** (7 connections) — `test/test_client/oauth/jwks.py`
- **oidc_provider.py** (7 connections) — `test/test_client/oauth/oidc_provider.py`
- **Any** (6 connections)
- **.setup_method()** (4 connections) — `test/test_client/oauth/test_oidc_provider.py`
- **.create_discovery_document()** (3 connections) — `test/test_client/oauth/oidc_provider.py`
- **.create_id_token()** (3 connections) — `test/test_client/oauth/oidc_provider.py`
- **.create_jwks_response()** (3 connections) — `test/test_client/oauth/oidc_provider.py`
- **.create_logout_response()** (3 connections) — `test/test_client/oauth/oidc_provider.py`
- **.create_userinfo_response()** (3 connections) — `test/test_client/oauth/oidc_provider.py`
- **.__init__()** (3 connections) — `test/test_client/oauth/oidc_provider.py`
- **.validate_id_token()** (3 connections) — `test/test_client/oauth/oidc_provider.py`
- **.setup_method()** (3 connections) — `test/test_client/oauth/test_oidc_provider.py`
- **.extract_claims_from_scope()** (2 connections) — `test/test_client/oauth/oidc_provider.py`
- **.get_supported_algorithms()** (2 connections) — `test/test_client/oauth/oidc_provider.py`
- **.validate_nonce()** (2 connections) — `test/test_client/oauth/oidc_provider.py`
- **.test_claims_extraction_and_userinfo_integration()** (2 connections) — `test/test_client/oauth/test_oidc_provider.py`
- **.test_discovery_and_jwks_integration()** (2 connections) — `test/test_client/oauth/test_oidc_provider.py`
- **.test_end_to_end_id_token_workflow()** (2 connections) — `test/test_client/oauth/test_oidc_provider.py`
- **.test_logout_workflow_integration()** (2 connections) — `test/test_client/oauth/test_oidc_provider.py`
- **.test_nonce_validation_and_id_token_integration()** (2 connections) — `test/test_client/oauth/test_oidc_provider.py`
- **.test_userinfo_scope_based_claims_integration()** (2 connections) — `test/test_client/oauth/test_oidc_provider.py`
- **JSON Web Key Set (JWKS) Manager This module handles JWT token generation,…** (1 connections) — `test/test_client/oauth/jwks.py`
- *... and 22 more nodes in this community*

## Relationships

- [JWT Key Management](JWT_Key_Management.md) (8 shared connections)
- [OAuth Client Store](OAuth_Client_Store.md) (3 shared connections)
- [HTTP Exception Classes](HTTP_Exception_Classes.md) (3 shared connections)
- [OIDC Provider Tests](OIDC_Provider_Tests.md) (3 shared connections)
- [Casedb CaseSet CRUD & Tests](Casedb_CaseSet_CRUD_&_Tests.md) (1 shared connections)

## Source Files

- `test/test_client/oauth/jwks.py`
- `test/test_client/oauth/oidc_provider.py`
- `test/test_client/oauth/test_oidc_provider.py`

## Audit Trail

- EXTRACTED: 69 (95%)
- INFERRED: 4 (5%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*