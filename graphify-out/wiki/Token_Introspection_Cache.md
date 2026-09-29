# Token Introspection Cache

> 18 nodes · cohesion 0.14

## Key Concepts

- **.introspect_token()** (8 connections) — `gen_epix/fastapp/services/auth/token_introspection_manager.py`
- **._now()** (7 connections) — `gen_epix/fastapp/services/auth/token_introspection_manager.py`
- **._get_cached_introspection_endpoint()** (5 connections) — `gen_epix/fastapp/services/auth/token_introspection_manager.py`
- **._introspect_token_with_server()** (4 connections) — `gen_epix/fastapp/services/auth/token_introspection_manager.py`
- **._is_recheck_introspection()** (4 connections) — `gen_epix/fastapp/services/auth/token_introspection_manager.py`
- **._prune_expired_introspection_cache()** (4 connections) — `gen_epix/fastapp/services/auth/token_introspection_manager.py`
- **._update_introspection_cache()** (4 connections) — `gen_epix/fastapp/services/auth/token_introspection_manager.py`
- **._fetch_introspection_endpoint()** (3 connections) — `gen_epix/fastapp/services/auth/token_introspection_manager.py`
- **._is_cached_introspection_token_inactive()** (3 connections) — `gen_epix/fastapp/services/auth/token_introspection_manager.py`
- **Any** (1 connections)
- **Return cached introspection endpoint.** (1 connections) — `gen_epix/fastapp/services/auth/token_introspection_manager.py`
- **Prune expired introspection cache.** (1 connections) — `gen_epix/fastapp/services/auth/token_introspection_manager.py`
- **Return whether cached introspection token inactive.** (1 connections) — `gen_epix/fastapp/services/auth/token_introspection_manager.py`
- **Return whether recheck introspection.** (1 connections) — `gen_epix/fastapp/services/auth/token_introspection_manager.py`
- **Update introspection cache.** (1 connections) — `gen_epix/fastapp/services/auth/token_introspection_manager.py`
- **Introspect token with server.** (1 connections) — `gen_epix/fastapp/services/auth/token_introspection_manager.py`
- **Now the requested value.** (1 connections) — `gen_epix/fastapp/services/auth/token_introspection_manager.py`
- **Fetch introspection endpoint.** (1 connections) — `gen_epix/fastapp/services/auth/token_introspection_manager.py`

## Relationships

- [Auth Protocols & Structured Logging](Auth_Protocols_&_Structured_Logging.md) (9 shared connections)

## Source Files

- `gen_epix/fastapp/services/auth/token_introspection_manager.py`

## Audit Trail

- EXTRACTED: 30 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*