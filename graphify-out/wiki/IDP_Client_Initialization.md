# IDP Client Initialization

> 10 nodes · cohesion 0.27

## Key Concepts

- **.__init__()** (8 connections) — `gen_epix/fastapp/services/auth/service.py`
- **._init_idp_clients()** (7 connections) — `gen_epix/fastapp/services/auth/service.py`
- **._validate_idp_cfgs()** (4 connections) — `gen_epix/fastapp/services/auth/service.py`
- **App** (3 connections)
- **SSLContext** (3 connections)
- **Any** (1 connections)
- **Logger** (1 connections)
- **Validate that configured provider names and labels are unique. Args: app:…** (1 connections) — `gen_epix/fastapp/services/auth/service.py`
- **Initialize authentication, identity-provider clients, and API dependencies.…** (1 connections) — `gen_epix/fastapp/services/auth/service.py`
- **Initialize configured identity-provider clients and queue retryable failures.…** (1 connections) — `gen_epix/fastapp/services/auth/service.py`

## Relationships

- [Authentication Service Base](Authentication_Service_Base.md) (3 shared connections)
- [Auth Protocols & Structured Logging](Auth_Protocols_&_Structured_Logging.md) (2 shared connections)
- [Mock IDP Client](Mock_IDP_Client.md) (1 shared connections)

## Source Files

- `gen_epix/fastapp/services/auth/service.py`

## Audit Trail

- EXTRACTED: 18 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*