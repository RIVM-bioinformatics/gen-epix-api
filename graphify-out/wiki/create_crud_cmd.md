# .create_crud_cmd

> 34 nodes · cohesion 0.11

## Key Concepts

- **.create_crud_cmd()** (18 connections) — `test/commondb/unit/policies/test_read_organization_results_only_policy.py`
- **.create_org_admin_policy()** (13 connections) — `test/commondb/unit/policies/test_read_organization_results_only_policy.py`
- **BasePolicyTestCase** (12 connections) — `test/commondb/unit/policies/test_read_organization_results_only_policy.py`
- **TestOrganizationIdFiltering** (9 connections) — `test/commondb/unit/policies/test_read_organization_results_only_policy.py`
- **TestPassThroughAndErrors** (9 connections) — `test/commondb/unit/policies/test_read_organization_results_only_policy.py`
- **TestUserIdFiltering** (8 connections) — `test/commondb/unit/policies/test_read_organization_results_only_policy.py`
- **.create_user()** (5 connections) — `test/commondb/unit/policies/test_read_organization_results_only_policy.py`
- **UUID** (4 connections)
- **.test_exempt_roles_passthrough()** (4 connections) — `test/commondb/unit/policies/test_read_organization_results_only_policy.py`
- **scenario_ids** (3 connections)
- **.test_read_all_filters_with_abac_orgs_and_user_org()** (3 connections) — `test/commondb/unit/policies/test_read_organization_results_only_policy.py`
- **.test_read_all_filters_with_no_abac_orgs_uses_user_org_only()** (3 connections) — `test/commondb/unit/policies/test_read_organization_results_only_policy.py`
- **.test_read_one_not_in_org_raises_unauthorized()** (3 connections) — `test/commondb/unit/policies/test_read_organization_results_only_policy.py`
- **.test_read_some_mixed_orgs_raises_unauthorized()** (3 connections) — `test/commondb/unit/policies/test_read_organization_results_only_policy.py`
- **.test_non_read_operation_passthrough()** (3 connections) — `test/commondb/unit/policies/test_read_organization_results_only_policy.py`
- **.test_user_id_read_all_filters_and_app_handle_called()** (3 connections) — `test/commondb/unit/policies/test_read_organization_results_only_policy.py`
- **.test_user_id_read_one_not_allowed_raises()** (3 connections) — `test/commondb/unit/policies/test_read_organization_results_only_policy.py`
- **.test_user_id_read_some_not_subset_raises()** (3 connections) — `test/commondb/unit/policies/test_read_organization_results_only_policy.py`
- **User** (2 connections)
- **.test_unrecognized_crud_command_raises_not_implemented()** (2 connections) — `test/commondb/unit/policies/test_read_organization_results_only_policy.py`
- **.test_no_user_raises_service_exception()** (2 connections) — `test/commondb/unit/policies/test_read_organization_results_only_policy.py`
- **CrudCommand** (1 connections)
- **Model** (1 connections)
- **OrganizationAdminPolicy** (1 connections)
- **Create a user with optional roles and organization.** (1 connections) — `test/commondb/unit/policies/test_read_organization_results_only_policy.py`
- *... and 9 more nodes in this community*

## Relationships

- [commondb/domain/model/__init__.py](commondb-domain-model-__init__.py.md) (8 shared connections)
- [services/user_manager.py](services-user_manager.py.md) (1 shared connections)
- [CrudOperation](CrudOperation.md) (1 shared connections)

## Source Files

- `test/commondb/unit/policies/test_read_organization_results_only_policy.py`

## Audit Trail

- EXTRACTED: 66 (96%)
- INFERRED: 3 (4%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*