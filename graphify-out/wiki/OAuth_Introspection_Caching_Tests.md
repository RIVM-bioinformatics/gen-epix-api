# OAuth Introspection Caching Tests

> 15 nodes · cohesion 0.25

## Key Concepts

- **TestOauthIdpClientIntrospection** (17 connections) — `test/fastapp/unit/auth/test_fastapp_oauth_idp_client_introspection.py`
- **._cache()** (8 connections) — `test/fastapp/unit/auth/test_fastapp_oauth_idp_client_introspection.py`
- **._now()** (6 connections) — `test/fastapp/unit/auth/test_fastapp_oauth_idp_client_introspection.py`
- **._enable_introspection()** (3 connections) — `test/fastapp/unit/auth/test_fastapp_oauth_idp_client_introspection.py`
- **.setup_class()** (3 connections) — `test/fastapp/unit/auth/test_fastapp_oauth_idp_client_introspection.py`
- **.test_cache_expiry_prunes_and_triggers_recheck()** (3 connections) — `test/fastapp/unit/auth/test_fastapp_oauth_idp_client_introspection.py`
- **.test_cached_active_within_interval_skips_recheck()** (3 connections) — `test/fastapp/unit/auth/test_fastapp_oauth_idp_client_introspection.py`
- **.test_interval_elapsed_triggers_single_recheck()** (3 connections) — `test/fastapp/unit/auth/test_fastapp_oauth_idp_client_introspection.py`
- **.test_introspection_inactive_denies()** (3 connections) — `test/fastapp/unit/auth/test_fastapp_oauth_idp_client_introspection.py`
- **.test_recheck_to_inactive_then_denies()** (3 connections) — `test/fastapp/unit/auth/test_fastapp_oauth_idp_client_introspection.py`
- **.test_claim_map_validator_rejects_bad_types()** (2 connections) — `test/fastapp/unit/auth/test_fastapp_oauth_idp_client_introspection.py`
- **.test_introspection_failure()** (2 connections) — `test/fastapp/unit/auth/test_fastapp_oauth_idp_client_introspection.py`
- **Any** (1 connections)
- **scenario_ids** (1 connections)
- **.test_introspection_populates_cache()** (1 connections) — `test/fastapp/unit/auth/test_fastapp_oauth_idp_client_introspection.py`

## Relationships

- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (2 shared connections)
- [IDP Retry Handling Tests](IDP_Retry_Handling_Tests.md) (2 shared connections)
- [Token Introspection Manager](Token_Introspection_Manager.md) (2 shared connections)
- [OAuth IDP Client](OAuth_IDP_Client.md) (1 shared connections)

## Source Files

- `test/fastapp/unit/auth/test_fastapp_oauth_idp_client_introspection.py`

## Audit Trail

- EXTRACTED: 30 (91%)
- INFERRED: 3 (9%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*