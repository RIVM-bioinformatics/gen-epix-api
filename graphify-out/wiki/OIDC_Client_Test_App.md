# OIDC Client Test App

> 52 nodes · cohesion 0.05

## Key Concepts

- **RequestorApp** (25 connections) — `test/end_to_end/client_credential_flow/apps/requestor_app.py`
- **TestOauthClientCredentialsFlow** (21 connections) — `test/end_to_end/client_credential_flow/test_client_credential_flow.py`
- **._b64url_encode_no_pad()** (6 connections) — `test/end_to_end/client_credential_flow/test_client_credential_flow.py`
- **.test_try_changing_jwt_signing_algorithm()** (6 connections) — `test/end_to_end/client_credential_flow/test_client_credential_flow.py`
- **._initialize_oauth_idp_client()** (5 connections) — `test/end_to_end/client_credential_flow/apps/requestor_app.py`
- **scenario_ids** (5 connections)
- **.test_try_jwt_header_injections()** (5 connections) — `test/end_to_end/client_credential_flow/test_client_credential_flow.py`
- **.test_expiry_jwt_token()** (4 connections) — `test/end_to_end/client_credential_flow/test_client_credential_flow.py`
- **.test_jwt_is_using_aws_cognito()** (4 connections) — `test/end_to_end/client_credential_flow/test_client_credential_flow.py`
- **.test_jwt_sensitive_info_disclosure()** (4 connections) — `test/end_to_end/client_credential_flow/test_client_credential_flow.py`
- **.test_load_keys_ignores_invalid_key()** (4 connections) — `test/end_to_end/client_credential_flow/test_client_credential_flow.py`
- **.test_oauth_client_credentials_flow_invalid_token()** (4 connections) — `test/end_to_end/client_credential_flow/test_client_credential_flow.py`
- **.test_oauth_client_credentials_flow_success()** (4 connections) — `test/end_to_end/client_credential_flow/test_client_credential_flow.py`
- **.test_try_modifying_payload_without_chaning_signature()** (4 connections) — `test/end_to_end/client_credential_flow/test_client_credential_flow.py`
- **.test_try_removing_signature_part()** (4 connections) — `test/end_to_end/client_credential_flow/test_client_credential_flow.py`
- **.call_protected_endpoint()** (3 connections) — `test/end_to_end/client_credential_flow/apps/requestor_app.py`
- **.test_check_jwt_if_using_asymmetric()** (3 connections) — `test/end_to_end/client_credential_flow/test_client_credential_flow.py`
- **.test_client_management_endpoints()** (3 connections) — `test/end_to_end/client_credential_flow/test_client_credential_flow.py`
- **.test_get_jwk_from_jwt_returns_existing_key()** (3 connections) — `test/end_to_end/client_credential_flow/test_client_credential_flow.py`
- **.test_oauth_client_credentials_flow_missing_token()** (3 connections) — `test/end_to_end/client_credential_flow/test_client_credential_flow.py`
- **.test_oauth_discovery_endpoint()** (3 connections) — `test/end_to_end/client_credential_flow/test_client_credential_flow.py`
- **.test_oauth_jwks_endpoint()** (3 connections) — `test/end_to_end/client_credential_flow/test_client_credential_flow.py`
- **.test_verify_if_within_scope()** (3 connections) — `test/end_to_end/client_credential_flow/test_client_credential_flow.py`
- **.create_invalid_token()** (2 connections) — `test/end_to_end/client_credential_flow/apps/requestor_app.py`
- **.get_access_token()** (2 connections) — `test/end_to_end/client_credential_flow/apps/requestor_app.py`
- *... and 27 more nodes in this community*

## Relationships

- [FastAPI App Composition](FastAPI_App_Composition.md) (12 shared connections)
- [Auth Protocols & Structured Logging](Auth_Protocols_&_Structured_Logging.md) (6 shared connections)

## Source Files

- `test/end_to_end/client_credential_flow/apps/requestor_app.py`
- `test/end_to_end/client_credential_flow/test_client_credential_flow.py`

## Audit Trail

- EXTRACTED: 87 (97%)
- INFERRED: 3 (3%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*