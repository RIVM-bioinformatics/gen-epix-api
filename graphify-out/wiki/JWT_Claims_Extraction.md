# JWT Claims Extraction

> 38 nodes · cohesion 0.06

## Key Concepts

- **.get_claims_from_jwt()** (10 connections) — `gen_epix/fastapp/services/auth/oauth_idp_client.py`
- **Any** (10 connections)
- **.__call__()** (9 connections) — `gen_epix/fastapp/services/auth/oauth_idp_client.py`
- **.get_jwk_from_jwt()** (7 connections) — `gen_epix/fastapp/services/auth/oauth_idp_client.py`
- **._validate_claims_from_userinfo()** (5 connections) — `gen_epix/fastapp/services/auth/oauth_idp_client.py`
- **._check_required_claims()** (4 connections) — `gen_epix/fastapp/services/auth/oauth_idp_client.py`
- **._decode_jwt_unverified()** (4 connections) — `gen_epix/fastapp/services/auth/oauth_idp_client.py`
- **.get_claims_from_userinfo()** (4 connections) — `gen_epix/fastapp/services/auth/oauth_idp_client.py`
- **._parse_authorization_header()** (4 connections) — `gen_epix/fastapp/services/auth/oauth_idp_client.py`
- **._refresh_signing_keys()** (4 connections) — `gen_epix/fastapp/services/auth/oauth_idp_client.py`
- **._verify_token()** (4 connections) — `gen_epix/fastapp/services/auth/oauth_idp_client.py`
- **._log_auth_error()** (3 connections) — `gen_epix/fastapp/services/auth/oauth_idp_client.py`
- **._log_keys_fetch_failure()** (3 connections) — `gen_epix/fastapp/services/auth/oauth_idp_client.py`
- **._log_keys_fetch_success()** (3 connections) — `gen_epix/fastapp/services/auth/oauth_idp_client.py`
- **._log_missing_authorization_header()** (3 connections) — `gen_epix/fastapp/services/auth/oauth_idp_client.py`
- **._log_unsupported_authorization_scheme()** (3 connections) — `gen_epix/fastapp/services/auth/oauth_idp_client.py`
- **._map_claims()** (3 connections) — `gen_epix/fastapp/services/auth/oauth_idp_client.py`
- **._validate_issuer()** (3 connections) — `gen_epix/fastapp/services/auth/oauth_idp_client.py`
- **.get_claims_from_jwt()** (2 connections) — `gen_epix/fastapp/services/auth/mock_idp_client.py`
- **.get_claims_from_userinfo()** (2 connections) — `gen_epix/fastapp/services/auth/mock_idp_client.py`
- **Return claims from jwt.** (2 connections) — `gen_epix/fastapp/services/auth/mock_idp_client.py`
- **Return claims from userinfo.** (2 connections) — `gen_epix/fastapp/services/auth/mock_idp_client.py`
- **._load_keys()** (2 connections) — `gen_epix/fastapp/services/auth/oauth_idp_client.py`
- **._parse_kid()** (2 connections) — `gen_epix/fastapp/services/auth/oauth_idp_client.py`
- **Request** (2 connections)
- *... and 13 more nodes in this community*

## Relationships

- [Auth Protocols & Structured Logging](Auth_Protocols_&_Structured_Logging.md) (21 shared connections)
- [Mock IDP Client](Mock_IDP_Client.md) (2 shared connections)
- [Authentication Service Base](Authentication_Service_Base.md) (1 shared connections)

## Source Files

- `gen_epix/fastapp/services/auth/mock_idp_client.py`
- `gen_epix/fastapp/services/auth/oauth_idp_client.py`

## Audit Trail

- EXTRACTED: 69 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*