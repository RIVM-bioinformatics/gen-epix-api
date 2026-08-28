# .get_token

> 16 nodes · cohesion 0.12

## Key Concepts

- **.get_token()** (7 connections) — `test/test_client/oauth/token_store.py`
- **.delete_token()** (6 connections) — `test/test_client/oauth/token_store.py`
- **.get_token_by_refresh()** (4 connections) — `test/test_client/oauth/token_store.py`
- **.cleanup_expired_tokens()** (3 connections) — `test/test_client/oauth/token_store.py`
- **.delete_refresh_token()** (3 connections) — `test/test_client/oauth/token_store.py`
- **.get_token_info()** (3 connections) — `test/test_client/oauth/token_store.py`
- **.revoke_tokens_for_client()** (3 connections) — `test/test_client/oauth/token_store.py`
- **.token_exists()** (3 connections) — `test/test_client/oauth/token_store.py`
- **Delete a refresh token and its associated access token.** (1 connections) — `test/test_client/oauth/token_store.py`
- **Revoke all tokens for a specific client.** (1 connections) — `test/test_client/oauth/token_store.py`
- **Remove all expired tokens from the store.** (1 connections) — `test/test_client/oauth/token_store.py`
- **Check if a token exists and is not expired.** (1 connections) — `test/test_client/oauth/token_store.py`
- **Get token information without the actual token value.** (1 connections) — `test/test_client/oauth/token_store.py`
- **Retrieve a token by access token.** (1 connections) — `test/test_client/oauth/token_store.py`
- **Retrieve a token by refresh token.** (1 connections) — `test/test_client/oauth/token_store.py`
- **Delete a token and its refresh token mapping.** (1 connections) — `test/test_client/oauth/token_store.py`

## Relationships

- [Client](Client.md) (8 shared connections)
- [Token](Token.md) (2 shared connections)

## Source Files

- `test/test_client/oauth/token_store.py`

## Audit Trail

- EXTRACTED: 25 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*