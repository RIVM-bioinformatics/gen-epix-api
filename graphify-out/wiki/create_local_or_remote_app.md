# .create_local_or_remote_app

> 19 nodes · cohesion 0.14

## Key Concepts

- **.create_local_or_remote_app()** (12 connections) — `gen_epix/commondb/services/remote_app.py`
- **.__init__()** (11 connections) — `gen_epix/commondb/services/remote_app.py`
- **._create_local_app()** (10 connections) — `gen_epix/commondb/services/remote_app.py`
- **User** (5 connections)
- **.register_invited_user()** (4 connections) — `gen_epix/commondb/services/remote_app.py`
- **.update_user()** (4 connections) — `gen_epix/commondb/services/remote_app.py`
- **.update_user_own_organization()** (4 connections) — `gen_epix/commondb/services/remote_app.py`
- **Any** (4 connections)
- **App** (3 connections)
- **Enum** (3 connections)
- **Logger** (3 connections)
- **Domain** (1 connections)
- **Register an invited user using their invitation token.** (1 connections) — `gen_epix/commondb/services/remote_app.py`
- **Update a user's active status, roles, or organization.** (1 connections) — `gen_epix/commondb/services/remote_app.py`
- **Update the authenticated user's own organization.** (1 connections) — `gen_epix/commondb/services/remote_app.py`
- **Create either a local or remote app instance based on setup type.** (1 connections) — `gen_epix/commondb/services/remote_app.py`
- **Instantiate a local app from configuration and a user definition.** (1 connections) — `gen_epix/commondb/services/remote_app.py`
- **Initialize with connection and authentication settings; register all commondb…** (1 connections) — `gen_epix/commondb/services/remote_app.py`
- **LogItem** (1 connections)

## Relationships

- [CommondbRemoteApp](CommondbRemoteApp.md) (6 shared connections)
- [CrudOperation](CrudOperation.md) (4 shared connections)
- [._create_remote_app](_create_remote_app.md) (3 shared connections)
- [casedb/domain/command/__init__.py](casedb-domain-command-__init__.py.md) (3 shared connections)
- [commondb/domain/enum.py](commondb-domain-enum.py.md) (2 shared connections)
- [BaseCommondbRemoteAppTestCase](BaseCommondbRemoteAppTestCase.md) (2 shared connections)
- [AppCfg](AppCfg.md) (1 shared connections)
- [OauthIdpClient](OauthIdpClient.md) (1 shared connections)
- [auth/__init__.py](auth-__init__.py.md) (1 shared connections)

## Source Files

- `gen_epix/commondb/services/remote_app.py`

## Audit Trail

- EXTRACTED: 47 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*