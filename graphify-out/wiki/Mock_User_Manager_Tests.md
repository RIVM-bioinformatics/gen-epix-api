# Mock User Manager Tests

> 20 nodes · cohesion 0.18

## Key Concepts

- **UserManager** (23 connections) — `test/fastapp/user_manager.py`
- **User** (9 connections)
- **Any** (6 connections)
- **.auto_create_new_user()** (5 connections) — `test/fastapp/user_manager.py`
- **.create_root_user_from_claims()** (4 connections) — `test/fastapp/user_manager.py`
- **MockUser** (3 connections) — `test/fastapp/user_manager.py`
- **.construct_user_instance_from_claims()** (3 connections) — `test/fastapp/user_manager.py`
- **.create_new_user_from_token()** (3 connections) — `test/fastapp/user_manager.py`
- **.retrieve_user_by_id()** (3 connections) — `test/fastapp/user_manager.py`
- **.retrieve_user_permissions()** (3 connections) — `test/fastapp/user_manager.py`
- **Hashable** (2 connections)
- **.get_user_name_from_claims()** (2 connections) — `test/fastapp/user_manager.py`
- **.__init__()** (2 connections) — `test/fastapp/user_manager.py`
- **.is_existing_user_by_key()** (2 connections) — `test/fastapp/user_manager.py`
- **.is_root_user()** (2 connections) — `test/fastapp/user_manager.py`
- **.is_root_user_claims()** (2 connections) — `test/fastapp/user_manager.py`
- **.retrieve_user_by_key()** (2 connections) — `test/fastapp/user_manager.py`
- **.update_user_name()** (2 connections) — `test/fastapp/user_manager.py`
- **BaseModel** (1 connections)
- **BaseUserManager** (1 connections)

## Relationships

- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (4 shared connections)
- [Fastapp CRUD Command Tests](Fastapp_CRUD_Command_Tests.md) (3 shared connections)
- [FastApp Domain Registry Core](FastApp_Domain_Registry_Core.md) (2 shared connections)
- [OAuth Client Model](OAuth_Client_Model.md) (1 shared connections)
- [RBAC Service Test Setup](RBAC_Service_Test_Setup.md) (1 shared connections)
- [Casedb Case CRUD Commands](Casedb_Case_CRUD_Commands.md) (1 shared connections)

## Source Files

- `test/fastapp/user_manager.py`

## Audit Trail

- EXTRACTED: 44 (96%)
- INFERRED: 2 (4%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*