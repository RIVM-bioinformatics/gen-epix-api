# Auth Service User Claims

> 26 nodes · cohesion 0.16

## Key Concepts

- **AuthService** (43 connections) — `gen_epix/fastapp/services/auth/service.py`
- **Claims** (25 connections) — `gen_epix/fastapp/services/auth/model.py`
- **IDPUser** (17 connections) — `gen_epix/fastapp/services/auth/model.py`
- **User** (8 connections)
- **.get_existing_user_from_claims()** (7 connections) — `gen_epix/fastapp/services/auth/service.py`
- **.get_existing_user_from_token()** (6 connections) — `gen_epix/fastapp/services/auth/service.py`
- **._verify_root_user_for_token_time_to_live()** (6 connections) — `gen_epix/fastapp/services/auth/service.py`
- **._auto_create_new_user()** (5 connections) — `gen_epix/fastapp/services/auth/service.py`
- **.create_user_dependencies()** (5 connections) — `gen_epix/fastapp/services/auth/service.py`
- **TestInitializationValidation** (5 connections) — `test/fastapp/unit/services/test_fastapp_auth_service.py`
- **Model** (4 connections)
- **._create_no_auth_dependencies()** (4 connections) — `gen_epix/fastapp/services/auth/service.py`
- **._create_user_dependencies_from_callables()** (4 connections) — `gen_epix/fastapp/services/auth/service.py`
- **._generate_user_key_from_claims()** (4 connections) — `gen_epix/fastapp/services/auth/service.py`
- **.get_idp_user_from_claims()** (3 connections) — `gen_epix/fastapp/services/auth/service.py`
- **.get_new_user_from_claims()** (3 connections) — `gen_epix/fastapp/services/auth/service.py`
- **.test_duplicate_idp_names_raise_initialization_error()** (3 connections) — `test/fastapp/unit/services/test_fastapp_auth_service.py`
- **.test_pending_idp_when_init_returns_none()** (3 connections) — `test/fastapp/unit/services/test_fastapp_auth_service.py`
- **._warn_too_many_idps()** (2 connections) — `gen_epix/fastapp/services/auth/service.py`
- **BaseUserManager** (2 connections)
- **Request** (1 connections)
- **Verify that if the user is a root user, the token is not too old based on the…** (1 connections) — `gen_epix/fastapp/services/auth/service.py`
- **Get existing user based on provided token, return None if token is invalid or…** (1 connections) — `gen_epix/fastapp/services/auth/service.py`
- **Test IDP configuration validation during initialization.** (1 connections) — `test/fastapp/unit/services/test_fastapp_auth_service.py`
- **Duplicate names raise InitializationServiceError.** (1 connections) — `test/fastapp/unit/services/test_fastapp_auth_service.py`
- *... and 1 more nodes in this community*

## Relationships

- [Identity Providers Command](Identity_Providers_Command.md) (16 shared connections)
- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (10 shared connections)
- [IDP Client Initialization](IDP_Client_Initialization.md) (5 shared connections)
- [Auth Service Tests](Auth_Service_Tests.md) (4 shared connections)
- [App Composition & Service Wiring](App_Composition_&_Service_Wiring.md) (4 shared connections)
- [Commondb Auth Tests](Commondb_Auth_Tests.md) (3 shared connections)
- [Identity Provider Client](Identity_Provider_Client.md) (3 shared connections)
- [Mock IDP Client](Mock_IDP_Client.md) (2 shared connections)
- [OAuth IDP Client](OAuth_IDP_Client.md) (2 shared connections)
- [FastApp Entity & Model Core](FastApp_Entity_&_Model_Core.md) (2 shared connections)
- [Commondb Organization Domain Models](Commondb_Organization_Domain_Models.md) (2 shared connections)
- [App Composition & Startup](App_Composition_&_Startup.md) (2 shared connections)

## Source Files

- `gen_epix/fastapp/services/auth/model.py`
- `gen_epix/fastapp/services/auth/service.py`
- `test/fastapp/unit/services/test_fastapp_auth_service.py`

## Audit Trail

- EXTRACTED: 105 (92%)
- INFERRED: 9 (8%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*