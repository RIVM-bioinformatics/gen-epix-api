# IDP Retry Handling Tests

> 18 nodes · cohesion 0.20

## Key Concepts

- **AuthTestClient** (24 connections) — `test/fastapp/auth_test_client.py`
- **TestAuth** (11 connections) — `test/fastapp/unit/auth/test_fastapp_auth.py`
- **test_fastapp_auth.py** (8 connections) — `test/fastapp/unit/auth/test_fastapp_auth.py`
- **.oauth_idp_client()** (5 connections) — `test/fastapp/unit/auth/test_fastapp_auth.py`
- **.get_test_client()** (4 connections) — `test/fastapp/auth_test_client.py`
- **get_test_client()** (4 connections) — `test/fastapp/unit/auth/test_fastapp_auth.py`
- **.test_invalid_claims()** (3 connections) — `test/fastapp/unit/auth/test_fastapp_auth.py`
- **.test_invalid_jwk()** (3 connections) — `test/fastapp/unit/auth/test_fastapp_auth.py`
- **fixture** (2 connections)
- **parametrize** (2 connections)
- **.test_idp_retry_handling_preserves_existing_clients()** (2 connections) — `test/fastapp/unit/auth/test_fastapp_auth.py`
- **.test_idp_retry_mechanism_adds_late_idp()** (2 connections) — `test/fastapp/unit/auth/test_fastapp_auth.py`
- **.test_invalid_jwt_token()** (2 connections) — `test/fastapp/unit/auth/test_fastapp_auth.py`
- **.test_non_secure_happy_flow()** (2 connections) — `test/fastapp/unit/auth/test_fastapp_auth.py`
- **.test_secure_no_token()** (2 connections) — `test/fastapp/unit/auth/test_fastapp_auth.py`
- **.test_valid_jwt_token_happy_flow()** (2 connections) — `test/fastapp/unit/auth/test_fastapp_auth.py`
- **.mock_create_token_header()** (1 connections) — `test/fastapp/auth_test_client.py`
- **Get an OidcClient instance from the test environment.** (1 connections) — `test/fastapp/unit/auth/test_fastapp_auth.py`

## Relationships

- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (5 shared connections)
- [OIDC Client Credentials Tests](OIDC_Client_Credentials_Tests.md) (4 shared connections)
- [Token Introspection Manager](Token_Introspection_Manager.md) (2 shared connections)
- [OAuth Introspection Caching Tests](OAuth_Introspection_Caching_Tests.md) (2 shared connections)
- [OAuth IDP Client](OAuth_IDP_Client.md) (2 shared connections)
- [OAuth Client Model](OAuth_Client_Model.md) (1 shared connections)
- [Commondb Auth Tests](Commondb_Auth_Tests.md) (1 shared connections)
- [Core App Base Class](Core_App_Base_Class.md) (1 shared connections)
- [Abac Service Access Control](Abac_Service_Access_Control.md) (1 shared connections)
- [Casedb CaseSet CRUD & Tests](Casedb_CaseSet_CRUD_&_Tests.md) (1 shared connections)

## Source Files

- `test/fastapp/auth_test_client.py`
- `test/fastapp/unit/auth/test_fastapp_auth.py`

## Audit Trail

- EXTRACTED: 42 (84%)
- INFERRED: 8 (16%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*