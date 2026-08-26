# Organization Service

> 57 nodes · cohesion 0.05

## Key Concepts

- **BaseOrganizationService** (23 connections) — `gen_epix/commondb/domain/service/organization.py`
- **AbacService** (17 connections) — `gen_epix/commondb/services/abac.py`
- **BaseRbacService** (16 connections) — `gen_epix/commondb/domain/service/rbac.py`
- **commondb/domain/service/__init__.py** (15 connections) — `gen_epix/commondb/domain/service/__init__.py`
- **BaseSystemService** (15 connections) — `gen_epix/commondb/domain/service/system.py`
- **service/organization.py** (14 connections) — `gen_epix/commondb/domain/service/organization.py`
- **seqdb/domain/service/__init__.py** (13 connections) — `gen_epix/seqdb/domain/service/__init__.py`
- **commondb/domain/service/abac.py** (12 connections) — `gen_epix/commondb/domain/service/abac.py`
- **service/rbac.py** (11 connections) — `gen_epix/commondb/domain/service/rbac.py`
- **omopdb/domain/service/__init__.py** (11 connections) — `gen_epix/omopdb/domain/service/__init__.py`
- **service/system.py** (10 connections) — `gen_epix/commondb/domain/service/system.py`
- **service/user_manager.py** (10 connections) — `gen_epix/commondb/domain/service/user_manager.py`
- **BaseUserManager** (10 connections) — `gen_epix/commondb/domain/service/user_manager.py`
- **BaseAbacService** (8 connections) — `gen_epix/omopdb/domain/service/abac.py`
- **.__init__()** (7 connections) — `gen_epix/commondb/domain/service/user_manager.py`
- **omopdb/domain/service/abac.py** (6 connections) — `gen_epix/omopdb/domain/service/abac.py`
- **ServiceType** (5 connections) — `gen_epix/commondb/domain/enum.py`
- **.__init__()** (5 connections) — `gen_epix/commondb/services/abac.py`
- **.anonymize_user()** (4 connections) — `gen_epix/commondb/domain/service/organization.py`
- **.register_invited_user()** (4 connections) — `gen_epix/commondb/domain/service/organization.py`
- **.update_user()** (4 connections) — `gen_epix/commondb/domain/service/organization.py`
- **User** (4 connections)
- **.retrieve_own_permissions()** (4 connections) — `gen_epix/commondb/domain/service/rbac.py`
- **.__init__()** (3 connections) — `gen_epix/commondb/domain/policy/system.py`
- **.retrieve_user_by_key()** (3 connections) — `gen_epix/commondb/domain/service/organization.py`
- *... and 32 more nodes in this community*

## Relationships

- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (20 shared connections)
- [Casedb Domain CRUD Commands](Casedb_Domain_CRUD_Commands.md) (15 shared connections)
- [Commondb Enums & Demo Data](Commondb_Enums_&_Demo_Data.md) (8 shared connections)
- [ABAC Base Policies](ABAC_Base_Policies.md) (8 shared connections)
- [RBAC/ABAC Policy Implementations](RBAC-ABAC_Policy_Implementations.md) (8 shared connections)
- [Abac Service Access Control](Abac_Service_Access_Control.md) (7 shared connections)
- [Commondb Organization Domain Models](Commondb_Organization_Domain_Models.md) (6 shared connections)
- [Identity Providers Command](Identity_Providers_Command.md) (6 shared connections)
- [App Composition & Service Wiring](App_Composition_&_Service_Wiring.md) (6 shared connections)
- [Casedb Repository Implementations](Casedb_Repository_Implementations.md) (5 shared connections)
- [Base Service Class](Base_Service_Class.md) (3 shared connections)
- [Core App Base Class](Core_App_Base_Class.md) (3 shared connections)

## Source Files

- `gen_epix/commondb/domain/enum.py`
- `gen_epix/commondb/domain/policy/system.py`
- `gen_epix/commondb/domain/service/__init__.py`
- `gen_epix/commondb/domain/service/abac.py`
- `gen_epix/commondb/domain/service/organization.py`
- `gen_epix/commondb/domain/service/rbac.py`
- `gen_epix/commondb/domain/service/system.py`
- `gen_epix/commondb/domain/service/user_manager.py`
- `gen_epix/commondb/services/abac.py`
- `gen_epix/omopdb/domain/service/__init__.py`
- `gen_epix/omopdb/domain/service/abac.py`
- `gen_epix/seqdb/domain/service/__init__.py`

## Audit Trail

- EXTRACTED: 183 (94%)
- INFERRED: 12 (6%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*