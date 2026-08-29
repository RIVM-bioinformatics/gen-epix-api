# OauthIdpClient

> 45 nodes

## Key Concepts

- **OauthIdpClient** (78 connections) — `gen_epix/fastapp/services/auth/oauth_idp_client.py`
- **Any** (10 connections)
- **.__call__()** (9 connections) — `gen_epix/fastapp/services/auth/oauth_idp_client.py`
- **.get_claims_from_jwt()** (9 connections) — `gen_epix/fastapp/services/auth/oauth_idp_client.py`
- **.__init__()** (9 connections) — `gen_epix/fastapp/services/auth/oauth_idp_client.py`
- **.get_jwk_from_jwt()** (8 connections) — `gen_epix/fastapp/services/auth/oauth_idp_client.py`
- **.retrieve_jwt_with_client_credentials_flow()** (6 connections) — `gen_epix/fastapp/services/auth/oauth_idp_client.py`
- **.update_server_config_from_discovery()** (5 connections) — `gen_epix/fastapp/services/auth/oauth_idp_client.py`
- **._validate_claims_from_userinfo()** (4 connections) — `gen_epix/fastapp/services/auth/oauth_idp_client.py`
- **._verify_token()** (4 connections) — `gen_epix/fastapp/services/auth/oauth_idp_client.py`
- **._check_required_claims()** (3 connections) — `gen_epix/fastapp/services/auth/oauth_idp_client.py`
- **._decode_jwt_unverified()** (3 connections) — `gen_epix/fastapp/services/auth/oauth_idp_client.py`
- **._generate_token_data()** (3 connections) — `gen_epix/fastapp/services/auth/oauth_idp_client.py`
- **.get_claims_from_userinfo()** (3 connections) — `gen_epix/fastapp/services/auth/oauth_idp_client.py`
- **._get_token_endpoint()** (3 connections) — `gen_epix/fastapp/services/auth/oauth_idp_client.py`
- **._log_auth_error()** (3 connections) — `gen_epix/fastapp/services/auth/oauth_idp_client.py`
- **._map_claims()** (3 connections) — `gen_epix/fastapp/services/auth/oauth_idp_client.py`
- **._parse_authorization_header()** (3 connections) — `gen_epix/fastapp/services/auth/oauth_idp_client.py`
- **._refresh_signing_keys()** (3 connections) — `gen_epix/fastapp/services/auth/oauth_idp_client.py`
- **._request_token_with_retries()** (3 connections) — `gen_epix/fastapp/services/auth/oauth_idp_client.py`
- **._validate_issuer()** (3 connections) — `gen_epix/fastapp/services/auth/oauth_idp_client.py`
- **.get_identity_provider()** (2 connections) — `gen_epix/fastapp/services/auth/oauth_idp_client.py`
- **._load_keys()** (2 connections) — `gen_epix/fastapp/services/auth/oauth_idp_client.py`
- **._log_failed_token_retrieval_attempts()** (2 connections) — `gen_epix/fastapp/services/auth/oauth_idp_client.py`
- **._log_keys_fetch_failure()** (2 connections) — `gen_epix/fastapp/services/auth/oauth_idp_client.py`
- *... and 20 more nodes in this community*

## Relationships

- [auth/__init__.py](auth-__init__.py.md) (13 shared connections)
- [.create_client](create_client_2.md) (12 shared connections)
- [AuthTestClient](AuthTestClient.md) (9 shared connections)
- [TokenIntrospectionManager](TokenIntrospectionManager.md) (4 shared connections)
- [AuthService](AuthService.md) (3 shared connections)
- [RequestorApp](RequestorApp.md) (2 shared connections)
- [CrudOperation](CrudOperation.md) (2 shared connections)
- [BaseLogItem](BaseLogItem.md) (2 shared connections)
- [.create_local_or_remote_app](create_local_or_remote_app.md) (1 shared connections)
- [CommondbRemoteApp](CommondbRemoteApp.md) (1 shared connections)
- [Permission](Permission.md) (1 shared connections)
- [TestOauthIdpClientIntrospection](TestOauthIdpClientIntrospection.md) (1 shared connections)

## Source Files

- `gen_epix/fastapp/services/auth/oauth_idp_client.py`

## Audit Trail

- EXTRACTED: 113 (86%)
- INFERRED: 19 (14%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*