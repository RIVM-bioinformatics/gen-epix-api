# Commondb Auth Tests

> 33 nodes · cohesion 0.10

## Key Concepts

- **test_commondb_auth.py** (40 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **InMemoryOrganizationRepository** (16 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **MockJWKAndToken** (11 connections) — `test/fastapp/unit/auth/mock_jwk_and_token.py`
- **.__init__()** (10 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **make_commondb_user_manager()** (10 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **User** (8 connections)
- **Any** (7 connections)
- **make_idps_cfg()** (5 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **make_mock_organization_service()** (5 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **_retrieve_user_by_key_from_repo()** (5 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **make_root_cfg()** (4 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **._get_token()** (4 connections) — `test/fastapp/unit/auth/mock_jwk_and_token.py`
- **.crud()** (3 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **make_mock_rbac_service()** (3 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **mock_jwk_and_token.py** (3 connections) — `test/fastapp/unit/auth/mock_jwk_and_token.py`
- **.add_invitation()** (2 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **.add_user()** (2 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **.get_user_by_key()** (2 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **.is_existing_user_by_key()** (2 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **.edit_claim()** (2 connections) — `test/fastapp/unit/auth/mock_jwk_and_token.py`
- **.edit_jwk()** (2 connections) — `test/fastapp/unit/auth/mock_jwk_and_token.py`
- **.__init__()** (2 connections) — `test/fastapp/unit/auth/mock_jwk_and_token.py`
- **.__init__()** (1 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **.uow()** (1 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **.user_exists_by_key()** (1 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- *... and 8 more nodes in this community*

## Relationships

- [User Invitation Tests](User_Invitation_Tests.md) (10 shared connections)
- [Auto-Create User Auth Tests](Auto-Create_User_Auth_Tests.md) (8 shared connections)
- [User Claims Name Extraction](User_Claims_Name_Extraction.md) (6 shared connections)
- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (6 shared connections)
- [Casedb CaseSet CRUD & Tests](Casedb_CaseSet_CRUD_&_Tests.md) (3 shared connections)
- [Auth Service User Claims](Auth_Service_User_Claims.md) (3 shared connections)
- [Base User Manager & RBAC](Base_User_Manager_&_RBAC.md) (2 shared connections)
- [Core App Base Class](Core_App_Base_Class.md) (2 shared connections)
- [Fastapp Repository Performance Tests](Fastapp_Repository_Performance_Tests.md) (2 shared connections)
- [Commondb Enums & Demo Data](Commondb_Enums_&_Demo_Data.md) (2 shared connections)
- [Auth Exception Middleware](Auth_Exception_Middleware.md) (1 shared connections)
- [OAuth IDP Client](OAuth_IDP_Client.md) (1 shared connections)

## Source Files

- `test/commondb/unit/auth/test_commondb_auth.py`
- `test/fastapp/unit/auth/mock_jwk_and_token.py`

## Audit Trail

- EXTRACTED: 102 (97%)
- INFERRED: 3 (3%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*