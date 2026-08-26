# Org Results Policy Tests

> 41 nodes · cohesion 0.09

## Key Concepts

- **test_read_organization_results_only_policy.py** (20 connections) — `test/commondb/unit/policies/test_read_organization_results_only_policy.py`
- **.create_crud_cmd()** (18 connections) — `test/commondb/unit/policies/test_read_organization_results_only_policy.py`
- **.create_org_admin_policy()** (13 connections) — `test/commondb/unit/policies/test_read_organization_results_only_policy.py`
- **BasePolicyTestCase** (12 connections) — `test/commondb/unit/policies/test_read_organization_results_only_policy.py`
- **TestOrganizationIdFiltering** (9 connections) — `test/commondb/unit/policies/test_read_organization_results_only_policy.py`
- **TestPassThroughAndErrors** (9 connections) — `test/commondb/unit/policies/test_read_organization_results_only_policy.py`
- **TestUserIdFiltering** (8 connections) — `test/commondb/unit/policies/test_read_organization_results_only_policy.py`
- **casedb/policies/read_organization_results_only_policy.py** (5 connections) — `gen_epix/casedb/policies/read_organization_results_only_policy.py`
- **ReadOrganizationResultsOnlyPolicy** (5 connections) — `gen_epix/casedb/policies/read_organization_results_only_policy.py`
- **.create_user()** (5 connections) — `test/commondb/unit/policies/test_read_organization_results_only_policy.py`
- **UUID** (4 connections)
- **.test_exempt_roles_passthrough()** (4 connections) — `test/commondb/unit/policies/test_read_organization_results_only_policy.py`
- **.__init__()** (3 connections) — `gen_epix/casedb/policies/read_organization_results_only_policy.py`
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
- *... and 16 more nodes in this community*

## Relationships

- [RBAC/ABAC Policy Implementations](RBAC-ABAC_Policy_Implementations.md) (8 shared connections)
- [Casedb CaseSet CRUD & Tests](Casedb_CaseSet_CRUD_&_Tests.md) (3 shared connections)
- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (3 shared connections)
- [Casedb Domain Enums & Policy](Casedb_Domain_Enums_&_Policy.md) (2 shared connections)
- [Casedb Domain CRUD Commands](Casedb_Domain_CRUD_Commands.md) (2 shared connections)
- [Abac Service Access Control](Abac_Service_Access_Control.md) (1 shared connections)
- [FastApp Permission & RBAC Core](FastApp_Permission_&_RBAC_Core.md) (1 shared connections)
- [User Manager Auto-Create Logic](User_Manager_Auto-Create_Logic.md) (1 shared connections)
- [Commondb Enums & Demo Data](Commondb_Enums_&_Demo_Data.md) (1 shared connections)
- [Commondb Organization Domain Models](Commondb_Organization_Domain_Models.md) (1 shared connections)
- [Organization Service](Organization_Service.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/policies/read_organization_results_only_policy.py`
- `test/commondb/unit/policies/test_read_organization_results_only_policy.py`

## Audit Trail

- EXTRACTED: 91 (97%)
- INFERRED: 3 (3%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*