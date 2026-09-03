# DictRepository

> God node · 124 connections · `gen_epix/fastapp/repositories/dict/repository.py`

**Community:** [DictRepository](DictRepository.md)

## Connections by Relation

### calls
- make_repo() `EXTRACTED`
- test_init_composite_id_field_raises() `EXTRACTED`
- .create_repository() `EXTRACTED`
- test_init_invalid_extra_data_raises() `EXTRACTED`
- test_init_invalid_missing_data_raises() `EXTRACTED`
- test_init_missing_data_raise() `EXTRACTED`

### contains
- dict/repository.py `EXTRACTED`

### imports
- gen_epix/fastapp/__init__.py `EXTRACTED`
- commondb/domain/util.py `EXTRACTED`
- test_fastapp_dict_repository.py `EXTRACTED`
- commondb/env.py `EXTRACTED`
- [test_fastapp_rbac_service.py](test_fastapp_rbac_service.py.md) `EXTRACTED`
- service_test_client.py `EXTRACTED`
- test_fastapp_repository.py `EXTRACTED`
- test_fastapp_repository_performance.py `EXTRACTED`
- etl.py `EXTRACTED`
- seq_dict.py `EXTRACTED`
- base_env.py `EXTRACTED`
- omop_dict.py `EXTRACTED`
- case_dict.py `EXTRACTED`
- commondb/repositories/organization_dict.py `EXTRACTED`
- fastapp/repositories/__init__.py `EXTRACTED`
- system_dict.py `EXTRACTED`
- file_dict.py `EXTRACTED`
- dict/__init__.py `EXTRACTED`
- casedb/repositories/abac_dict.py `EXTRACTED`
- geo_dict.py `EXTRACTED`

### inherits
- [BaseRepository](BaseRepository.md) `EXTRACTED`
- [SeqDictRepository](SeqDictRepository.md) `EXTRACTED`
- OrganizationDictRepository `EXTRACTED`
- OmopDictRepository `EXTRACTED`
- SystemDictRepository `EXTRACTED`
- CaseDictRepository `EXTRACTED`
- AbacDictRepository `EXTRACTED`
- GeoDictRepository `EXTRACTED`
- OntologyDictRepository `EXTRACTED`
- AbacDictRepository `EXTRACTED`
- AbacDictRepository `EXTRACTED`
- AbacDictRepository `EXTRACTED`
- FileDictRepository `EXTRACTED`

### method
- .crud() `EXTRACTED`
- .create_repository() `EXTRACTED`
- .__init__() `EXTRACTED`
- .read_some() `EXTRACTED`
- .upsert_some() `EXTRACTED`
- .delete_some() `EXTRACTED`
- .verify_valid_ids() `EXTRACTED`
- .create_repository_from_json() `EXTRACTED`
- ._validate_upsert_objects() `EXTRACTED`
- .create_repository_from_pkl() `EXTRACTED`
- ._verify_duplicate_ids() `EXTRACTED`
- .read_all() `EXTRACTED`
- .upsert_model_objects() `EXTRACTED`
- .delete_all() `EXTRACTED`
- .read_fields() `EXTRACTED`
- .read_one() `EXTRACTED`
- .upsert_one() `EXTRACTED`
- ._apply_link_updates() `EXTRACTED`
- .delete_one() `EXTRACTED`
- ._verify_duplicate_keys() `EXTRACTED`

### rationale_for
- Repository that stores models in an in-memory dict, keyed by model class. `EXTRACTED`

### references
- create_demo_data_from_repository() `EXTRACTED`

### uses
- [Entity](Entity.md) `INFERRED`
- [Model](Model.md) `INFERRED`
- AppComposer `INFERRED`
- [ServiceTestClient](ServiceTestClient.md) `INFERRED`
- [BaseAppComposer](BaseAppComposer.md) `INFERRED`
- BaseDictModelModifier `INFERRED`
- DictUnitOfWork `INFERRED`
- pc_repo() `INFERRED`
- parent_repo() `INFERRED`
- test_create_repository_no_file_initializes_empty_db() `INFERRED`
- TestRepository `INFERRED`
- test_create_repository_detect_pkl_calls_from_pkl() `INFERRED`
- test_create_repository_detect_zip_calls_from_json() `INFERRED`
- test_create_repository_from_json_happy() `INFERRED`
- test_create_repository_from_pkl_gz() `INFERRED`
- test_create_repository_from_pkl_plain() `INFERRED`
- test_upsert_errors() `INFERRED`
- test_upsert_links() `INFERRED`
- test_crud_dispatch_all_ops() `INFERRED`
- test_upsert_create_and_update() `INFERRED`

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*