# Model

> God node · 153 connections · `gen_epix/fastapp/model.py`

**Community:** [casedb/domain/model/__init__.py](casedb-domain-model-__init__.py.md)

## Connections by Relation

### calls
- .test_non_model_noid_objects_in_list_are_skipped() `EXTRACTED`

### contains
- gen_epix/fastapp/model.py `EXTRACTED`

### imports
- gen_epix/fastapp/__init__.py `EXTRACTED`
- fastapp/app.py `EXTRACTED`
- test_fastapp_dict_repository.py `EXTRACTED`
- test_fastapp_domain.py `EXTRACTED`
- test_fastapp_remote_app.py `EXTRACTED`
- gen_epix/fastapp/service.py `EXTRACTED`
- [test_fastapp_rbac_service.py](test_fastapp_rbac_service.py.md) `EXTRACTED`
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
- test_fastapp_dict_model_modifier.py `EXTRACTED`
- modifier.py `EXTRACTED`

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
- [Domain](Domain.md) `INFERRED`
- [BaseService](BaseService.md) `INFERRED`
- [BaseRepository](BaseRepository.md) `INFERRED`
- SeqProfile `INFERRED`
- Protocol `INFERRED`
- [SAMapper](SAMapper.md) `INFERRED`
- Seq `INFERRED`
- OidcServerCfg `INFERRED`
- [BaseSAMapper](BaseSAMapper.md) `INFERRED`
- Claims `INFERRED`
- [TestRegistrationAndLookups](TestRegistrationAndLookups.md) `INFERRED`
- IdentityProvider `INFERRED`
- [ReadSet](ReadSet.md) `INFERRED`
- RefDataAccess `INFERRED`
- [_DummyMapper](_DummyMapper.md) `INFERRED`
- [RBACTestClient](RBACTestClient.md) `INFERRED`
- [BaseSeq](BaseSeq.md) `INFERRED`

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*