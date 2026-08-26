# User Manager Auto-Create Logic

> 29 nodes · cohesion 0.10

## Key Concepts

- **BaseUserManager** (22 connections) — `gen_epix/fastapp/user_manager.py`
- **User** (9 connections)
- **Any** (7 connections)
- **.auto_create_new_user()** (4 connections) — `gen_epix/fastapp/user_manager.py`
- **.construct_user_instance_from_claims()** (4 connections) — `gen_epix/fastapp/user_manager.py`
- **.create_new_user_from_token()** (4 connections) — `gen_epix/fastapp/user_manager.py`
- **.create_root_user_from_claims()** (4 connections) — `gen_epix/fastapp/user_manager.py`
- **.retrieve_user_by_id()** (4 connections) — `gen_epix/fastapp/user_manager.py`
- **.retrieve_user_permissions()** (4 connections) — `gen_epix/fastapp/user_manager.py`
- **.get_user_key_from_claims()** (3 connections) — `gen_epix/fastapp/user_manager.py`
- **.get_user_name_from_claims()** (3 connections) — `gen_epix/fastapp/user_manager.py`
- **.is_root_user()** (3 connections) — `gen_epix/fastapp/user_manager.py`
- **.is_root_user_claims()** (3 connections) — `gen_epix/fastapp/user_manager.py`
- **.retrieve_user_by_key()** (3 connections) — `gen_epix/fastapp/user_manager.py`
- **.update_user_name()** (3 connections) — `gen_epix/fastapp/user_manager.py`
- **Hashable** (1 connections)
- **Class that defines the interface for a user manager. This class should be…** (1 connections) — `gen_epix/fastapp/user_manager.py`
- **Get the user key, which uniquely identifies the user across systems, from the…** (1 connections) — `gen_epix/fastapp/user_manager.py`
- **Construct user instance from identity claims.** (1 connections) — `gen_epix/fastapp/user_manager.py`
- **Create root user from identity claims.** (1 connections) — `gen_epix/fastapp/user_manager.py`
- **Check if claims belong to root user.** (1 connections) — `gen_epix/fastapp/user_manager.py`
- **Check if user is root user.** (1 connections) — `gen_epix/fastapp/user_manager.py`
- **Automatically create new user from claims.** (1 connections) — `gen_epix/fastapp/user_manager.py`
- **Create new user from token.** (1 connections) — `gen_epix/fastapp/user_manager.py`
- **Retrieve an existing user by their key.** (1 connections) — `gen_epix/fastapp/user_manager.py`
- *... and 4 more nodes in this community*

## Relationships

- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (4 shared connections)
- [RBAC/ABAC Policy Implementations](RBAC-ABAC_Policy_Implementations.md) (1 shared connections)
- [Organization Service](Organization_Service.md) (1 shared connections)
- [Identity Providers Command](Identity_Providers_Command.md) (1 shared connections)
- [Org Results Policy Tests](Org_Results_Policy_Tests.md) (1 shared connections)
- [Casedb Case CRUD Commands](Casedb_Case_CRUD_Commands.md) (1 shared connections)
- [FastApp Domain Registry Core](FastApp_Domain_Registry_Core.md) (1 shared connections)

## Source Files

- `gen_epix/fastapp/user_manager.py`

## Audit Trail

- EXTRACTED: 52 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*