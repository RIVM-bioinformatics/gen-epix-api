# RBAC/ABAC Policy Implementations

> 118 nodes · cohesion 0.03

## Key Concepts

- **AppImplDetails** (70 connections) — `gen_epix/commondb/app_impl_details.py`
- **app_impl_details.py** (35 connections) — `gen_epix/commondb/app_impl_details.py`
- **services/user_manager.py** (24 connections) — `gen_epix/commondb/services/user_manager.py`
- **BaseAbacService** (23 connections) — `gen_epix/commondb/domain/service/abac.py`
- **api/ontology.py** (16 connections) — `gen_epix/casedb/api/ontology.py`
- **commondb/policies/__init__.py** (16 connections) — `gen_epix/commondb/policies/__init__.py`
- **IsOrganizationAdminPolicy** (15 connections) — `gen_epix/commondb/policies/is_organization_admin_policy.py`
- **commondb/policies/read_organization_results_only_policy.py** (14 connections) — `gen_epix/commondb/policies/read_organization_results_only_policy.py`
- **ReadOrganizationResultsOnlyPolicy** (14 connections) — `gen_epix/commondb/policies/read_organization_results_only_policy.py`
- **commondb/policies/update_user_policy.py** (14 connections) — `gen_epix/commondb/policies/update_user_policy.py`
- **commondb/policies/is_organization_admin_policy.py** (13 connections) — `gen_epix/commondb/policies/is_organization_admin_policy.py`
- **commondb/policies/read_self_results_only_policy.py** (13 connections) — `gen_epix/commondb/policies/read_self_results_only_policy.py`
- **omopdb/policies/__init__.py** (11 connections) — `gen_epix/omopdb/policies/__init__.py`
- **ReadSelfResultsOnlyPolicy** (9 connections) — `gen_epix/commondb/policies/read_self_results_only_policy.py`
- **seqdb/policies/__init__.py** (9 connections) — `gen_epix/seqdb/policies/__init__.py`
- **.get_mapped_class()** (8 connections) — `gen_epix/commondb/app_impl_details.py`
- **._filter_users_by_organization()** (6 connections) — `gen_epix/commondb/policies/read_organization_results_only_policy.py`
- **casedb/policies/read_self_results_only_policy.py** (5 connections) — `gen_epix/casedb/policies/read_self_results_only_policy.py`
- **.rev_role_map()** (5 connections) — `gen_epix/commondb/app_impl_details.py`
- **Enum** (5 connections)
- **UUID** (5 connections)
- **.filter()** (5 connections) — `gen_epix/commondb/policies/read_organization_results_only_policy.py`
- **ReadSelfResultsOnlyPolicy** (4 connections) — `gen_epix/casedb/policies/read_self_results_only_policy.py`
- **.idp_user_dependency()** (4 connections) — `gen_epix/commondb/app_impl_details.py`
- **.new_user_dependency()** (4 connections) — `gen_epix/commondb/app_impl_details.py`
- *... and 93 more nodes in this community*

## Relationships

- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (19 shared connections)
- [Casedb Domain CRUD Commands](Casedb_Domain_CRUD_Commands.md) (12 shared connections)
- [Commondb Enums & Demo Data](Commondb_Enums_&_Demo_Data.md) (12 shared connections)
- [ABAC API Routers](ABAC_API_Routers.md) (11 shared connections)
- [App Composition & Service Wiring](App_Composition_&_Service_Wiring.md) (10 shared connections)
- [ABAC Base Policies](ABAC_Base_Policies.md) (10 shared connections)
- [Org Results Policy Tests](Org_Results_Policy_Tests.md) (8 shared connections)
- [Organization Service](Organization_Service.md) (8 shared connections)
- [Casedb ABAC & Filter Logic](Casedb_ABAC_&_Filter_Logic.md) (6 shared connections)
- [Commondb Organization Domain Models](Commondb_Organization_Domain_Models.md) (6 shared connections)
- [Update User ABAC Policy](Update_User_ABAC_Policy.md) (6 shared connections)
- [Case API Endpoints](Case_API_Endpoints.md) (5 shared connections)

## Source Files

- `gen_epix/casedb/api/ontology.py`
- `gen_epix/casedb/policies/read_self_results_only_policy.py`
- `gen_epix/commondb/app_impl_details.py`
- `gen_epix/commondb/domain/service/abac.py`
- `gen_epix/commondb/policies/__init__.py`
- `gen_epix/commondb/policies/is_organization_admin_policy.py`
- `gen_epix/commondb/policies/read_organization_results_only_policy.py`
- `gen_epix/commondb/policies/read_self_results_only_policy.py`
- `gen_epix/commondb/policies/update_user_policy.py`
- `gen_epix/commondb/services/user_manager.py`
- `gen_epix/omopdb/policies/__init__.py`
- `gen_epix/omopdb/policies/is_organization_admin_policy.py`
- `gen_epix/omopdb/policies/read_organization_results_only_policy.py`
- `gen_epix/omopdb/policies/read_self_results_only_policy.py`
- `gen_epix/seqdb/policies/__init__.py`
- `gen_epix/seqdb/policies/is_organization_admin_policy.py`
- `gen_epix/seqdb/policies/read_organization_results_only_policy.py`
- `gen_epix/seqdb/policies/read_self_results_only_policy.py`
- `test/commondb/unit/policies/test_read_organization_results_only_policy.py`

## Audit Trail

- EXTRACTED: 336 (92%)
- INFERRED: 29 (8%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*