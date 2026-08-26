# FastApp Domain Registry Core

> 94 nodes · cohesion 0.05

## Key Concepts

- **Domain** (95 connections) — `gen_epix/fastapp/domain/domain.py`
- **Permission** (82 connections) — `gen_epix/fastapp/model.py`
- **Hashable** (25 connections)
- **Model** (19 connections)
- **Command** (16 connections)
- **.register_entity()** (11 connections) — `gen_epix/fastapp/domain/domain.py`
- **.get_dag_sorted_entities()** (9 connections) — `gen_epix/fastapp/domain/domain.py`
- **.register_command()** (9 connections) — `gen_epix/fastapp/domain/domain.py`
- **ApiPermission** (8 connections) — `gen_epix/casedb/api/organization.py`
- **._verify_command_exists()** (8 connections) — `gen_epix/fastapp/domain/domain.py`
- **._verify_service_type_exists()** (8 connections) — `gen_epix/fastapp/domain/domain.py`
- **CrudCommand** (8 connections)
- **TestContent** (8 connections) — `test/casedb/integration/content/test_casedb_content.py`
- **.get_model_links()** (7 connections) — `gen_epix/fastapp/domain/domain.py`
- **.get_permissions_for_model()** (7 connections) — `gen_epix/fastapp/domain/domain.py`
- **._link_new_command()** (7 connections) — `gen_epix/fastapp/domain/domain.py`
- **._verify_model_exists()** (7 connections) — `gen_epix/fastapp/domain/domain.py`
- **.get_entity_for_model()** (6 connections) — `gen_epix/fastapp/domain/domain.py`
- **.get_permissions_for_command()** (6 connections) — `gen_epix/fastapp/domain/domain.py`
- **.get_service_type_for_entity()** (6 connections) — `gen_epix/fastapp/domain/domain.py`
- **._update_entity_dag()** (6 connections) — `gen_epix/fastapp/domain/domain.py`
- **._verify_entity_exists()** (6 connections) — `gen_epix/fastapp/domain/domain.py`
- **._verify_permission_exists()** (6 connections) — `gen_epix/fastapp/domain/domain.py`
- **._associate_command_with_service()** (5 connections) — `gen_epix/fastapp/domain/domain.py`
- **._filter_entities()** (5 connections) — `gen_epix/fastapp/domain/domain.py`
- *... and 69 more nodes in this community*

## Relationships

- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (40 shared connections)
- [FastApp Entity & Model Core](FastApp_Entity_&_Model_Core.md) (30 shared connections)
- [FastApp Permission & RBAC Core](FastApp_Permission_&_RBAC_Core.md) (11 shared connections)
- [ABAC API Routers](ABAC_API_Routers.md) (7 shared connections)
- [Commondb Remote App Client](Commondb_Remote_App_Client.md) (5 shared connections)
- [Domain Entity Registration](Domain_Entity_Registration.md) (3 shared connections)
- [Organization Service](Organization_Service.md) (3 shared connections)
- [CRUD Endpoint Generation Helpers](CRUD_Endpoint_Generation_Helpers.md) (3 shared connections)
- [Remote App Test Base](Remote_App_Test_Base.md) (2 shared connections)
- [FastApp RBAC Service Tests](FastApp_RBAC_Service_Tests.md) (2 shared connections)
- [App Composition & Service Wiring](App_Composition_&_Service_Wiring.md) (2 shared connections)
- [Mock User Manager Tests](Mock_User_Manager_Tests.md) (2 shared connections)

## Source Files

- `gen_epix/casedb/api/organization.py`
- `gen_epix/fastapp/domain/domain.py`
- `gen_epix/fastapp/model.py`
- `gen_epix/fastapp/services/rbac/policy.py`
- `gen_epix/omopdb/api/organization.py`
- `gen_epix/seqdb/api/organization.py`
- `test/casedb/integration/content/test_casedb_content.py`

## Audit Trail

- EXTRACTED: 311 (89%)
- INFERRED: 39 (11%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*