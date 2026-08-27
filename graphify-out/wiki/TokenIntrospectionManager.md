# TokenIntrospectionManager

> 30 nodes · cohesion 0.12

## Key Concepts

- **TokenIntrospectionManager** (28 connections) — `gen_epix/fastapp/services/auth/token_introspection_manager.py`
- **test_fastapp_oauth_idp_client_introspection_endpoint.py** (9 connections) — `test/fastapp/unit/auth/test_fastapp_oauth_idp_client_introspection_endpoint.py`
- **TestOauthIdpClientIntrospectionEndpoint** (9 connections) — `test/fastapp/unit/auth/test_fastapp_oauth_idp_client_introspection_endpoint.py`
- **.introspect_token()** (8 connections) — `gen_epix/fastapp/services/auth/token_introspection_manager.py`
- **.__init__()** (7 connections) — `gen_epix/fastapp/services/auth/token_introspection_manager.py`
- **._now()** (6 connections) — `gen_epix/fastapp/services/auth/token_introspection_manager.py`
- **make_dummy_client()** (6 connections) — `test/fastapp/unit/auth/test_fastapp_oauth_idp_client_introspection_endpoint.py`
- **._get_cached_introspection_endpoint()** (4 connections) — `gen_epix/fastapp/services/auth/token_introspection_manager.py`
- **.test_fetch_introspection_endpoint_returns_endpoint()** (4 connections) — `test/fastapp/unit/auth/test_fastapp_oauth_idp_client_introspection_endpoint.py`
- **.test_get_cached_introspection_endpoint_respects_ttl_and_refetches()** (4 connections) — `test/fastapp/unit/auth/test_fastapp_oauth_idp_client_introspection_endpoint.py`
- **.test_get_cached_introspection_endpoint_uses_cache()** (4 connections) — `test/fastapp/unit/auth/test_fastapp_oauth_idp_client_introspection_endpoint.py`
- **._introspect_token_with_server()** (3 connections) — `gen_epix/fastapp/services/auth/token_introspection_manager.py`
- **._is_recheck_introspection()** (3 connections) — `gen_epix/fastapp/services/auth/token_introspection_manager.py`
- **._prune_expired_introspection_cache()** (3 connections) — `gen_epix/fastapp/services/auth/token_introspection_manager.py`
- **._update_introspection_cache()** (3 connections) — `gen_epix/fastapp/services/auth/token_introspection_manager.py`
- **DummyResponse** (3 connections) — `test/fastapp/unit/auth/test_fastapp_oauth_idp_client_introspection_endpoint.py`
- **MonkeyPatch** (3 connections)
- **._fetch_introspection_endpoint()** (2 connections) — `gen_epix/fastapp/services/auth/token_introspection_manager.py`
- **._is_cached_introspection_token_inactive()** (2 connections) — `gen_epix/fastapp/services/auth/token_introspection_manager.py`
- **._validate_discovery_url()** (2 connections) — `gen_epix/fastapp/services/auth/token_introspection_manager.py`
- **._validate_introspection_interval()** (2 connections) — `gen_epix/fastapp/services/auth/token_introspection_manager.py`
- **.setup_class()** (2 connections) — `test/fastapp/unit/auth/test_fastapp_oauth_idp_client_introspection_endpoint.py`
- **Any** (1 connections)
- **Logger** (1 connections)
- **SSLContext** (1 connections)
- *... and 5 more nodes in this community*

## Relationships

- [auth/__init__.py](auth-__init__.py.md) (7 shared connections)
- [OauthIdpClient](OauthIdpClient.md) (4 shared connections)
- [AuthTestClient](AuthTestClient.md) (4 shared connections)
- [TestOauthIdpClientIntrospection](TestOauthIdpClientIntrospection.md) (2 shared connections)
- [BaseLogItem](BaseLogItem.md) (2 shared connections)
- [Permission](Permission.md) (1 shared connections)
- [.create_client](create_client.md) (1 shared connections)

## Source Files

- `gen_epix/fastapp/services/auth/token_introspection_manager.py`
- `test/fastapp/unit/auth/test_fastapp_oauth_idp_client_introspection_endpoint.py`

## Audit Trail

- EXTRACTED: 65 (89%)
- INFERRED: 8 (11%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*