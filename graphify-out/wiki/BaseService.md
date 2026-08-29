# BaseService

> 50 nodes

## Key Concepts

- **BaseService** (70 connections) — `gen_epix/fastapp/service.py`
- **Link** (22 connections) — `gen_epix/fastapp/domain/link.py`
- **.update_association()** (11 connections) — `gen_epix/fastapp/service.py`
- **.crud()** (10 connections) — `gen_epix/fastapp/service.py`
- **.__init__()** (9 connections) — `gen_epix/fastapp/service.py`
- **._verify_same_service_links()** (8 connections) — `gen_epix/fastapp/service.py`
- **Any** (8 connections)
- **CrudCommand** (8 connections)
- **.crud_repository()** (7 connections) — `gen_epix/fastapp/service.py`
- **._verify_other_service_links()** (7 connections) — `gen_epix/fastapp/service.py`
- **.uow()** (6 connections) — `gen_epix/fastapp/repository.py`
- **.create_log_message()** (6 connections) — `gen_epix/fastapp/service.py`
- **._get_model_links()** (6 connections) — `gen_epix/fastapp/service.py`
- **.set_object_id()** (6 connections) — `gen_epix/fastapp/service.py`
- **BaseModel** (6 connections)
- **.register_crud_listener()** (5 connections) — `gen_epix/fastapp/service.py`
- **.unregister_crud_listener()** (4 connections) — `gen_epix/fastapp/service.py`
- **datetime** (4 connections)
- **Hashable** (4 connections)
- **Model** (4 connections)
- **UpdateAssociationCommand** (4 connections)
- **.generate_id()** (3 connections) — `gen_epix/fastapp/service.py`
- **.logger()** (3 connections) — `gen_epix/fastapp/service.py`
- **.register_default_crud_handlers()** (3 connections) — `gen_epix/fastapp/service.py`
- **.register_handlers()** (3 connections) — `gen_epix/fastapp/service.py`
- *... and 25 more nodes in this community*

## Relationships

- [CrudOperation](CrudOperation.md) (18 shared connections)
- [BaseUnitOfWork](BaseUnitOfWork.md) (8 shared connections)
- [casedb/domain/enum.py](casedb-domain-enum.py.md) (4 shared connections)
- [entity.py](entity.py.md) (3 shared connections)
- [Permission](Permission.md) (3 shared connections)
- [test_commondb_upload.py](test_commondb_upload.py.md) (3 shared connections)
- [ServiceTestClient](ServiceTestClient.md) (3 shared connections)
- [Domain](Domain.md) (2 shared connections)
- [DomainException](DomainException.md) (2 shared connections)
- [services/user_manager.py](services-user_manager.py.md) (2 shared connections)
- [auth/__init__.py](auth-__init__.py.md) (2 shared connections)
- [FileCompression](FileCompression.md) (2 shared connections)

## Source Files

- `gen_epix/casedb/services/case/upload.py`
- `gen_epix/fastapp/domain/link.py`
- `gen_epix/fastapp/repository.py`
- `gen_epix/fastapp/service.py`
- `gen_epix/omopdb/services/omop/upload.py`
- `test/commondb/unit/upload/model.py`

## Audit Trail

- EXTRACTED: 160 (94%)
- INFERRED: 11 (6%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*