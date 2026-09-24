# Role Registration Tests

> 24 nodes · cohesion 0.08

## Key Concepts

- **TestRoleRegistration** (15 connections) — `test/fastapp/unit/services/rbac/test_fastapp_base_rbac_service.py`
- **.test_register_role_invalid_permissions_fails()** (3 connections) — `test/fastapp/unit/services/rbac/test_fastapp_base_rbac_service.py`
- **.test_register_role_existing_role_with_update_succeeds()** (2 connections) — `test/fastapp/unit/services/rbac/test_fastapp_base_rbac_service.py`
- **.test_register_role_existing_role_without_update_fails()** (2 connections) — `test/fastapp/unit/services/rbac/test_fastapp_base_rbac_service.py`
- **.test_register_role_new_role_succeeds()** (2 connections) — `test/fastapp/unit/services/rbac/test_fastapp_base_rbac_service.py`
- **.test_register_roles_multiple_roles_succeeds()** (2 connections) — `test/fastapp/unit/services/rbac/test_fastapp_base_rbac_service.py`
- **.test_register_roles_with_root_role_adds_missing_permissions()** (2 connections) — `test/fastapp/unit/services/rbac/test_fastapp_base_rbac_service.py`
- **.test_register_roles_with_root_role_missing_permissions_raises()** (2 connections) — `test/fastapp/unit/services/rbac/test_fastapp_base_rbac_service.py`
- **.test_unregister_role_existing_role_succeeds()** (2 connections) — `test/fastapp/unit/services/rbac/test_fastapp_base_rbac_service.py`
- **.test_unregister_role_non_existing_role_fails()** (2 connections) — `test/fastapp/unit/services/rbac/test_fastapp_base_rbac_service.py`
- **.test_verify_roles_exist_for_all_permission_fails_when_missing_roles()** (2 connections) — `test/fastapp/unit/services/rbac/test_fastapp_base_rbac_service.py`
- **.test_verify_roles_exist_for_all_permission_succeeds_when_all_covered()** (2 connections) — `test/fastapp/unit/services/rbac/test_fastapp_base_rbac_service.py`
- **Test role registration and management.** (1 connections) — `test/fastapp/unit/services/rbac/test_fastapp_base_rbac_service.py`
- **Test registering a new role with permissions.** (1 connections) — `test/fastapp/unit/services/rbac/test_fastapp_base_rbac_service.py`
- **Test registering role with invalid permissions fails.** (1 connections) — `test/fastapp/unit/services/rbac/test_fastapp_base_rbac_service.py`
- **Test registering existing role without update fails.** (1 connections) — `test/fastapp/unit/services/rbac/test_fastapp_base_rbac_service.py`
- **Test updating existing role succeeds.** (1 connections) — `test/fastapp/unit/services/rbac/test_fastapp_base_rbac_service.py`
- **Test registering multiple roles at once.** (1 connections) — `test/fastapp/unit/services/rbac/test_fastapp_base_rbac_service.py`
- **Test registering roles with root role adds all missing permissions.** (1 connections) — `test/fastapp/unit/services/rbac/test_fastapp_base_rbac_service.py`
- **Test registering roles with root role and missing permissions raises error.** (1 connections) — `test/fastapp/unit/services/rbac/test_fastapp_base_rbac_service.py`
- **Test unregistering existing role succeeds.** (1 connections) — `test/fastapp/unit/services/rbac/test_fastapp_base_rbac_service.py`
- **Test unregistering non-existing role fails.** (1 connections) — `test/fastapp/unit/services/rbac/test_fastapp_base_rbac_service.py`
- **Test verification succeeds when all permissions have roles.** (1 connections) — `test/fastapp/unit/services/rbac/test_fastapp_base_rbac_service.py`
- **Test verification fails when some permissions have no roles.** (1 connections) — `test/fastapp/unit/services/rbac/test_fastapp_base_rbac_service.py`

## Relationships

- [RBAC Service Tests](RBAC_Service_Tests.md) (3 shared connections)
- [Domain Registry & ABAC Policies](Domain_Registry_&_ABAC_Policies.md) (1 shared connections)

## Source Files

- `test/fastapp/unit/services/rbac/test_fastapp_base_rbac_service.py`

## Audit Trail

- EXTRACTED: 27 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*