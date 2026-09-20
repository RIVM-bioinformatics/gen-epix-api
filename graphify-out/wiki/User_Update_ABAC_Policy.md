# User Update ABAC Policy

> 52 nodes · cohesion 0.11

## Key Concepts

- **UpdateUserPolicy** (18 connections) — `gen_epix/commondb/policies/update_user_policy.py`
- **test_update_user_policy.py** (18 connections) — `test/commondb/unit/policies/test_update_user_policy.py`
- **_make_abac_service()** (18 connections) — `test/commondb/unit/policies/test_update_user_policy.py`
- **_make_policy()** (18 connections) — `test/commondb/unit/policies/test_update_user_policy.py`
- **_make_user()** (18 connections) — `test/commondb/unit/policies/test_update_user_policy.py`
- **_make_role_set_map()** (17 connections) — `test/commondb/unit/policies/test_update_user_policy.py`
- **TestUpdateCommand** (12 connections) — `test/commondb/unit/policies/test_update_user_policy.py`
- **_make_update_cmd()** (11 connections) — `test/commondb/unit/policies/test_update_user_policy.py`
- **TestInviteCommand** (9 connections) — `test/commondb/unit/policies/test_update_user_policy.py`
- **_make_invite_cmd()** (8 connections) — `test/commondb/unit/policies/test_update_user_policy.py`
- **.test_app_admin_invite_target_with_equal_permissions_disallowed()** (8 connections) — `test/commondb/unit/policies/test_update_user_policy.py`
- **.test_app_admin_invite_target_with_less_permissions_allowed()** (8 connections) — `test/commondb/unit/policies/test_update_user_policy.py`
- **_set_permission_side_effect()** (7 connections) — `test/commondb/unit/policies/test_update_user_policy.py`
- **.test_app_admin_update_target_with_equal_permissions_disallowed()** (7 connections) — `test/commondb/unit/policies/test_update_user_policy.py`
- **.test_app_admin_update_target_with_less_permissions_allowed()** (7 connections) — `test/commondb/unit/policies/test_update_user_policy.py`
- **.test_org_admin_update_only_allowed_within_admin_orgs_and_less_permissions()** (7 connections) — `test/commondb/unit/policies/test_update_user_policy.py`
- **TestInitialChecks** (6 connections) — `test/commondb/unit/policies/test_update_user_policy.py`
- **.test_invite_self_disallowed_even_for_root()** (6 connections) — `test/commondb/unit/policies/test_update_user_policy.py`
- **.test_root_can_invite_anyone()** (6 connections) — `test/commondb/unit/policies/test_update_user_policy.py`
- **.test_user_below_org_admin_cannot_invite()** (6 connections) — `test/commondb/unit/policies/test_update_user_policy.py`
- **.test_org_admin_cannot_change_organization()** (6 connections) — `test/commondb/unit/policies/test_update_user_policy.py`
- **.test_org_admin_update_disallowed_when_not_admin_of_target_org()** (6 connections) — `test/commondb/unit/policies/test_update_user_policy.py`
- **.test_org_admin_update_target_with_non_org_roles_disallowed()** (6 connections) — `test/commondb/unit/policies/test_update_user_policy.py`
- **.test_root_can_update_anyone()** (6 connections) — `test/commondb/unit/policies/test_update_user_policy.py`
- **.test_user_below_org_admin_cannot_update()** (6 connections) — `test/commondb/unit/policies/test_update_user_policy.py`
- *... and 27 more nodes in this community*

## Relationships

- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (9 shared connections)
- [Role Generation & Hierarchy](Role_Generation_&_Hierarchy.md) (9 shared connections)
- [Seqdb Sequence Retrieval Commands](Seqdb_Sequence_Retrieval_Commands.md) (2 shared connections)
- [Organization & ABAC Models](Organization_&_ABAC_Models.md) (2 shared connections)
- [Casedb Policy Adapters](Casedb_Policy_Adapters.md) (1 shared connections)
- [Organization Admin Policy](Organization_Admin_Policy.md) (1 shared connections)
- [Commondb ABAC Policies](Commondb_ABAC_Policies.md) (1 shared connections)
- [Domain Registry & ABAC Policies](Domain_Registry_&_ABAC_Policies.md) (1 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (1 shared connections)

## Source Files

- `gen_epix/commondb/policies/update_user_policy.py`
- `gen_epix/seqdb/policies/update_user_policy.py`
- `test/commondb/unit/policies/test_update_user_policy.py`

## Audit Trail

- EXTRACTED: 158 (93%)
- INFERRED: 11 (7%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*