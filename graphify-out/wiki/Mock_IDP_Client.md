# Mock IDP Client

> 49 nodes · cohesion 0.07

## Key Concepts

- **MockIDPClient** (21 connections) — `gen_epix/fastapp/services/auth/mock_idp_client.py`
- **create_client()** (16 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- **test_fastapp_mock_idp_client.py** (15 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- **TestAuthorizationHandling** (12 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- **make_request()** (10 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- **TestPublicInterface** (9 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- **.test_non_bearer_scheme_logs_and_returns_none()** (6 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- **.__init__()** (5 connections) — `gen_epix/fastapp/services/auth/mock_idp_client.py`
- **assert_logged_with_code()** (5 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- **.test_bearer_scheme_decode_raises_auth_exception_logs_and_returns_none()** (5 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- **.test_bearer_scheme_decode_returns_claims_success()** (5 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- **.test_no_authorization_header_logs_and_returns_none()** (5 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- **.__call__()** (4 connections) — `gen_epix/fastapp/services/auth/mock_idp_client.py`
- **DummyLogItem** (4 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- **DummyRequest** (4 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- **.test_bearer_scheme_decode_raises_auth_exception_no_logger_returns_none()** (4 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- **.test_bearer_scheme_decode_returns_empty_claims_returns_none()** (4 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- **.test_no_authorization_header_no_logger_returns_none()** (4 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- **Id the requested value.** (3 connections) — `gen_epix/fastapp/app.py`
- **.id()** (3 connections) — `gen_epix/fastapp/services/auth/mock_idp_client.py`
- **.id()** (2 connections) — `gen_epix/fastapp/app.py`
- **.id()** (2 connections) — `gen_epix/fastapp/service.py`
- **UUID** (2 connections)
- **.__init__()** (2 connections) — `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`
- **parametrize** (2 connections)
- *... and 24 more nodes in this community*

## Relationships

- [Auth Protocols & Structured Logging](Auth_Protocols_&_Structured_Logging.md) (9 shared connections)
- [Authentication Service Base](Authentication_Service_Base.md) (7 shared connections)
- [FastApp API Tests](FastApp_API_Tests.md) (7 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (2 shared connections)
- [JWT Claims Extraction](JWT_Claims_Extraction.md) (2 shared connections)
- [Seqdb Sequence Retrieval Commands](Seqdb_Sequence_Retrieval_Commands.md) (1 shared connections)
- [IDP Client Initialization](IDP_Client_Initialization.md) (1 shared connections)
- [Application Log Items](Application_Log_Items.md) (1 shared connections)
- [Command Exception Handling](Command_Exception_Handling.md) (1 shared connections)

## Source Files

- `gen_epix/fastapp/app.py`
- `gen_epix/fastapp/service.py`
- `gen_epix/fastapp/services/auth/mock_idp_client.py`
- `test/fastapp/unit/services/auth/test_fastapp_mock_idp_client.py`

## Audit Trail

- EXTRACTED: 93 (86%)
- INFERRED: 15 (14%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*