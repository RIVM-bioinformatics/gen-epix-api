# Auto-Create User Auth Tests

> 31 nodes · cohesion 0.10

## Key Concepts

- **AuthEnv** (35 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **TestRootUserLogin** (13 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **TestAutoCreateUser** (11 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **scenario_ids** (5 connections)
- **.make_claims()** (4 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **.get_secure()** (3 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **._setup_http()** (3 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **.test_auto_create_calls_user_manager_method()** (3 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **.test_auto_create_enabled_does_not_duplicate_existing_user()** (3 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **.test_known_user_allowed_when_auto_create_disabled()** (3 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **.test_non_root_user_not_detected_as_root()** (3 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **.test_root_user_login_via_async_service_method()** (3 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **.test_root_user_subsequent_login_succeeds()** (3 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **.make_token_header()** (2 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **.test_auto_create_disabled_does_not_call_auto_create_method()** (2 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **.test_auto_created_user_has_configured_role()** (2 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **.test_auto_created_user_key_matches_email_claim()** (2 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **.test_unknown_user_auto_created_when_enabled()** (2 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **.test_unknown_user_rejected_when_auto_create_disabled()** (2 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **.test_is_root_user_claims_false_for_non_root_email()** (2 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **.test_is_root_user_claims_true_for_root_key()** (2 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **.test_root_user_first_login_assigns_root_role()** (2 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **.test_root_user_first_login_creates_user()** (2 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **.test_root_user_is_detected_as_root_after_first_login()** (2 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **.test_root_user_key_matches_configured_identity()** (2 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- *... and 6 more nodes in this community*

## Relationships

- [User Claims Name Extraction](User_Claims_Name_Extraction.md) (12 shared connections)
- [Commondb Auth Tests](Commondb_Auth_Tests.md) (8 shared connections)
- [User Invitation Tests](User_Invitation_Tests.md) (3 shared connections)
- [Core App Base Class](Core_App_Base_Class.md) (1 shared connections)
- [Abac Service Access Control](Abac_Service_Access_Control.md) (1 shared connections)
- [Auth Service User Claims](Auth_Service_User_Claims.md) (1 shared connections)
- [OAuth Client Model](OAuth_Client_Model.md) (1 shared connections)

## Source Files

- `test/commondb/unit/auth/test_commondb_auth.py`

## Audit Trail

- EXTRACTED: 71 (95%)
- INFERRED: 4 (5%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*