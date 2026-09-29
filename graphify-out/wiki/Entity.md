# Entity

> God node · 192 connections · `gen_epix/fastapp/domain/entity.py`

**Community:** [Domain & Entity Registry](Domain_&_Entity_Registry.md)

## Connections by Relation

### calls
- test_create_sa_repository_attached_sqlite_is_in_memory() `EXTRACTED`
- _make_entity() `EXTRACTED`
- .clone() `EXTRACTED`
- .setup_method() `EXTRACTED`
- .setup_method() `EXTRACTED`
- .test_errors_for_unknown_items() `EXTRACTED`
- .test_get_dag_sorted_service_types_handles_non_contiguous_service_blocks() `EXTRACTED`
- .test_get_dag_sorted_service_types_raises_on_real_service_cycle() `EXTRACTED`
- .test_invalid_entity_id_field_type_raises() `EXTRACTED`
- .test_cycle_falls_back_to_declaration_order_with_warning() `INFERRED`
- .test_register_command_error_paths() `EXTRACTED`
- .test_register_service_type_and_entity_cycle_handling() `EXTRACTED`
- .test_unconstrained_children_keep_relative_order_within_a_layer() `INFERRED`

### contains
- entity.py `EXTRACTED`

### imports
- gen_epix/fastapp/model.py `EXTRACTED`
- test_fastapp_dict_repository.py `EXTRACTED`
- commondb/domain/util.py `EXTRACTED`
- sa/repository.py `EXTRACTED`
- test_fastapp_sa_repository.py `EXTRACTED`
- test_fastapp_api.py `EXTRACTED`
- case/crud_common.py `EXTRACTED`
- model/upload.py `EXTRACTED`
- test_fastapp_domain.py `EXTRACTED`
- omop/non_persistable.py `EXTRACTED`
- test_crud_endpoint_generator.py `EXTRACTED`
- model/case/upload.py `EXTRACTED`
- dict/repository.py `EXTRACTED`
- test_fastapp_client.py `EXTRACTED`
- crud_endpoint_generator.py `EXTRACTED`
- model/seq/base.py `EXTRACTED`
- auth/model.py `EXTRACTED`
- fastapp/domain/__init__.py `EXTRACTED`
- common.py `EXTRACTED`
- domain.py `EXTRACTED`
- *…and 9 more `imports` connection(s) not listed (lowest-degree first to go)*

### inherits
- BaseModel `EXTRACTED`

### method
- .has_model() `EXTRACTED`
- .set_model_class() `EXTRACTED`
- ._verify_and_parse_model_links() `EXTRACTED`
- .crud_command_class() `EXTRACTED`
- .get_field_names() `EXTRACTED`
- ._validate_keys() `EXTRACTED`
- ._validate_links() `EXTRACTED`
- .set_crud_command_class() `EXTRACTED`
- ._verify_link_field_name() `EXTRACTED`
- ._verify_relationship_fields() `EXTRACTED`
- .topological_sort() `EXTRACTED`
- ._validate_names() `EXTRACTED`
- ._validate_model() `EXTRACTED`
- .get_obj_id() `EXTRACTED`
- .set_db_model_class() `EXTRACTED`
- .set_create_api_model_class() `EXTRACTED`
- .set_read_api_model_class() `EXTRACTED`
- ._create_keys_generator() `EXTRACTED`
- ._get_model_field_names() `EXTRACTED`
- .name() `EXTRACTED`
- *…and 20 more `method` connection(s) not listed (lowest-degree first to go)*

### rationale_for
- Represents a domain model's names, persistence, keys, and links. Model… `EXTRACTED`

### references
- .create_sa_repository() `EXTRACTED`
- .get_crud_endpoint_set_for_entity() `EXTRACTED`
- .__init__() `EXTRACTED`
- .register_entity() `EXTRACTED`
- .__init__() `EXTRACTED`
- .get_dag_sorted_entities() `EXTRACTED`
- .create_repository_from_pkl() `EXTRACTED`
- .create_repository_from_json() `EXTRACTED`
- .register_mappers() `EXTRACTED`
- ._link_new_command() `EXTRACTED`
- .create_repository() `EXTRACTED`
- ._init_mappers() `EXTRACTED`
- .get_service_type_for_entity() `EXTRACTED`
- ._verify_entity_exists() `EXTRACTED`
- .get_entity_for_model() `EXTRACTED`
- .__init__() `EXTRACTED`
- ._create_empty_db_for_entities() `EXTRACTED`
- ._process_repository_params() `EXTRACTED`
- .__init__() `EXTRACTED`
- .__init__() `EXTRACTED`
- *…and 17 more `references` connection(s) not listed (lowest-degree first to go)*

### uses
- DictRepository `INFERRED`
- SARepository `INFERRED`
- Domain `INFERRED`
- UploadResult `INFERRED`
- CrudEndpointGenerator `INFERRED`
- Model `INFERRED`
- BaseBatchUploadResult `INFERRED`
- FullPerson `INFERRED`
- OnException `INFERRED`
- Claims `INFERRED`
- OidcServerCfg `INFERRED`
- TestRegistrationAndLookups `INFERRED`
- ParentForUpload `INFERRED`
- IdentityProvider `INFERRED`
- BaseBatchForUpload `INFERRED`
- Link `INFERRED`
- FieldType `INFERRED`
- BaseAppComposer `INFERRED`
- make_parent_entity() `INFERRED`
- BaseSeq `INFERRED`
- *…and 50 more `uses` connection(s) not listed (lowest-degree first to go)*

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*