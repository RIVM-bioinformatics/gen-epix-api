# Authentication Service Base

> 157 nodes · cohesion 0.03

## Key Concepts

- **AuthService** (47 connections) — `gen_epix/fastapp/services/auth/service.py`
- **Claims** (38 connections) — `gen_epix/fastapp/services/auth/model.py`
- **auth/__init__.py** (31 connections) — `gen_epix/fastapp/services/auth/__init__.py`
- **BaseUserManager** (31 connections) — `gen_epix/fastapp/user_manager.py`
- **auth/service.py** (28 connections) — `gen_epix/fastapp/services/auth/service.py`
- **test_fastapp_auth_service.py** (26 connections) — `test/fastapp/unit/services/test_fastapp_auth_service.py`
- **.create_user_dependencies()** (21 connections) — `gen_epix/fastapp/services/auth/service.py`
- **BaseAuthServiceTestCase** (21 connections) — `test/fastapp/unit/services/test_fastapp_auth_service.py`
- **.create_claims()** (20 connections) — `test/fastapp/unit/services/test_fastapp_auth_service.py`
- **.run_async()** (20 connections) — `test/fastapp/unit/services/test_fastapp_auth_service.py`
- **._warn_too_many_idps()** (17 connections) — `gen_epix/fastapp/services/auth/service.py`
- **IDPUser** (16 connections) — `gen_epix/fastapp/services/auth/model.py`
- **BaseAuthService** (14 connections) — `gen_epix/fastapp/services/auth/base.py`
- **GetIdentityProvidersCommand** (14 connections) — `gen_epix/fastapp/services/auth/command.py`
- **.get_existing_user_from_claims()** (14 connections) — `gen_epix/fastapp/services/auth/service.py`
- **.make_idp_client()** (13 connections) — `test/fastapp/unit/services/test_fastapp_auth_service.py`
- **TestGetExistingUserFromClaims** (11 connections) — `test/fastapp/unit/services/test_fastapp_auth_service.py`
- **.get_new_user_from_claims()** (10 connections) — `gen_epix/fastapp/services/auth/service.py`
- **auth/base.py** (9 connections) — `gen_epix/fastapp/services/auth/base.py`
- **.get_idp_user_from_claims()** (9 connections) — `gen_epix/fastapp/services/auth/service.py`
- **User** (8 connections)
- **auth/command.py** (7 connections) — `gen_epix/fastapp/services/auth/command.py`
- **._create_no_auth_dependencies()** (7 connections) — `gen_epix/fastapp/services/auth/service.py`
- **.extract_security_callable()** (7 connections) — `test/fastapp/unit/services/test_fastapp_auth_service.py`
- **TestCreateUserDependenciesWithIdps** (7 connections) — `test/fastapp/unit/services/test_fastapp_auth_service.py`
- *... and 132 more nodes in this community*

## Relationships

- [Auth Protocols & Structured Logging](Auth_Protocols_&_Structured_Logging.md) (43 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (22 shared connections)
- [User Manager Operations](User_Manager_Operations.md) (12 shared connections)
- [Auth Claim Utilities](Auth_Claim_Utilities.md) (8 shared connections)
- [Mock IDP Client](Mock_IDP_Client.md) (7 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (6 shared connections)
- [Seqdb Sequence Retrieval Commands](Seqdb_Sequence_Retrieval_Commands.md) (5 shared connections)
- [Domain Registry & ABAC Policies](Domain_Registry_&_ABAC_Policies.md) (3 shared connections)
- [IDP Client Initialization](IDP_Client_Initialization.md) (3 shared connections)
- [JWT Claims Extraction](JWT_Claims_Extraction.md) (2 shared connections)
- [Domain & Entity Registry](Domain_&_Entity_Registry.md) (2 shared connections)
- [Casedb Case API Models](Casedb_Case_API_Models.md) (2 shared connections)

## Source Files

- `gen_epix/fastapp/services/auth/__init__.py`
- `gen_epix/fastapp/services/auth/base.py`
- `gen_epix/fastapp/services/auth/command.py`
- `gen_epix/fastapp/services/auth/model.py`
- `gen_epix/fastapp/services/auth/service.py`
- `gen_epix/fastapp/user_manager.py`
- `test/fastapp/unit/services/test_fastapp_auth_service.py`

## Audit Trail

- EXTRACTED: 396 (88%)
- INFERRED: 53 (12%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*