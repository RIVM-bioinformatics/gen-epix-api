# Root Token TTL Tests

> 6 nodes · cohesion 0.33

## Key Concepts

- **TestRootUserTokenTimeToLive** (5 connections) — `test/fastapp/unit/services/test_fastapp_auth_service.py`
- **.test_root_token_older_than_15_minutes_is_rejected()** (3 connections) — `test/fastapp/unit/services/test_fastapp_auth_service.py`
- **.test_root_token_within_15_minutes_is_allowed()** (3 connections) — `test/fastapp/unit/services/test_fastapp_auth_service.py`
- **Test root token TTL enforcement helper.** (1 connections) — `test/fastapp/unit/services/test_fastapp_auth_service.py`
- **Root token younger than configured TTL should pass.** (1 connections) — `test/fastapp/unit/services/test_fastapp_auth_service.py`
- **Root token older than configured TTL should raise UnauthorizedAuthError.** (1 connections) — `test/fastapp/unit/services/test_fastapp_auth_service.py`

## Relationships

- [Auth Service Tests](Auth_Service_Tests.md) (3 shared connections)
- [Identity Providers Command](Identity_Providers_Command.md) (1 shared connections)

## Source Files

- `test/fastapp/unit/services/test_fastapp_auth_service.py`

## Audit Trail

- EXTRACTED: 9 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*