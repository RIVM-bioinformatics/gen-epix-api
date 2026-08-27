# test_update_user_policy.py

> 30 nodes · cohesion 0.27

## Key Concepts

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
- **TestInitialChecks** (5 connections) — `test/commondb/unit/policies/test_update_user_policy.py`
- *... and 5 more nodes in this community*

## Relationships

- [commondb/domain/model/__init__.py](commondb-domain-model-__init__.py.md) (6 shared connections)
- [commondb/domain/enum.py](commondb-domain-enum.py.md) (5 shared connections)
- [CrudOperation](CrudOperation.md) (1 shared connections)
- [seqdb/domain/model/__init__.py](seqdb-domain-model-__init__.py.md) (1 shared connections)
- [casedb/domain/command/__init__.py](casedb-domain-command-__init__.py.md) (1 shared connections)

## Source Files

- `test/commondb/unit/policies/test_update_user_policy.py`

## Audit Trail

- EXTRACTED: 127 (98%)
- INFERRED: 3 (2%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*