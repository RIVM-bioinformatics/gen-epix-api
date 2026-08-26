# Base User Manager & RBAC

> 22 nodes · cohesion 0.19

## Key Concepts

- **UserManager** (27 connections) — `gen_epix/commondb/services/user_manager.py`
- **User** (9 connections)
- **Any** (7 connections)
- **.construct_user_instance_from_claims()** (6 connections) — `gen_epix/commondb/services/user_manager.py`
- **.create_new_user_from_token()** (6 connections) — `gen_epix/commondb/services/user_manager.py`
- **.create_root_user_from_claims()** (6 connections) — `gen_epix/commondb/services/user_manager.py`
- **get_email_from_claims()** (6 connections) — `gen_epix/fastapp/services/auth/util.py`
- **.auto_create_new_user()** (5 connections) — `gen_epix/commondb/services/user_manager.py`
- **.get_user_name_from_claims()** (5 connections) — `gen_epix/commondb/services/user_manager.py`
- **.generate_id()** (4 connections) — `gen_epix/commondb/services/user_manager.py`
- **.retrieve_user_by_id()** (4 connections) — `gen_epix/commondb/services/user_manager.py`
- **UUID** (3 connections)
- **.__init__()** (3 connections) — `gen_epix/commondb/services/user_manager.py`
- **.is_existing_user_by_key()** (3 connections) — `gen_epix/commondb/services/user_manager.py`
- **.retrieve_user_permissions()** (3 connections) — `gen_epix/commondb/services/user_manager.py`
- **.get_user_key_from_claims()** (2 connections) — `gen_epix/commondb/services/user_manager.py`
- **.is_root_user()** (2 connections) — `gen_epix/commondb/services/user_manager.py`
- **.is_root_user_claims()** (2 connections) — `gen_epix/commondb/services/user_manager.py`
- **.retrieve_user_by_key()** (2 connections) — `gen_epix/commondb/services/user_manager.py`
- **.update_user_name()** (2 connections) — `gen_epix/commondb/services/user_manager.py`
- **BaseRbacService** (1 connections)
- **BaseUserManager** (1 connections)

## Relationships

- [RBAC/ABAC Policy Implementations](RBAC-ABAC_Policy_Implementations.md) (4 shared connections)
- [App Composition & Service Wiring](App_Composition_&_Service_Wiring.md) (4 shared connections)
- [Commondb Auth Tests](Commondb_Auth_Tests.md) (2 shared connections)
- [User Manager Auto-Create Tests](User_Manager_Auto-Create_Tests.md) (2 shared connections)
- [User Claims Name Extraction](User_Claims_Name_Extraction.md) (2 shared connections)
- [Identity Providers Command](Identity_Providers_Command.md) (2 shared connections)
- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (1 shared connections)
- [OMOP Model Validators](OMOP_Model_Validators.md) (1 shared connections)
- [Organization Service](Organization_Service.md) (1 shared connections)
- [Casedb Case CRUD Commands](Casedb_Case_CRUD_Commands.md) (1 shared connections)
- [FastApp Domain Registry Core](FastApp_Domain_Registry_Core.md) (1 shared connections)

## Source Files

- `gen_epix/commondb/services/user_manager.py`
- `gen_epix/fastapp/services/auth/util.py`

## Audit Trail

- EXTRACTED: 64 (98%)
- INFERRED: 1 (2%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*