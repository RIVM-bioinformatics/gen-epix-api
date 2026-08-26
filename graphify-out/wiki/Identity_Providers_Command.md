# Identity Providers Command

> 25 nodes · cohesion 0.16

## Key Concepts

- **auth/__init__.py** (30 connections) — `gen_epix/fastapp/services/auth/__init__.py`
- **auth/service.py** (27 connections) — `gen_epix/fastapp/services/auth/service.py`
- **test_fastapp_auth_service.py** (26 connections) — `test/fastapp/unit/services/test_fastapp_auth_service.py`
- **IdentityProvider** (23 connections) — `gen_epix/fastapp/services/auth/model.py`
- **GetIdentityProvidersCommand** (18 connections) — `gen_epix/fastapp/services/auth/command.py`
- **mock_idp_client.py** (15 connections) — `gen_epix/fastapp/services/auth/mock_idp_client.py`
- **BaseAuthService** (13 connections) — `gen_epix/fastapp/services/auth/base.py`
- **idp_client.py** (12 connections) — `gen_epix/fastapp/services/auth/idp_client.py`
- **auth/base.py** (8 connections) — `gen_epix/fastapp/services/auth/base.py`
- **auth/command.py** (7 connections) — `gen_epix/fastapp/services/auth/command.py`
- **auth/util.py** (6 connections) — `gen_epix/fastapp/services/auth/util.py`
- **TestGetIdentityProviders** (6 connections) — `test/fastapp/unit/services/test_fastapp_auth_service.py`
- **.get_identity_providers()** (4 connections) — `gen_epix/commondb/services/remote_app.py`
- **.get_identity_providers()** (4 connections) — `gen_epix/fastapp/services/auth/base.py`
- **.get_identity_providers()** (4 connections) — `gen_epix/fastapp/services/auth/service.py`
- **auth/literal.py** (2 connections) — `gen_epix/fastapp/services/auth/literal.py`
- **Retrieve the list of configured identity providers.** (1 connections) — `gen_epix/commondb/services/remote_app.py`
- **.register_handlers()** (1 connections) — `gen_epix/fastapp/services/auth/base.py`
- **Retrieve a list of available identity providers for authentication.** (1 connections) — `gen_epix/fastapp/services/auth/base.py`
- **Command** (1 connections)
- **# TODO: make async** (1 connections) — `gen_epix/fastapp/services/auth/idp_client.py`
- **# TODO: check if this is a security risk** (1 connections) — `gen_epix/fastapp/services/auth/mock_idp_client.py`
- **# TODO: generate get_current_user and get_new_user functions** (1 connections) — `gen_epix/fastapp/services/auth/service.py`
- **# TODO: only select actual discovery doc keys, should be class variable of…** (1 connections) — `gen_epix/fastapp/services/auth/service.py`
- **Test scenarios for get_identity_providers.** (1 connections) — `test/fastapp/unit/services/test_fastapp_auth_service.py`

## Relationships

- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (30 shared connections)
- [Auth Service User Claims](Auth_Service_User_Claims.md) (16 shared connections)
- [Auth Service Tests](Auth_Service_Tests.md) (11 shared connections)
- [Identity Provider Client](Identity_Provider_Client.md) (8 shared connections)
- [Organization Service](Organization_Service.md) (6 shared connections)
- [Mock IDP Client](Mock_IDP_Client.md) (5 shared connections)
- [Commondb Organization Domain Models](Commondb_Organization_Domain_Models.md) (4 shared connections)
- [Casedb Domain CRUD Commands](Casedb_Domain_CRUD_Commands.md) (3 shared connections)
- [OAuth IDP Client](OAuth_IDP_Client.md) (3 shared connections)
- [Base Service Class](Base_Service_Class.md) (2 shared connections)
- [Abac Service Access Control](Abac_Service_Access_Control.md) (2 shared connections)
- [Case Data Serialization](Case_Data_Serialization.md) (2 shared connections)

## Source Files

- `gen_epix/commondb/services/remote_app.py`
- `gen_epix/fastapp/services/auth/__init__.py`
- `gen_epix/fastapp/services/auth/base.py`
- `gen_epix/fastapp/services/auth/command.py`
- `gen_epix/fastapp/services/auth/idp_client.py`
- `gen_epix/fastapp/services/auth/literal.py`
- `gen_epix/fastapp/services/auth/mock_idp_client.py`
- `gen_epix/fastapp/services/auth/model.py`
- `gen_epix/fastapp/services/auth/service.py`
- `gen_epix/fastapp/services/auth/util.py`
- `test/fastapp/unit/services/test_fastapp_auth_service.py`

## Audit Trail

- EXTRACTED: 159 (96%)
- INFERRED: 6 (4%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*