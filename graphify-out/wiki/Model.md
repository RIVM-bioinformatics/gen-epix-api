# Model

> God node · 159 connections · `gen_epix/fastapp/model.py`

**Community:** [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md)

## Connections by Relation

### calls
- .test_non_model_noid_objects_in_list_are_skipped() `EXTRACTED`

### contains
- gen_epix/fastapp/model.py `EXTRACTED`

### imports
- gen_epix/fastapp/__init__.py `EXTRACTED`
- fastapp/app.py `EXTRACTED`
- test_fastapp_dict_repository.py `EXTRACTED`
- sa/repository.py `EXTRACTED`
- test_fastapp_sa_repository.py `EXTRACTED`
- test_fastapp_domain.py `EXTRACTED`
- test_fastapp_remote_app.py `EXTRACTED`
- gen_epix/fastapp/service.py `EXTRACTED`
- test_fastapp_rbac_service.py `EXTRACTED`
- dict/repository.py `EXTRACTED`
- domain.py `EXTRACTED`
- auth/model.py `EXTRACTED`
- test/fastapp/model.py `EXTRACTED`
- test_fastapp_base_repository.py `EXTRACTED`
- test_fastapp_sa_repository_mapper.py `EXTRACTED`
- fastapp/repository.py `EXTRACTED`
- test_model_process_metadata_policy.py `EXTRACTED`
- mapper.py `EXTRACTED`
- sa_mapper.py `EXTRACTED`
- dict_modifier.py `EXTRACTED`

### inherits
- PydanticBaseModel `EXTRACTED`

### method
- .get_id() `EXTRACTED`
- .model_entity() `EXTRACTED`
- .model_name() `EXTRACTED`

### rationale_for
- Base class for all models in an application. Models are used to represent the… `EXTRACTED`

### references
- .get_objs() `EXTRACTED`

### uses
- [Entity](Entity.md) `INFERRED`
- [App](App.md) `INFERRED`
- [DictRepository](DictRepository.md) `INFERRED`
- [SARepository](SARepository.md) `INFERRED`
- Domain `INFERRED`
- BaseService `INFERRED`
- BaseRepository `INFERRED`
- SeqProfile `INFERRED`
- Protocol `INFERRED`
- SAMapper `INFERRED`
- BaseSAMapper `INFERRED`
- Seq `INFERRED`
- OidcServerCfg `INFERRED`
- Claims `INFERRED`
- TestRegistrationAndLookups `INFERRED`
- IdentityProvider `INFERRED`
- ReadSet `INFERRED`
- RefDataAccess `INFERRED`
- _DummyMapper `INFERRED`
- RBACTestClient `INFERRED`

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*