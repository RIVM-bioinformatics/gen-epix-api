# OAuth2 Request Validator

> 42 nodes · cohesion 0.07

## Key Concepts

- **OAuth2Validator** (35 connections) — `test/test_client/oauth/validators.py`
- **Any** (19 connections)
- **.get_default_scopes()** (4 connections) — `test/test_client/oauth/validators.py`
- **.get_default_scopes_for_client_credentials()** (4 connections) — `test/test_client/oauth/validators.py`
- **.test_validator_initialization()** (3 connections) — `test/test_client/oauth/test_validators.py`
- **.authenticate_client()** (3 connections) — `test/test_client/oauth/validators.py`
- **.client_authentication_required()** (3 connections) — `test/test_client/oauth/validators.py`
- **.confirm_redirect_uri()** (3 connections) — `test/test_client/oauth/validators.py`
- **.get_default_redirect_uri()** (3 connections) — `test/test_client/oauth/validators.py`
- **.introspect_token()** (3 connections) — `test/test_client/oauth/validators.py`
- **.is_within_original_scope()** (3 connections) — `test/test_client/oauth/validators.py`
- **.save_authorization_code()** (3 connections) — `test/test_client/oauth/validators.py`
- **.save_bearer_token()** (3 connections) — `test/test_client/oauth/validators.py`
- **.validate_bearer_token()** (3 connections) — `test/test_client/oauth/validators.py`
- **.validate_client_id()** (3 connections) — `test/test_client/oauth/validators.py`
- **.validate_code()** (3 connections) — `test/test_client/oauth/validators.py`
- **.validate_grant_type()** (3 connections) — `test/test_client/oauth/validators.py`
- **.validate_redirect_uri()** (3 connections) — `test/test_client/oauth/validators.py`
- **.validate_refresh_token()** (3 connections) — `test/test_client/oauth/validators.py`
- **.validate_response_type()** (3 connections) — `test/test_client/oauth/validators.py`
- **.validate_scopes()** (3 connections) — `test/test_client/oauth/validators.py`
- **.revoke_token()** (2 connections) — `test/test_client/oauth/validators.py`
- **RequestValidator** (1 connections)
- **Test OAuth2Validator initialization.** (1 connections) — `test/test_client/oauth/test_validators.py`
- **Save authorization code (not used in client credentials flow).** (1 connections) — `test/test_client/oauth/validators.py`
- *... and 17 more nodes in this community*

## Relationships

- [OAuth Client Store](OAuth_Client_Store.md) (4 shared connections)
- [OAuth Provider Test Harness](OAuth_Provider_Test_Harness.md) (3 shared connections)
- [OAuth Client Auth Tests](OAuth_Client_Auth_Tests.md) (2 shared connections)
- [Token Store Tests](Token_Store_Tests.md) (2 shared connections)
- [OAuth Token Model Tests](OAuth_Token_Model_Tests.md) (2 shared connections)
- [Test Fixture Setup](Test_Fixture_Setup.md) (1 shared connections)
- [OAuth Demo Client Flows](OAuth_Demo_Client_Flows.md) (1 shared connections)

## Source Files

- `test/test_client/oauth/test_validators.py`
- `test/test_client/oauth/validators.py`

## Audit Trail

- EXTRACTED: 70 (93%)
- INFERRED: 5 (7%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*