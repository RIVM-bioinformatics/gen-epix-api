# IDP Client Initialization

> 11 nodes · cohesion 0.25

## Key Concepts

- **._init_idp_client()** (8 connections) — `gen_epix/fastapp/services/auth/service.py`
- **.__init__()** (7 connections) — `gen_epix/fastapp/services/auth/service.py`
- **._init_idp_clients()** (6 connections) — `gen_epix/fastapp/services/auth/service.py`
- **._validate_idp_cfgs()** (4 connections) — `gen_epix/fastapp/services/auth/service.py`
- **._retry_pending_idp_clients()** (3 connections) — `gen_epix/fastapp/services/auth/service.py`
- **App** (3 connections)
- **SSLContext** (3 connections)
- **Any** (1 connections)
- **Logger** (1 connections)
- **Try to initialize a single IDP client from its configuration. If unsuccessful,…** (1 connections) — `gen_epix/fastapp/services/auth/service.py`
- **Verify non-unique names and labels in the provided IDP configurations and raise…** (1 connections) — `gen_epix/fastapp/services/auth/service.py`

## Relationships

- [Auth Service User Claims](Auth_Service_User_Claims.md) (5 shared connections)
- [Mock IDP Client](Mock_IDP_Client.md) (1 shared connections)
- [OAuth IDP Client](OAuth_IDP_Client.md) (1 shared connections)
- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (1 shared connections)
- [Identity Provider Client](Identity_Provider_Client.md) (1 shared connections)
- [Identity Providers Command](Identity_Providers_Command.md) (1 shared connections)

## Source Files

- `gen_epix/fastapp/services/auth/service.py`

## Audit Trail

- EXTRACTED: 24 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*