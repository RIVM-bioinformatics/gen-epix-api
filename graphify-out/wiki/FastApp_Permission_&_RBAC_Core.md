# FastApp Permission & RBAC Core

> 54 nodes · cohesion 0.06

## Key Concepts

- **BaseRbacService** (42 connections) — `gen_epix/fastapp/services/rbac/service.py`
- **Hashable** (12 connections)
- **.register_roles()** (9 connections) — `gen_epix/fastapp/services/rbac/service.py`
- **.register_rbac_policies()** (8 connections) — `gen_epix/fastapp/services/rbac/service.py`
- **.retrieve_user_permissions()** (7 connections) — `gen_epix/fastapp/services/rbac/service.py`
- **Command** (7 connections)
- **.expand_hierarchical_role_permissions()** (6 connections) — `gen_epix/fastapp/services/rbac/service.py`
- **.register_role()** (6 connections) — `gen_epix/fastapp/services/rbac/service.py`
- **.retrieve_user_roles()** (6 connections) — `gen_epix/fastapp/services/rbac/service.py`
- **._validate_and_register_role()** (6 connections) — `gen_epix/fastapp/services/rbac/service.py`
- **._compile_subrole_permissions()** (5 connections) — `gen_epix/fastapp/services/rbac/service.py`
- **.retrieve_user_has_more_permissions()** (5 connections) — `gen_epix/fastapp/services/rbac/service.py`
- **User** (5 connections)
- **.get_command_classes_with_rbac()** (4 connections) — `gen_epix/fastapp/services/rbac/service.py`
- **._get_permissions()** (4 connections) — `gen_epix/fastapp/services/rbac/service.py`
- **.get_rbac_permissions_for_command_class()** (4 connections) — `gen_epix/fastapp/services/rbac/service.py`
- **.retrieve_user_has_all_rbac_permissions()** (4 connections) — `gen_epix/fastapp/services/rbac/service.py`
- **.retrieve_user_is_non_rbac_authorized()** (4 connections) — `gen_epix/fastapp/services/rbac/service.py`
- **.retrieve_user_is_root()** (4 connections) — `gen_epix/fastapp/services/rbac/service.py`
- **Any** (4 connections)
- **.get_roles()** (3 connections) — `gen_epix/fastapp/services/rbac/service.py`
- **.get_root_permissions()** (3 connections) — `gen_epix/fastapp/services/rbac/service.py`
- **.get_sub_roles()** (3 connections) — `gen_epix/fastapp/services/rbac/service.py`
- **.__init__()** (3 connections) — `gen_epix/fastapp/services/rbac/service.py`
- **.permissions_by_role()** (3 connections) — `gen_epix/fastapp/services/rbac/service.py`
- *... and 29 more nodes in this community*

## Relationships

- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (14 shared connections)
- [FastApp Domain Registry Core](FastApp_Domain_Registry_Core.md) (11 shared connections)
- [ABAC Base Policies](ABAC_Base_Policies.md) (3 shared connections)
- [RBAC/ABAC Policy Implementations](RBAC-ABAC_Policy_Implementations.md) (1 shared connections)
- [Organization Service](Organization_Service.md) (1 shared connections)
- [Org Results Policy Tests](Org_Results_Policy_Tests.md) (1 shared connections)
- [Fastapp CRUD Command Tests](Fastapp_CRUD_Command_Tests.md) (1 shared connections)
- [Base Service Class](Base_Service_Class.md) (1 shared connections)

## Source Files

- `gen_epix/fastapp/services/rbac/service.py`

## Audit Trail

- EXTRACTED: 118 (98%)
- INFERRED: 2 (2%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*