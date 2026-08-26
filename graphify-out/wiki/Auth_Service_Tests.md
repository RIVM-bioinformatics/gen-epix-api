# Auth Service Tests

> 65 nodes · cohesion 0.05

## Key Concepts

- **.create_claims()** (20 connections) — `test/fastapp/unit/services/test_fastapp_auth_service.py`
- **.run_async()** (20 connections) — `test/fastapp/unit/services/test_fastapp_auth_service.py`
- **BaseAuthServiceTestCase** (19 connections) — `test/fastapp/unit/services/test_fastapp_auth_service.py`
- **.make_idp_client()** (13 connections) — `test/fastapp/unit/services/test_fastapp_auth_service.py`
- **TestGetExistingUserFromClaims** (10 connections) — `test/fastapp/unit/services/test_fastapp_auth_service.py`
- **.extract_security_callable()** (7 connections) — `test/fastapp/unit/services/test_fastapp_auth_service.py`
- **.test_dependencies_multiple_idps_resolution()** (7 connections) — `test/fastapp/unit/services/test_fastapp_auth_service.py`
- **TestGetNewUserFromClaims** (6 connections) — `test/fastapp/unit/services/test_fastapp_auth_service.py`
- **TestCreateUserDependenciesNoIdp** (5 connections) — `test/fastapp/unit/services/test_fastapp_auth_service.py`
- **.test_dependencies_no_idp_happy_paths()** (5 connections) — `test/fastapp/unit/services/test_fastapp_auth_service.py`
- **TestCreateUserDependenciesWithIdps** (5 connections) — `test/fastapp/unit/services/test_fastapp_auth_service.py`
- **.test_dependencies_multiple_idps_unauthorized()** (5 connections) — `test/fastapp/unit/services/test_fastapp_auth_service.py`
- **.test_get_existing_user_key_from_userinfo_then_found()** (5 connections) — `test/fastapp/unit/services/test_fastapp_auth_service.py`
- **TestGetExistingUserFromToken** (5 connections) — `test/fastapp/unit/services/test_fastapp_auth_service.py`
- **.test_get_new_user_from_claims_user_manager_none_raises()** (5 connections) — `test/fastapp/unit/services/test_fastapp_auth_service.py`
- **.test_get_new_user_from_claims_userinfo_and_user_manager()** (5 connections) — `test/fastapp/unit/services/test_fastapp_auth_service.py`
- **.test_dependencies_no_idp_missing_claims_raises()** (4 connections) — `test/fastapp/unit/services/test_fastapp_auth_service.py`
- **.test_get_existing_user_found_updates_name()** (4 connections) — `test/fastapp/unit/services/test_fastapp_auth_service.py`
- **.test_get_existing_user_no_results_auto_create_failure()** (4 connections) — `test/fastapp/unit/services/test_fastapp_auth_service.py`
- **.test_get_existing_user_no_results_auto_create_success()** (4 connections) — `test/fastapp/unit/services/test_fastapp_auth_service.py`
- **.test_get_existing_user_no_results_root_user()** (4 connections) — `test/fastapp/unit/services/test_fastapp_auth_service.py`
- **.test_get_existing_user_no_user_manager_unauthorized()** (4 connections) — `test/fastapp/unit/services/test_fastapp_auth_service.py`
- **.test_get_existing_user_update_name_domain_exception()** (4 connections) — `test/fastapp/unit/services/test_fastapp_auth_service.py`
- **.test_existing_user_from_token_no_valid_user_raises()** (4 connections) — `test/fastapp/unit/services/test_fastapp_auth_service.py`
- **.test_existing_user_from_token_second_idp_succeeds()** (4 connections) — `test/fastapp/unit/services/test_fastapp_auth_service.py`
- *... and 40 more nodes in this community*

## Relationships

- [Identity Providers Command](Identity_Providers_Command.md) (11 shared connections)
- [Auth Service User Claims](Auth_Service_User_Claims.md) (4 shared connections)
- [Root Token TTL Tests](Root_Token_TTL_Tests.md) (3 shared connections)
- [IDP Clients Property Tests](IDP_Clients_Property_Tests.md) (2 shared connections)
- [Identity Provider Client](Identity_Provider_Client.md) (1 shared connections)

## Source Files

- `test/fastapp/unit/services/test_fastapp_auth_service.py`

## Audit Trail

- EXTRACTED: 128 (99%)
- INFERRED: 1 (1%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*