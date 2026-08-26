# Token Store Tests

> 68 nodes · cohesion 0.03

## Key Concepts

- **TestTokenStore** (39 connections) — `test/test_client/oauth/test_token_store.py`
- **.test_get_token_by_refresh_expired_token()** (3 connections) — `test/test_client/oauth/test_token_store.py`
- **.test_revoke_tokens_for_client_multiple_tokens()** (3 connections) — `test/test_client/oauth/test_token_store.py`
- **.test_cleanup_expired_tokens()** (2 connections) — `test/test_client/oauth/test_token_store.py`
- **.test_cleanup_expired_tokens_none_expired()** (2 connections) — `test/test_client/oauth/test_token_store.py`
- **.test_clear_store()** (2 connections) — `test/test_client/oauth/test_token_store.py`
- **.test_delete_refresh_token_existing()** (2 connections) — `test/test_client/oauth/test_token_store.py`
- **.test_delete_refresh_token_nonexistent()** (2 connections) — `test/test_client/oauth/test_token_store.py`
- **.test_delete_token_existing()** (2 connections) — `test/test_client/oauth/test_token_store.py`
- **.test_delete_token_nonexistent()** (2 connections) — `test/test_client/oauth/test_token_store.py`
- **.test_delete_token_without_refresh_token()** (2 connections) — `test/test_client/oauth/test_token_store.py`
- **.test_get_stats_comprehensive()** (2 connections) — `test/test_client/oauth/test_token_store.py`
- **.test_get_stats_empty_store()** (2 connections) — `test/test_client/oauth/test_token_store.py`
- **.test_get_token_by_refresh_existing()** (2 connections) — `test/test_client/oauth/test_token_store.py`
- **.test_get_token_by_refresh_nonexistent()** (2 connections) — `test/test_client/oauth/test_token_store.py`
- **.test_get_token_existing_valid()** (2 connections) — `test/test_client/oauth/test_token_store.py`
- **.test_get_token_expired_auto_cleanup()** (2 connections) — `test/test_client/oauth/test_token_store.py`
- **.test_get_token_info_existing_token()** (2 connections) — `test/test_client/oauth/test_token_store.py`
- **.test_get_token_info_expired_token()** (2 connections) — `test/test_client/oauth/test_token_store.py`
- **.test_get_token_info_nonexistent_token()** (2 connections) — `test/test_client/oauth/test_token_store.py`
- **.test_get_token_nonexistent()** (2 connections) — `test/test_client/oauth/test_token_store.py`
- **.test_list_active_tokens_all_clients()** (2 connections) — `test/test_client/oauth/test_token_store.py`
- **.test_list_active_tokens_empty_store()** (2 connections) — `test/test_client/oauth/test_token_store.py`
- **.test_list_active_tokens_filtered_by_client()** (2 connections) — `test/test_client/oauth/test_token_store.py`
- **.test_revoke_tokens_for_client_nonexistent_client()** (2 connections) — `test/test_client/oauth/test_token_store.py`
- *... and 43 more nodes in this community*

## Relationships

- [Token Store Unit Tests](Token_Store_Unit_Tests.md) (4 shared connections)
- [Token Store Lifecycle Tests](Token_Store_Lifecycle_Tests.md) (3 shared connections)

## Source Files

- `test/test_client/oauth/test_token_store.py`

## Audit Trail

- EXTRACTED: 72 (97%)
- INFERRED: 2 (3%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*