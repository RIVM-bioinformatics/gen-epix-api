# User Read Policy Tests

> 35 nodes · cohesion 0.09

## Key Concepts

- **._make_user_cmd()** (18 connections) — `test/commondb/unit/policies/test_read_user_policy.py`
- **._make_user()** (15 connections) — `test/commondb/unit/policies/test_read_user_policy.py`
- **._make_org_admin_policy()** (13 connections) — `test/commondb/unit/policies/test_read_user_policy.py`
- **._users()** (7 connections) — `test/commondb/unit/policies/test_read_user_policy.py`
- **.test_read_all_org_admin_filters_and_allows_inactive()** (5 connections) — `test/commondb/unit/policies/test_read_user_policy.py`
- **.test_read_one_org_admin_allows_inactive()** (5 connections) — `test/commondb/unit/policies/test_read_user_policy.py`
- **.test_read_some_org_admin_authorizes_subset()** (5 connections) — `test/commondb/unit/policies/test_read_user_policy.py`
- **.test_read_some_org_admin_denies_outside_org()** (5 connections) — `test/commondb/unit/policies/test_read_user_policy.py`
- **.test_read_all_regular_user_filters_only_self_and_active_admins()** (5 connections) — `test/commondb/unit/policies/test_read_user_policy.py`
- **.test_read_one_regular_user_denies_other_org_or_inactive()** (5 connections) — `test/commondb/unit/policies/test_read_user_policy.py`
- **.test_read_some_regular_user_allows_self_and_active_admins()** (5 connections) — `test/commondb/unit/policies/test_read_user_policy.py`
- **.test_read_some_regular_user_denies_other_org()** (5 connections) — `test/commondb/unit/policies/test_read_user_policy.py`
- **UUID** (4 connections)
- **.test_app_admin_returns_unmodified()** (4 connections) — `test/commondb/unit/policies/test_read_user_policy.py`
- **.test_read_one_regular_user_allows_self()** (4 connections) — `test/commondb/unit/policies/test_read_user_policy.py`
- **.test_none_user_id_raises_assertion()** (4 connections) — `test/commondb/unit/policies/test_read_user_policy.py`
- **.test_operation_not_read_returns_unmodified()** (4 connections) — `test/commondb/unit/policies/test_read_user_policy.py`
- **User** (3 connections)
- **Any** (1 connections)
- **Non-read operations should return results unchanged.** (1 connections) — `test/commondb/unit/policies/test_read_user_policy.py`
- **User without id should assert.** (1 connections) — `test/commondb/unit/policies/test_read_user_policy.py`
- **APP_ADMIN should receive unmodified results for READ operations.** (1 connections) — `test/commondb/unit/policies/test_read_user_policy.py`
- **READ_ALL for org admin should include users in admin orgs and admins, including…** (1 connections) — `test/commondb/unit/policies/test_read_user_policy.py`
- **READ_SOME for org admin should authorize when all users are within admin orgs.** (1 connections) — `test/commondb/unit/policies/test_read_user_policy.py`
- **READ_SOME should raise when any user is outside admin orgs.** (1 connections) — `test/commondb/unit/policies/test_read_user_policy.py`
- *... and 10 more nodes in this community*

## Relationships

- [Read User Policy Tests](Read_User_Policy_Tests.md) (18 shared connections)
- [Read User Policy Filter](Read_User_Policy_Filter.md) (1 shared connections)
- [Casedb CaseSet CRUD & Tests](Casedb_CaseSet_CRUD_&_Tests.md) (1 shared connections)
- [Casedb Domain CRUD Commands](Casedb_Domain_CRUD_Commands.md) (1 shared connections)

## Source Files

- `test/commondb/unit/policies/test_read_user_policy.py`

## Audit Trail

- EXTRACTED: 77 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*