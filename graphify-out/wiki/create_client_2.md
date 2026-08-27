# create_client

> 35 nodes · cohesion 0.10

## Key Concepts

- **create_client()** (16 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- **test_fastapp_mock_idp_client.py** (15 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- **TestAuthorizationHandling** (11 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- **make_request()** (10 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- **TestPublicInterface** (9 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- **assert_logged_with_code()** (5 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- **.test_non_bearer_scheme_logs_and_returns_none()** (5 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- **DummyLogItem** (4 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- **DummyRequest** (4 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- **.test_bearer_scheme_decode_raises_auth_exception_logs_and_returns_none()** (4 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- **.test_bearer_scheme_decode_returns_claims_success()** (4 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- **.test_no_authorization_header_logs_and_returns_none()** (4 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- **.test_bearer_scheme_decode_raises_auth_exception_no_logger_returns_none()** (3 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- **.test_bearer_scheme_decode_returns_empty_claims_returns_none()** (3 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- **.test_no_authorization_header_no_logger_returns_none()** (3 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- **.__init__()** (2 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- **parametrize** (2 connections)
- **scenario_ids** (2 connections)
- **UUID** (2 connections)
- **.test_get_claims_from_jwt_not_implemented()** (2 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- **.test_get_claims_from_userinfo_not_implemented()** (2 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- **.test_get_identity_provider_not_implemented()** (2 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- **.test_id_property_generates_uuid()** (2 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- **.test_id_property_returns_provided_id()** (2 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- **.dumps()** (1 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- *... and 10 more nodes in this community*

## Relationships

- [AuthService](AuthService.md) (4 shared connections)
- [auth/__init__.py](auth-__init__.py.md) (3 shared connections)
- [CrudOperation](CrudOperation.md) (2 shared connections)

## Source Files

- `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`

## Audit Trail

- EXTRACTED: 67 (97%)
- INFERRED: 2 (3%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*