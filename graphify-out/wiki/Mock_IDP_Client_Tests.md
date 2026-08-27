# Mock IDP Client Tests

> 30 nodes · cohesion 0.13

## Key Concepts

- **create_client()** (16 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- **test_fastapp_mock_idp_client.py** (15 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- **TestAuthorizationHandling** (11 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- **make_request()** (10 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- **TestPublicInterface** (9 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- **assert_logged_with_code()** (5 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- **.test_non_bearer_scheme_logs_and_returns_none()** (5 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- **DummyRequest** (4 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- **.test_bearer_scheme_decode_raises_auth_exception_logs_and_returns_none()** (4 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- **.test_bearer_scheme_decode_returns_claims_success()** (4 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- **.test_no_authorization_header_logs_and_returns_none()** (4 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- **.test_bearer_scheme_decode_raises_auth_exception_no_logger_returns_none()** (3 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- **.test_bearer_scheme_decode_returns_empty_claims_returns_none()** (3 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- **.test_no_authorization_header_no_logger_returns_none()** (3 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- **parametrize** (2 connections)
- **scenario_ids** (2 connections)
- **UUID** (2 connections)
- **.test_get_claims_from_jwt_not_implemented()** (2 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- **.test_get_claims_from_userinfo_not_implemented()** (2 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- **.test_get_identity_provider_not_implemented()** (2 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- **.test_id_property_generates_uuid()** (2 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- **.test_id_property_returns_provided_id()** (2 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- **.__init__()** (1 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- **Unit tests for MockIDPClient authentication flow. Tests cover all public…** (1 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- **Authorization header parsing and scheme handling.** (1 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- *... and 5 more nodes in this community*

## Relationships

- [Mock IDP Client](Mock_IDP_Client.md) (4 shared connections)
- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (2 shared connections)
- [Auth Service User Claims](Auth_Service_User_Claims.md) (1 shared connections)
- [Casedb CaseSet CRUD & Tests](Casedb_CaseSet_CRUD_&_Tests.md) (1 shared connections)
- [Identity Providers Command](Identity_Providers_Command.md) (1 shared connections)
- [Mock Log Item Stub](Mock_Log_Item_Stub.md) (1 shared connections)

## Source Files

- `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`

## Audit Trail

- EXTRACTED: 63 (97%)
- INFERRED: 2 (3%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*