# AuthService

> 55 nodes

## Key Concepts

- **AuthService** (43 connections) — `gen_epix/fastapp/services/auth/service.py`
- **IdpClient** (20 connections) — `gen_epix/fastapp/services/auth/idp_client.py`
- **MockIDPClient** (18 connections) — `gen_epix/fastapp/services/auth/mock_idp_client.py`
- **IDPUser** (17 connections) — `gen_epix/fastapp/services/auth/model.py`
- **._init_idp_client()** (8 connections) — `gen_epix/fastapp/services/auth/service.py`
- **User** (8 connections)
- **.get_existing_user_from_claims()** (7 connections) — `gen_epix/fastapp/services/auth/service.py`
- **.__init__()** (7 connections) — `gen_epix/fastapp/services/auth/service.py`
- **.get_existing_user_from_token()** (6 connections) — `gen_epix/fastapp/services/auth/service.py`
- **._init_idp_clients()** (6 connections) — `gen_epix/fastapp/services/auth/service.py`
- **._verify_root_user_for_token_time_to_live()** (6 connections) — `gen_epix/fastapp/services/auth/service.py`
- **TestInitializationValidation** (5 connections) — `test/fastapp/unit/services/test_fastapp_auth_service.py`
- **._auto_create_new_user()** (5 connections) — `gen_epix/fastapp/services/auth/service.py`
- **.create_user_dependencies()** (5 connections) — `gen_epix/fastapp/services/auth/service.py`
- **._create_no_auth_dependencies()** (4 connections) — `gen_epix/fastapp/services/auth/service.py`
- **._create_user_dependencies_from_callables()** (4 connections) — `gen_epix/fastapp/services/auth/service.py`
- **._generate_user_key_from_claims()** (4 connections) — `gen_epix/fastapp/services/auth/service.py`
- **.get_identity_providers()** (4 connections) — `gen_epix/fastapp/services/auth/service.py`
- **._validate_idp_cfgs()** (4 connections) — `gen_epix/fastapp/services/auth/service.py`
- **.get_identity_provider()** (3 connections) — `gen_epix/fastapp/services/auth/idp_client.py`
- **.__init__()** (3 connections) — `gen_epix/fastapp/services/auth/idp_client.py`
- **.__call__()** (3 connections) — `gen_epix/fastapp/services/auth/mock_idp_client.py`
- **.get_idp_user_from_claims()** (3 connections) — `gen_epix/fastapp/services/auth/service.py`
- **.get_new_user_from_claims()** (3 connections) — `gen_epix/fastapp/services/auth/service.py`
- **._retry_pending_idp_clients()** (3 connections) — `gen_epix/fastapp/services/auth/service.py`
- *... and 30 more nodes in this community*

## Relationships

- [auth/__init__.py](auth-__init__.py.md) (35 shared connections)
- [DummyIdpClient](DummyIdpClient.md) (5 shared connections)
- [.create_claims](create_claims.md) (4 shared connections)
- [create_client](create_client.md) (4 shared connections)
- [OrganizationService](OrganizationService.md) (4 shared connections)
- [OauthIdpClient](OauthIdpClient.md) (3 shared connections)
- [CrudOperation](CrudOperation.md) (3 shared connections)
- [BaseLogItem](BaseLogItem.md) (2 shared connections)
- [casedb/domain/model/__init__.py](casedb-domain-model-__init__.py.md) (2 shared connections)
- [AuthTestClient](AuthTestClient.md) (2 shared connections)
- [AppCfg](AppCfg.md) (2 shared connections)
- [Permission](Permission.md) (1 shared connections)

## Source Files

- `gen_epix/fastapp/services/auth/idp_client.py`
- `gen_epix/fastapp/services/auth/mock_idp_client.py`
- `gen_epix/fastapp/services/auth/model.py`
- `gen_epix/fastapp/services/auth/service.py`
- `test/fastapp/unit/services/test_fastapp_auth_service.py`

## Audit Trail

- EXTRACTED: 148 (92%)
- INFERRED: 13 (8%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*