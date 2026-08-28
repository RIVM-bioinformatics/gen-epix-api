# TestUserPermissions

> 15 nodes · cohesion 0.14

## Key Concepts

- **TestUserPermissions** (11 connections) — `test/fastapp/unit/services/rbac/test_fastapp_base_rbac_service.py`
- **Test checking if user has more permissions than another user.** (2 connections) — `test/fastapp/unit/services/rbac/test_fastapp_base_rbac_service.py`
- **.test_retrieve_user_has_all_rbac_permissions_false_when_missing()** (2 connections) — `test/fastapp/unit/services/rbac/test_fastapp_base_rbac_service.py`
- **.test_retrieve_user_has_all_rbac_permissions_true_when_has_all()** (2 connections) — `test/fastapp/unit/services/rbac/test_fastapp_base_rbac_service.py`
- **.test_retrieve_user_has_more_permissions_false_when_subset()** (2 connections) — `test/fastapp/unit/services/rbac/test_fastapp_base_rbac_service.py`
- **.test_retrieve_user_has_more_permissions_with_roles_target()** (2 connections) — `test/fastapp/unit/services/rbac/test_fastapp_base_rbac_service.py`
- **.test_retrieve_user_has_more_permissions_with_user_target()** (2 connections) — `test/fastapp/unit/services/rbac/test_fastapp_base_rbac_service.py`
- **.test_retrieve_user_permissions_empty_roles_returns_empty_set()** (2 connections) — `test/fastapp/unit/services/rbac/test_fastapp_base_rbac_service.py`
- **.test_retrieve_user_permissions_returns_union_of_role_permissions()** (2 connections) — `test/fastapp/unit/services/rbac/test_fastapp_base_rbac_service.py`
- **Test user permission retrieval and authorization checks.** (1 connections) — `test/fastapp/unit/services/rbac/test_fastapp_base_rbac_service.py`
- **Test that user permissions are union of all their role permissions.** (1 connections) — `test/fastapp/unit/services/rbac/test_fastapp_base_rbac_service.py`
- **Test that user with no roles has no permissions.** (1 connections) — `test/fastapp/unit/services/rbac/test_fastapp_base_rbac_service.py`
- **Test that user has all RBAC permissions when they actually do.** (1 connections) — `test/fastapp/unit/services/rbac/test_fastapp_base_rbac_service.py`
- **Test that user doesn't have all RBAC permissions when missing some.** (1 connections) — `test/fastapp/unit/services/rbac/test_fastapp_base_rbac_service.py`
- **Test that user doesn't have more permissions when they're a subset.** (1 connections) — `test/fastapp/unit/services/rbac/test_fastapp_base_rbac_service.py`

## Relationships

- [BaseRbacServiceTestCase](BaseRbacServiceTestCase.md) (2 shared connections)
- [Permission](Permission.md) (1 shared connections)

## Source Files

- `test/fastapp/unit/services/rbac/test_fastapp_base_rbac_service.py`

## Audit Trail

- EXTRACTED: 18 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*