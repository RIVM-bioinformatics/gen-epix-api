# UserManager

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

- [Permission](Permission.md) (5 shared connections)
- [AuthTestClient](AuthTestClient.md) (2 shared connections)
- [test_fastapp_rbac_service.py](test_fastapp_rbac_service.py.md) (2 shared connections)
- [ServiceTestClient](ServiceTestClient.md) (1 shared connections)
- [RBACTestClient](RBACTestClient.md) (1 shared connections)
- [BaseUnitOfWork](BaseUnitOfWork.md) (1 shared connections)

## Source Files

- `test/fastapp/user_manager.py`

## Audit Trail

- EXTRACTED: 44 (96%)
- INFERRED: 2 (4%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*