# RBAC Service Test Setup

> 33 nodes · cohesion 0.10

## Key Concepts

- **RBACTestClient** (19 connections) — `test/fastapp/unit/services/rbac/test_fastapp_rbac_service.py`
- **User** (11 connections) — `test/fastapp/unit/services/rbac/test_fastapp_rbac_service.py`
- **.crud_command_class()** (10 connections) — `gen_epix/fastapp/domain/entity.py`
- **TestRBAC** (9 connections) — `test/fastapp/unit/services/rbac/test_fastapp_rbac_service.py`
- **.__init__()** (7 connections) — `test/fastapp/unit/services/rbac/test_fastapp_rbac_service.py`
- **RbacService** (5 connections) — `test/fastapp/unit/services/rbac/test_fastapp_rbac_service.py`
- **.create_one()** (5 connections) — `test/fastapp/unit/services/rbac/test_fastapp_rbac_service.py`
- **get_test_client()** (4 connections) — `test/fastapp/unit/services/rbac/test_fastapp_rbac_service.py`
- **Model** (4 connections)
- **.delete_one()** (4 connections) — `test/fastapp/unit/services/rbac/test_fastapp_rbac_service.py`
- **.get_user()** (4 connections) — `test/fastapp/unit/services/rbac/test_fastapp_rbac_service.py`
- **.read_one()** (4 connections) — `test/fastapp/unit/services/rbac/test_fastapp_rbac_service.py`
- **.update_one()** (4 connections) — `test/fastapp/unit/services/rbac/test_fastapp_rbac_service.py`
- **.retrieve_user_roles()** (3 connections) — `test/fastapp/unit/services/rbac/test_fastapp_rbac_service.py`
- **Role** (3 connections) — `test/fastapp/unit/services/rbac/test_fastapp_rbac_service.py`
- **Enum** (2 connections)
- **.retrieve_user_is_root()** (2 connections) — `test/fastapp/unit/services/rbac/test_fastapp_rbac_service.py`
- **.test_create_one()** (2 connections) — `test/fastapp/unit/services/rbac/test_fastapp_rbac_service.py`
- **.test_create_role()** (2 connections) — `test/fastapp/unit/services/rbac/test_fastapp_rbac_service.py`
- **.test_delete_one()** (2 connections) — `test/fastapp/unit/services/rbac/test_fastapp_rbac_service.py`
- **.test_get_user_roles()** (2 connections) — `test/fastapp/unit/services/rbac/test_fastapp_rbac_service.py`
- **.test_read_one()** (2 connections) — `test/fastapp/unit/services/rbac/test_fastapp_rbac_service.py`
- **.test_update_one()** (2 connections) — `test/fastapp/unit/services/rbac/test_fastapp_rbac_service.py`
- **.test_update_role()** (2 connections) — `test/fastapp/unit/services/rbac/test_fastapp_rbac_service.py`
- **ServiceUser** (1 connections)
- *... and 8 more nodes in this community*

## Relationships

- [Fastapp CRUD Command Tests](Fastapp_CRUD_Command_Tests.md) (7 shared connections)
- [FastApp Entity & Model Core](FastApp_Entity_&_Model_Core.md) (4 shared connections)
- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (3 shared connections)
- [Seqdb Upload Batch Processing](Seqdb_Upload_Batch_Processing.md) (2 shared connections)
- [In-Memory Dict Repository](In-Memory_Dict_Repository.md) (1 shared connections)
- [Service Test Client Fixtures](Service_Test_Client_Fixtures.md) (1 shared connections)
- [Abac Service Access Control](Abac_Service_Access_Control.md) (1 shared connections)
- [Mock User Manager Tests](Mock_User_Manager_Tests.md) (1 shared connections)
- [Repository Association Handling](Repository_Association_Handling.md) (1 shared connections)

## Source Files

- `gen_epix/fastapp/domain/entity.py`
- `test/fastapp/unit/services/rbac/test_fastapp_rbac_service.py`

## Audit Trail

- EXTRACTED: 61 (85%)
- INFERRED: 11 (15%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*