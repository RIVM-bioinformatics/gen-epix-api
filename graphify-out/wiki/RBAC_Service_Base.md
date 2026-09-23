# RBAC Service Base

> 53 nodes · cohesion 0.06

## Key Concepts

- **BaseRbacService** (40 connections) — `gen_epix/fastapp/services/rbac/service.py`
- **Hashable** (12 connections)
- **Permission** (11 connections)
- **.register_roles()** (9 connections) — `gen_epix/fastapp/services/rbac/service.py`
- **.register_rbac_policies()** (8 connections) — `gen_epix/fastapp/services/rbac/service.py`
- **.retrieve_user_permissions()** (7 connections) — `gen_epix/fastapp/services/rbac/service.py`
- **._validate_and_register_role()** (7 connections) — `gen_epix/fastapp/services/rbac/service.py`
- **.register_role()** (6 connections) — `gen_epix/fastapp/services/rbac/service.py`
- **.retrieve_user_roles()** (6 connections) — `gen_epix/fastapp/services/rbac/service.py`
- **.retrieve_user_has_more_permissions()** (5 connections) — `gen_epix/fastapp/services/rbac/service.py`
- **User** (5 connections)
- **.get_command_classes_with_rbac()** (4 connections) — `gen_epix/fastapp/services/rbac/service.py`
- **.get_rbac_permissions_for_command_class()** (4 connections) — `gen_epix/fastapp/services/rbac/service.py`
- **.__init__()** (4 connections) — `gen_epix/fastapp/services/rbac/service.py`
- **.retrieve_user_has_all_rbac_permissions()** (4 connections) — `gen_epix/fastapp/services/rbac/service.py`
- **.retrieve_user_is_non_rbac_authorized()** (4 connections) — `gen_epix/fastapp/services/rbac/service.py`
- **.retrieve_user_is_root()** (4 connections) — `gen_epix/fastapp/services/rbac/service.py`
- **Any** (4 connections)
- **.get_roles()** (3 connections) — `gen_epix/fastapp/services/rbac/service.py`
- **.get_root_permissions()** (3 connections) — `gen_epix/fastapp/services/rbac/service.py`
- **.get_sub_roles()** (3 connections) — `gen_epix/fastapp/services/rbac/service.py`
- **.permissions_by_role()** (3 connections) — `gen_epix/fastapp/services/rbac/service.py`
- **.permissions_without_rbac()** (3 connections) — `gen_epix/fastapp/services/rbac/service.py`
- **.register_permission_without_rbac()** (3 connections) — `gen_epix/fastapp/services/rbac/service.py`
- **.roles_by_permission()** (3 connections) — `gen_epix/fastapp/services/rbac/service.py`
- *... and 28 more nodes in this community*

## Relationships

- [Domain Registry & ABAC Policies](Domain_Registry_&_ABAC_Policies.md) (6 shared connections)
- [RBAC Policy](RBAC_Policy.md) (4 shared connections)
- [RBAC Service Tests](RBAC_Service_Tests.md) (4 shared connections)
- [Seqdb Sequence Retrieval Commands](Seqdb_Sequence_Retrieval_Commands.md) (4 shared connections)
- [Commondb ABAC Policies](Commondb_ABAC_Policies.md) (1 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (1 shared connections)
- [FastApp Test Fixtures](FastApp_Test_Fixtures.md) (1 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (1 shared connections)
- [Organization Admin Policy Tests](Organization_Admin_Policy_Tests.md) (1 shared connections)

## Source Files

- `gen_epix/fastapp/services/rbac/service.py`

## Audit Trail

- EXTRACTED: 107 (96%)
- INFERRED: 4 (4%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*