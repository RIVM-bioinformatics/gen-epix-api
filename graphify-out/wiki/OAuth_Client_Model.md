# OAuth Client Model

> 65 nodes · cohesion 0.04

## Key Concepts

- **Client** (53 connections) — `test/test_client/oauth/client_store.py`
- **TestClient** (22 connections) — `test/test_client/oauth/test_client_store.py`
- **test_client_store.py** (8 connections) — `test/test_client/oauth/test_client_store.py`
- **TestClientStoreIntegration** (8 connections) — `test/test_client/oauth/test_client_store.py`
- **.__init__()** (5 connections) — `test/fastapp/auth_test_client.py`
- **._hash_secret()** (4 connections) — `test/test_client/oauth/client_store.py`
- **.__post_init__()** (3 connections) — `test/test_client/oauth/client_store.py`
- **.test_check_secret_backward_compatibility()** (3 connections) — `test/test_client/oauth/test_client_store.py`
- **.test_check_secret_with_hashed_secret()** (3 connections) — `test/test_client/oauth/test_client_store.py`
- **.test_check_secret_with_malformed_hash()** (3 connections) — `test/test_client/oauth/test_client_store.py`
- **.test_client_creation_basic()** (3 connections) — `test/test_client/oauth/test_client_store.py`
- **.test_client_creation_with_all_fields()** (3 connections) — `test/test_client/oauth/test_client_store.py`
- **.test_client_secret_hashing_on_creation()** (3 connections) — `test/test_client/oauth/test_client_store.py`
- **.test_client_secret_no_double_hashing()** (3 connections) — `test/test_client/oauth/test_client_store.py`
- **.test_default_factory_functions()** (3 connections) — `test/test_client/oauth/test_client_store.py`
- **.test_hash_secret_static_method()** (3 connections) — `test/test_client/oauth/test_client_store.py`
- **.test_supports_grant_type()** (3 connections) — `test/test_client/oauth/test_client_store.py`
- **.test_supports_redirect_uri()** (3 connections) — `test/test_client/oauth/test_client_store.py`
- **.test_to_dict_excludes_sensitive_data()** (3 connections) — `test/test_client/oauth/test_client_store.py`
- **.test_validate_scopes_all_valid()** (3 connections) — `test/test_client/oauth/test_client_store.py`
- **.test_validate_scopes_duplicates()** (3 connections) — `test/test_client/oauth/test_client_store.py`
- **.test_validate_scopes_empty_request()** (3 connections) — `test/test_client/oauth/test_client_store.py`
- **.test_validate_scopes_none_valid()** (3 connections) — `test/test_client/oauth/test_client_store.py`
- **.test_validate_scopes_some_invalid()** (3 connections) — `test/test_client/oauth/test_client_store.py`
- **.setup_method()** (3 connections) — `test/test_client/oauth/test_client_store.py`
- *... and 40 more nodes in this community*

## Relationships

- [OAuth Client Store](OAuth_Client_Store.md) (15 shared connections)
- [HTTP Exception Classes](HTTP_Exception_Classes.md) (5 shared connections)
- [Client Store Tests](Client_Store_Tests.md) (4 shared connections)
- [OAuth Client Credentials Validators](OAuth_Client_Credentials_Validators.md) (2 shared connections)
- [App Command/Domain Base](App_Command-Domain_Base.md) (2 shared connections)
- [Mock User Manager Tests](Mock_User_Manager_Tests.md) (1 shared connections)
- [Core App Base Class](Core_App_Base_Class.md) (1 shared connections)
- [Auth Service User Claims](Auth_Service_User_Claims.md) (1 shared connections)
- [IDP Retry Handling Tests](IDP_Retry_Handling_Tests.md) (1 shared connections)
- [Token Store Lifecycle Tests](Token_Store_Lifecycle_Tests.md) (1 shared connections)
- [Casedb ABAC & Filter Logic](Casedb_ABAC_&_Filter_Logic.md) (1 shared connections)
- [Casedb CaseSet CRUD & Tests](Casedb_CaseSet_CRUD_&_Tests.md) (1 shared connections)

## Source Files

- `test/fastapp/auth_test_client.py`
- `test/test_client/oauth/client_store.py`
- `test/test_client/oauth/test_client_store.py`

## Audit Trail

- EXTRACTED: 110 (91%)
- INFERRED: 11 (9%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*