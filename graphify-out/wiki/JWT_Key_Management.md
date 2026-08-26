# JWT Key Management

> 101 nodes · cohesion 0.03

## Key Concepts

- **JWKSManager** (60 connections) — `test/test_client/oauth/jwks.py`
- **TestJWKSManager** (31 connections) — `test/test_client/oauth/test_jwks.py`
- **TestJWKSManagerIntegration** (8 connections) — `test/test_client/oauth/test_jwks.py`
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
- **.test_decode_token_header()** (3 connections) — `test/test_client/oauth/test_jwks.py`
- **.test_decode_token_header_invalid()** (3 connections) — `test/test_client/oauth/test_jwks.py`
- **.test_decode_token_payload()** (3 connections) — `test/test_client/oauth/test_jwks.py`
- *... and 76 more nodes in this community*

## Relationships

- [OIDC Provider & JWKS](OIDC_Provider_&_JWKS.md) (8 shared connections)
- [OAuth Client Store](OAuth_Client_Store.md) (1 shared connections)
- [HTTP Exception Classes](HTTP_Exception_Classes.md) (1 shared connections)
- [OIDC Provider Tests](OIDC_Provider_Tests.md) (1 shared connections)

## Source Files

- `test/test_client/oauth/jwks.py`
- `test/test_client/oauth/test_jwks.py`

## Audit Trail

- EXTRACTED: 150 (97%)
- INFERRED: 5 (3%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*