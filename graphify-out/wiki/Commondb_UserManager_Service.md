# Commondb UserManager Service

> 22 nodes

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
- **.__init__()** (3 connections) — `gen_epix/commondb/services/user_manager.py`
- **.is_existing_user_by_key()** (3 connections) — `gen_epix/commondb/services/user_manager.py`
- **.retrieve_user_permissions()** (3 connections) — `gen_epix/commondb/services/user_manager.py`
- **UUID** (3 connections)
- **.get_user_key_from_claims()** (2 connections) — `gen_epix/commondb/services/user_manager.py`
- **.is_root_user()** (2 connections) — `gen_epix/commondb/services/user_manager.py`
- **.is_root_user_claims()** (2 connections) — `gen_epix/commondb/services/user_manager.py`
- **.retrieve_user_by_key()** (2 connections) — `gen_epix/commondb/services/user_manager.py`
- **.update_user_name()** (2 connections) — `gen_epix/commondb/services/user_manager.py`
- **BaseRbacService** (1 connections)
- **BaseUserManager** (1 connections)

## Relationships

- [OrganizationService](OrganizationService.md) (4 shared connections)
- [services/user_manager.py](services-user_manager.py.md) (4 shared connections)
- [test_user_manager_auto_create.py](test_user_manager_auto_create.py.md) (2 shared connections)
- [CrudOperation](CrudOperation.md) (2 shared connections)
- [make_cdb_user](make_cdb_user.md) (2 shared connections)
- [auth/__init__.py](auth-__init__.py.md) (2 shared connections)
- [InMemoryOrganizationRepository](InMemoryOrganizationRepository.md) (1 shared connections)
- [commondb/domain/model/__init__.py](commondb-domain-model-__init__.py.md) (1 shared connections)
- [_uuid_field_name](_uuid_field_name.md) (1 shared connections)
- [BaseUnitOfWork](BaseUnitOfWork.md) (1 shared connections)
- [Permission](Permission.md) (1 shared connections)

## Source Files

- `gen_epix/commondb/services/user_manager.py`
- `gen_epix/fastapp/services/auth/util.py`

## Audit Trail

- EXTRACTED: 64 (98%)
- INFERRED: 1 (2%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*