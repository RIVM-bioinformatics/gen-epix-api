# JWKSManager

> 107 nodes

## Key Concepts

- **JWKSManager** (60 connections) — `test/test_client/oauth/jwks.py`
- **TestJWKSManager** (31 connections) — `test/test_client/oauth/test_jwks.py`
- **TestJWKSManagerIntegration** (8 connections) — `test/test_client/oauth/test_jwks.py`
- **test_oidc_provider.py** (8 connections) — `test/test_client/oauth/test_oidc_provider.py`
- **jwks.py** (7 connections) — `test/test_client/oauth/jwks.py`
- **oidc_provider.py** (7 connections) — `test/test_client/oauth/oidc_provider.py`
- **Any** (6 connections)
- **test_jwks.py** (5 connections) — `test/test_client/oauth/test_jwks.py`
- **.create_id_token()** (4 connections) — `test/test_client/oauth/jwks.py`
- **.create_jwt()** (4 connections) — `test/test_client/oauth/jwks.py`
- **._generate_key_pair()** (4 connections) — `test/test_client/oauth/jwks.py`
- **.verify_jwt()** (4 connections) — `test/test_client/oauth/jwks.py`
- **.decode_token_header()** (3 connections) — `test/test_client/oauth/jwks.py`
- **.decode_token_payload()** (3 connections) — `test/test_client/oauth/jwks.py`
- **.get_public_keys()** (3 connections) — `test/test_client/oauth/jwks.py`
- **.__init__()** (3 connections) — `test/test_client/oauth/jwks.py`
- **.rotate_keys()** (3 connections) — `test/test_client/oauth/jwks.py`
- **.validate_token_signature()** (3 connections) — `test/test_client/oauth/jwks.py`
- **.test_create_id_token_basic()** (3 connections) — `test/test_client/oauth/test_jwks.py`
- **.test_create_id_token_expiration()** (3 connections) — `test/test_client/oauth/test_jwks.py`
- **.test_create_id_token_with_additional_claims()** (3 connections) — `test/test_client/oauth/test_jwks.py`
- **.test_create_id_token_with_nonce()** (3 connections) — `test/test_client/oauth/test_jwks.py`
- **.test_create_jwt_basic()** (3 connections) — `test/test_client/oauth/test_jwks.py`
- **.test_create_jwt_includes_kid_in_header()** (3 connections) — `test/test_client/oauth/test_jwks.py`
- **.test_create_jwt_with_custom_kid()** (3 connections) — `test/test_client/oauth/test_jwks.py`
- *... and 82 more nodes in this community*

## Relationships

- [OIDCProvider](OIDCProvider.md) (7 shared connections)
- [Client](Client.md) (3 shared connections)
- [server.py](server.py.md) (3 shared connections)
- [TestOIDCProvider](TestOIDCProvider.md) (2 shared connections)
- [CrudOperation](CrudOperation.md) (1 shared connections)

## Source Files

- `test/test_client/oauth/jwks.py`
- `test/test_client/oauth/oidc_provider.py`
- `test/test_client/oauth/test_jwks.py`
- `test/test_client/oauth/test_oidc_provider.py`

## Audit Trail

- EXTRACTED: 165 (97%)
- INFERRED: 5 (3%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*