# Update User ABAC Policy

> 51 nodes · cohesion 0.11

## Key Concepts

- **UpdateUserPolicy** (19 connections) — `gen_epix/commondb/policies/update_user_policy.py`
- **test_update_user_policy.py** (18 connections) — `test/commondb/unit/policies/test_update_user_policy.py`
- **_make_policy()** (18 connections) — `test/commondb/unit/policies/test_update_user_policy.py`
- **_make_user()** (18 connections) — `test/commondb/unit/policies/test_update_user_policy.py`
- **_make_abac_service()** (17 connections) — `test/commondb/unit/policies/test_update_user_policy.py`
- **_make_role_set_map()** (17 connections) — `test/commondb/unit/policies/test_update_user_policy.py`
- **_make_update_cmd()** (11 connections) — `test/commondb/unit/policies/test_update_user_policy.py`
- **TestUpdateCommand** (11 connections) — `test/commondb/unit/policies/test_update_user_policy.py`
- **_make_invite_cmd()** (8 connections) — `test/commondb/unit/policies/test_update_user_policy.py`
- **TestInviteCommand** (8 connections) — `test/commondb/unit/policies/test_update_user_policy.py`
- **.test_app_admin_invite_target_with_equal_permissions_disallowed()** (8 connections) — `test/commondb/unit/policies/test_update_user_policy.py`
- **.test_app_admin_invite_target_with_less_permissions_allowed()** (8 connections) — `test/commondb/unit/policies/test_update_user_policy.py`
- **_set_permission_side_effect()** (7 connections) — `test/commondb/unit/policies/test_update_user_policy.py`
- **.test_app_admin_update_target_with_equal_permissions_disallowed()** (7 connections) — `test/commondb/unit/policies/test_update_user_policy.py`
- **.test_app_admin_update_target_with_less_permissions_allowed()** (7 connections) — `test/commondb/unit/policies/test_update_user_policy.py`
- **.test_org_admin_update_only_allowed_within_admin_orgs_and_less_permissions()** (7 connections) — `test/commondb/unit/policies/test_update_user_policy.py`
- **User** (6 connections)
- **.test_invite_self_disallowed_even_for_root()** (6 connections) — `test/commondb/unit/policies/test_update_user_policy.py`
- **.test_root_can_invite_anyone()** (6 connections) — `test/commondb/unit/policies/test_update_user_policy.py`
- **.test_user_below_org_admin_cannot_invite()** (6 connections) — `test/commondb/unit/policies/test_update_user_policy.py`
- **.test_org_admin_cannot_change_organization()** (6 connections) — `test/commondb/unit/policies/test_update_user_policy.py`
- **.test_org_admin_update_disallowed_when_not_admin_of_target_org()** (6 connections) — `test/commondb/unit/policies/test_update_user_policy.py`
- **.test_org_admin_update_target_with_non_org_roles_disallowed()** (6 connections) — `test/commondb/unit/policies/test_update_user_policy.py`
- **.test_root_can_update_anyone()** (6 connections) — `test/commondb/unit/policies/test_update_user_policy.py`
- **.test_user_below_org_admin_cannot_update()** (6 connections) — `test/commondb/unit/policies/test_update_user_policy.py`
- *... and 26 more nodes in this community*

## Relationships

- [RBAC/ABAC Policy Implementations](RBAC-ABAC_Policy_Implementations.md) (6 shared connections)
- [Commondb Enums & Demo Data](Commondb_Enums_&_Demo_Data.md) (3 shared connections)
- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (2 shared connections)
- [Commondb Organization Domain Models](Commondb_Organization_Domain_Models.md) (2 shared connections)
- [Upload/ETL Result Model](Upload-ETL_Result_Model.md) (2 shared connections)
- [Casedb Domain Enums & Policy](Casedb_Domain_Enums_&_Policy.md) (1 shared connections)
- [ABAC Base Policies](ABAC_Base_Policies.md) (1 shared connections)
- [Organization Service](Organization_Service.md) (1 shared connections)
- [Base Model & Identifiers](Base_Model_&_Identifiers.md) (1 shared connections)
- [Casedb CaseSet CRUD & Tests](Casedb_CaseSet_CRUD_&_Tests.md) (1 shared connections)
- [Casedb Domain CRUD Commands](Casedb_Domain_CRUD_Commands.md) (1 shared connections)

## Source Files

- `gen_epix/commondb/policies/update_user_policy.py`
- `gen_epix/omopdb/policies/update_user_policy.py`
- `gen_epix/seqdb/policies/update_user_policy.py`
- `test/commondb/unit/policies/test_update_user_policy.py`

## Audit Trail

- EXTRACTED: 161 (97%)
- INFERRED: 5 (3%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*