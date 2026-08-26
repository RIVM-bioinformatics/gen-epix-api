# App Composition & User Registration

> 31 nodes · cohesion 0.09

## Key Concepts

- **.create_local_or_remote_app()** (12 connections) — `gen_epix/commondb/services/remote_app.py`
- **._create_local_app()** (10 connections) — `gen_epix/commondb/services/remote_app.py`
- **._create_remote_app()** (8 connections) — `gen_epix/commondb/services/remote_app.py`
- **TestCreateRemoteAppErrors** (7 connections) — `test/commondb/unit/remote_app/test_commondb_remote_app.py`
- **TestCreateLocalOrRemoteApp** (6 connections) — `test/commondb/unit/remote_app/test_commondb_remote_app.py`
- **User** (5 connections)
- **.register_invited_user()** (4 connections) — `gen_epix/commondb/services/remote_app.py`
- **.update_user()** (4 connections) — `gen_epix/commondb/services/remote_app.py`
- **.update_user_own_organization()** (4 connections) — `gen_epix/commondb/services/remote_app.py`
- **Any** (4 connections)
- **App** (3 connections)
- **Enum** (3 connections)
- **Logger** (3 connections)
- **.test_app_setup_type_case_insensitive()** (3 connections) — `test/commondb/unit/remote_app/test_commondb_remote_app.py`
- **.test_invalid_app_setup_type_rejected()** (3 connections) — `test/commondb/unit/remote_app/test_commondb_remote_app.py`
- **.test_remote_app_missing_class_name_raises_error()** (3 connections) — `test/commondb/unit/remote_app/test_commondb_remote_app.py`
- **.test_remote_app_missing_module_raises_error()** (3 connections) — `test/commondb/unit/remote_app/test_commondb_remote_app.py`
- **.test_remote_app_props_none_raises_error()** (3 connections) — `test/commondb/unit/remote_app/test_commondb_remote_app.py`
- **Register an invited user using their invitation token.** (1 connections) — `gen_epix/commondb/services/remote_app.py`
- **Update a user's active status, roles, or organization.** (1 connections) — `gen_epix/commondb/services/remote_app.py`
- **Update the authenticated user's own organization.** (1 connections) — `gen_epix/commondb/services/remote_app.py`
- **Create either a local or remote app instance based on setup type.** (1 connections) — `gen_epix/commondb/services/remote_app.py`
- **Instantiate a local app from configuration and a user definition.** (1 connections) — `gen_epix/commondb/services/remote_app.py`
- **Instantiate a remote app from a module path and class name.** (1 connections) — `gen_epix/commondb/services/remote_app.py`
- **Test create_local_or_remote_app class method.** (1 connections) — `test/commondb/unit/remote_app/test_commondb_remote_app.py`
- *... and 6 more nodes in this community*

## Relationships

- [Commondb Remote App Client](Commondb_Remote_App_Client.md) (6 shared connections)
- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (5 shared connections)
- [Remote App Auth Header Tests](Remote_App_Auth_Header_Tests.md) (4 shared connections)
- [Casedb Domain CRUD Commands](Casedb_Domain_CRUD_Commands.md) (3 shared connections)
- [Commondb Enums & Demo Data](Commondb_Enums_&_Demo_Data.md) (2 shared connections)
- [App Composition & Startup](App_Composition_&_Startup.md) (1 shared connections)

## Source Files

- `gen_epix/commondb/services/remote_app.py`
- `test/commondb/unit/remote_app/test_commondb_remote_app.py`

## Audit Trail

- EXTRACTED: 61 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*