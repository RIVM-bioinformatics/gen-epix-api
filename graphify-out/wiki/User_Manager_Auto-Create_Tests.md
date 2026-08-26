# User Manager Auto-Create Tests

> 56 nodes · cohesion 0.08

## Key Concepts

- **test_user_manager_auto_create.py** (21 connections) — `test/commondb/unit/services/test_user_manager_auto_create.py`
- **UUID** (20 connections)
- **make_user_manager()** (19 connections) — `test/commondb/unit/services/test_user_manager_auto_create.py`
- **Organization** (16 connections)
- **Any** (12 connections)
- **fixture** (9 connections)
- **TestAutoCreateNewUserRegressions** (9 connections) — `test/commondb/unit/services/test_user_manager_auto_create.py`
- **TestAutoCreateNewUserRootOrgFeature** (7 connections) — `test/commondb/unit/services/test_user_manager_auto_create.py`
- **.test_creates_user_successfully_when_all_validations_pass()** (6 connections) — `test/commondb/unit/services/test_user_manager_auto_create.py`
- **.test_generates_and_assigns_user_id_before_persistence()** (6 connections) — `test/commondb/unit/services/test_user_manager_auto_create.py`
- **.test_raises_when_non_root_org_does_not_exist()** (6 connections) — `test/commondb/unit/services/test_user_manager_auto_create.py`
- **.test_raises_when_user_already_exists()** (6 connections) — `test/commondb/unit/services/test_user_manager_auto_create.py`
- **.test_returns_none_when_config_not_provided()** (6 connections) — `test/commondb/unit/services/test_user_manager_auto_create.py`
- **.test_verifies_repo_create_call_with_expected_user_object()** (6 connections) — `test/commondb/unit/services/test_user_manager_auto_create.py`
- **.test_auto_creates_root_org_when_missing_and_org_id_matches_root()** (6 connections) — `test/commondb/unit/services/test_user_manager_auto_create.py`
- **.test_org_validation_happens_before_user_existence_check()** (6 connections) — `test/commondb/unit/services/test_user_manager_auto_create.py`
- **.test_root_org_auto_create_with_non_root_org_id_still_raises()** (6 connections) — `test/commondb/unit/services/test_user_manager_auto_create.py`
- **.test_skips_org_creation_when_org_already_exists()** (6 connections) — `test/commondb/unit/services/test_user_manager_auto_create.py`
- **other_org()** (5 connections) — `test/commondb/unit/services/test_user_manager_auto_create.py`
- **root_org()** (5 connections) — `test/commondb/unit/services/test_user_manager_auto_create.py`
- **root_user()** (5 connections) — `test/commondb/unit/services/test_user_manager_auto_create.py`
- **.test_raises_when_construct_user_returns_none()** (5 connections) — `test/commondb/unit/services/test_user_manager_auto_create.py`
- **.test_user_creation_not_attempted_if_org_creation_fails()** (5 connections) — `test/commondb/unit/services/test_user_manager_auto_create.py`
- **claims_basic()** (4 connections) — `test/commondb/unit/services/test_user_manager_auto_create.py`
- **mock_organization_service()** (4 connections) — `test/commondb/unit/services/test_user_manager_auto_create.py`
- *... and 31 more nodes in this community*

## Relationships

- [Base User Manager & RBAC](Base_User_Manager_&_RBAC.md) (2 shared connections)
- [Casedb CaseSet CRUD & Tests](Casedb_CaseSet_CRUD_&_Tests.md) (2 shared connections)
- [RBAC/ABAC Policy Implementations](RBAC-ABAC_Policy_Implementations.md) (1 shared connections)
- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (1 shared connections)
- [Commondb Enums & Demo Data](Commondb_Enums_&_Demo_Data.md) (1 shared connections)
- [Commondb Organization Domain Models](Commondb_Organization_Domain_Models.md) (1 shared connections)

## Source Files

- `test/commondb/unit/services/test_user_manager_auto_create.py`

## Audit Trail

- EXTRACTED: 128 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*