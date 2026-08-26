# Token Introspection Manager

> 26 nodes · cohesion 0.14

## Key Concepts

- **TokenIntrospectionManager** (28 connections) — `gen_epix/fastapp/services/auth/token_introspection_manager.py`
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
- **MonkeyPatch** (3 connections)
- **._fetch_introspection_endpoint()** (2 connections) — `gen_epix/fastapp/services/auth/token_introspection_manager.py`
- **._is_cached_introspection_token_inactive()** (2 connections) — `gen_epix/fastapp/services/auth/token_introspection_manager.py`
- **._validate_discovery_url()** (2 connections) — `gen_epix/fastapp/services/auth/token_introspection_manager.py`
- **._validate_introspection_interval()** (2 connections) — `gen_epix/fastapp/services/auth/token_introspection_manager.py`
- **.setup_class()** (2 connections) — `test/fastapp/unit/auth/test_fastapp_oauth_idp_client_introspection_endpoint.py`
- **Any** (1 connections)
- **Logger** (1 connections)
- **SSLContext** (1 connections)
- **Any** (1 connections)
- **scenario_ids** (1 connections)
- *... and 1 more nodes in this community*

## Relationships

- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (8 shared connections)
- [OAuth IDP Client](OAuth_IDP_Client.md) (3 shared connections)
- [Core App Base Class](Core_App_Base_Class.md) (3 shared connections)
- [OAuth Introspection Caching Tests](OAuth_Introspection_Caching_Tests.md) (2 shared connections)
- [IDP Retry Handling Tests](IDP_Retry_Handling_Tests.md) (2 shared connections)
- [OAuth IDP Client Tests](OAuth_IDP_Client_Tests.md) (1 shared connections)

## Source Files

- `gen_epix/fastapp/services/auth/token_introspection_manager.py`
- `test/fastapp/unit/auth/test_fastapp_oauth_idp_client_introspection_endpoint.py`

## Audit Trail

- EXTRACTED: 57 (88%)
- INFERRED: 8 (12%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*