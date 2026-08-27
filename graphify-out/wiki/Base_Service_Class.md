# Base Service Class

> 42 nodes · cohesion 0.10

## Key Concepts

- **BaseService** (70 connections) — `gen_epix/fastapp/service.py`
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
- **.repository()** (3 connections) — `gen_epix/fastapp/service.py`
- **.app()** (2 connections) — `gen_epix/fastapp/service.py`
- *... and 17 more nodes in this community*

## Relationships

- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (15 shared connections)
- [Abac Service Access Control](Abac_Service_Access_Control.md) (5 shared connections)
- [Domain Entity Registration](Domain_Entity_Registration.md) (5 shared connections)
- [Casedb Case CRUD Commands](Casedb_Case_CRUD_Commands.md) (4 shared connections)
- [Seqdb Upload Batch Processing](Seqdb_Upload_Batch_Processing.md) (4 shared connections)
- [Fastapp CRUD Command Tests](Fastapp_CRUD_Command_Tests.md) (4 shared connections)
- [Organization Service](Organization_Service.md) (3 shared connections)
- [Commondb Upload Test Suite](Commondb_Upload_Test_Suite.md) (3 shared connections)
- [Repository Association Handling](Repository_Association_Handling.md) (2 shared connections)
- [Identity Providers Command](Identity_Providers_Command.md) (2 shared connections)
- [File Creation Command](File_Creation_Command.md) (2 shared connections)
- [App Composer Base](App_Composer_Base.md) (1 shared connections)

## Source Files

- `gen_epix/fastapp/repository.py`
- `gen_epix/fastapp/service.py`
- `gen_epix/omopdb/services/omop/upload.py`
- `test/commondb/unit/upload/model.py`

## Audit Trail

- EXTRACTED: 137 (94%)
- INFERRED: 9 (6%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*