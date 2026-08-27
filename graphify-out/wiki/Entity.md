# Entity

> God node · 174 connections · `gen_epix/fastapp/domain/entity.py`

**Community:** [FastApp Entity & Model Core](FastApp_Entity_&_Model_Core.md)

## Connections by Relation

### calls
- .create_entity() `EXTRACTED`
- _make_entity() `EXTRACTED`
- .clone() `EXTRACTED`
- .setup_method() `EXTRACTED`
- .setup_method() `EXTRACTED`
- .test_errors_for_unknown_items() `EXTRACTED`
- .test_get_dag_sorted_service_types_handles_non_contiguous_service_blocks() `EXTRACTED`
- .test_get_dag_sorted_service_types_raises_on_real_service_cycle() `EXTRACTED`
- .test_invalid_entity_id_field_type_raises() `EXTRACTED`
- .test_register_command_error_paths() `EXTRACTED`
- .test_register_service_type_and_entity_cycle_handling() `EXTRACTED`

### contains
- entity.py `EXTRACTED`

### imports
- gen_epix/fastapp/model.py `EXTRACTED`
- test_fastapp_dict_repository.py `EXTRACTED`
- sa/repository.py `EXTRACTED`
- crud_endpoint_generator.py `EXTRACTED`
- case/crud_common.py `EXTRACTED`
- test_fastapp_sa_repository.py `EXTRACTED`
- model/upload.py `EXTRACTED`
- test_fastapp_domain.py `EXTRACTED`
- omop/non_persistable.py `EXTRACTED`
- test_fastapp_remote_app.py `EXTRACTED`
- dict/repository.py `EXTRACTED`
- model/case/upload.py `EXTRACTED`
- domain.py `EXTRACTED`
- auth/model.py `EXTRACTED`
- seq/non_persistable.py `EXTRACTED`
- fastapp/domain/__init__.py `EXTRACTED`
- common.py `EXTRACTED`
- test_fastapp_base_repository.py `EXTRACTED`
- model/seq/base.py `EXTRACTED`
- test_fastapp_sa_repository_mapper.py `EXTRACTED`

### inherits
- BaseModel `EXTRACTED`

### method
- .has_model() `EXTRACTED`
- .crud_command_class() `EXTRACTED`
- .set_model_class() `EXTRACTED`
- ._verify_and_parse_model_links() `EXTRACTED`
- .get_field_names() `EXTRACTED`
- .get_obj_id() `EXTRACTED`
- .set_crud_command_class() `EXTRACTED`
- .topological_sort() `EXTRACTED`
- ._validate_links() `EXTRACTED`
- .model_class() `EXTRACTED`
- .set_db_model_class() `EXTRACTED`
- .set_create_api_model_class() `EXTRACTED`
- .set_read_api_model_class() `EXTRACTED`
- ._verify_link_field_name() `EXTRACTED`
- ._verify_relationship_fields() `EXTRACTED`
- ._validate_keys() `EXTRACTED`
- .get_link_id() `EXTRACTED`
- ._get_model_field_names() `EXTRACTED`
- .name() `EXTRACTED`
- .db_model_class() `EXTRACTED`

### references
- .get_crud_endpoint_set_for_entity() `EXTRACTED`
- .register_entity() `EXTRACTED`
- .__init__() `EXTRACTED`
- .__init__() `EXTRACTED`
- .get_dag_sorted_entities() `EXTRACTED`
- .create_repository_from_json() `EXTRACTED`
- .create_repository_from_pkl() `EXTRACTED`
- .create_sa_repository() `EXTRACTED`
- .register_mappers() `EXTRACTED`
- ._init_mappers() `EXTRACTED`
- ._link_new_command() `EXTRACTED`
- .create_repository() `EXTRACTED`
- ._create_empty_db_for_entities() `EXTRACTED`
- ._process_repository_params() `EXTRACTED`
- .get_service_type_for_entity() `EXTRACTED`
- ._update_entity_dag() `EXTRACTED`
- ._verify_entity_exists() `EXTRACTED`
- ._get_links() `EXTRACTED`
- .get_entity_for_model() `EXTRACTED`
- .__init__() `EXTRACTED`

### uses
- [Model](Model.md) `INFERRED`
- [DictRepository](DictRepository.md) `INFERRED`
- [SARepository](SARepository.md) `INFERRED`
- Domain `INFERRED`
- UploadResult `INFERRED`
- CrudEndpointGenerator `INFERRED`
- FullPerson `INFERRED`
- BaseBatchUploadResult `INFERRED`
- OidcServerCfg `INFERRED`
- Claims `INFERRED`
- TestRegistrationAndLookups `INFERRED`
- IdentityProvider `INFERRED`
- FullSample `INFERRED`
- BaseBatchForUpload `INFERRED`
- Link `INFERRED`
- create_dict_repository() `INFERRED`
- BaseSeq `INFERRED`
- BaseAppComposer `INFERRED`
- ParentForUpload `INFERRED`
- IDPUser `INFERRED`

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*