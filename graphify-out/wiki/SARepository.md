# SARepository

> God node · 104 connections · `gen_epix/fastapp/repositories/sa/repository.py`

**Community:** [FastApp SA Repository Core](FastApp_SA_Repository_Core.md)

## Connections by Relation

### calls
- repo() `EXTRACTED`
- test_register_mappers_with_entity() `EXTRACTED`

### contains
- sa/repository.py `EXTRACTED`

### imports
- gen_epix/fastapp/__init__.py `EXTRACTED`
- commondb/domain/util.py `EXTRACTED`
- commondb/env.py `EXTRACTED`
- test_fastapp_sa_repository.py `EXTRACTED`
- service_test_client.py `EXTRACTED`
- test_fastapp_repository.py `EXTRACTED`
- test_fastapp_repository_performance.py `EXTRACTED`
- etl.py `EXTRACTED`
- commondb/repositories/organization_sa.py `EXTRACTED`
- base_env.py `EXTRACTED`
- sa/__init__.py `EXTRACTED`
- omop_sa.py `EXTRACTED`
- seq_sa.py `EXTRACTED`
- case_sa.py `EXTRACTED`
- fastapp/repositories/__init__.py `EXTRACTED`
- system_sa.py `EXTRACTED`
- file_sa.py `EXTRACTED`
- casedb/repositories/abac_sa.py `EXTRACTED`
- geo_sa.py `EXTRACTED`
- ontology_sa.py `EXTRACTED`

### inherits
- BaseRepository `EXTRACTED`
- SeqSARepository `EXTRACTED`
- OrganizationSARepository `EXTRACTED`
- OmopSARepository `EXTRACTED`
- SystemSARepository `EXTRACTED`
- CaseSARepository `EXTRACTED`
- AbacSARepository `EXTRACTED`
- GeoSARepository `EXTRACTED`
- OntologySARepository `EXTRACTED`
- AbacSARepository `EXTRACTED`
- AbacSARepository `EXTRACTED`
- AbacSARepository `EXTRACTED`
- FileSARepository `EXTRACTED`

### method
- .crud() `EXTRACTED`
- ._execute_sa() `EXTRACTED`
- .get_mapper() `EXTRACTED`
- .uow() `EXTRACTED`
- .read_some() `EXTRACTED`
- .exists_some() `EXTRACTED`
- .read_fields() `EXTRACTED`
- .read_all() `EXTRACTED`
- .update_some() `EXTRACTED`
- .upsert_some() `EXTRACTED`
- .delete_some() `EXTRACTED`
- .delete_all() `EXTRACTED`
- ._in_session_read_some() `EXTRACTED`
- .create_sa_repository() `EXTRACTED`
- .register_mappers() `EXTRACTED`
- .create_some() `EXTRACTED`
- .create_unique_values_temp_table() `EXTRACTED`
- ._select_with_id_join() `EXTRACTED`
- .__init__() `EXTRACTED`
- .get_session() `EXTRACTED`

### rationale_for
- SQLAlchemy-backed repository `EXTRACTED`

### references
- create_demo_data_from_repository() `EXTRACTED`
- test_crud_dispatch() `EXTRACTED`
- test_read_fields() `EXTRACTED`
- test_split_filter_and_get_where_clause() `EXTRACTED`
- test_create_read_update_upsert_delete_and_exists() `EXTRACTED`
- test_print_db_content() `EXTRACTED`
- test_verify_valid_ids() `EXTRACTED`
- test_create_some_and_upsert_some_validation() `EXTRACTED`
- test_crud_input_validation_errors() `EXTRACTED`
- test_register_get_mapper_and_duplicate_errors() `EXTRACTED`
- test_to_sql_and_from_sql() `EXTRACTED`
- test_read_some_raises_invalid_ids() `EXTRACTED`
- test_repository_properties_and_session() `EXTRACTED`
- test_uow_nested_and_invalid_nested_kwargs() `EXTRACTED`

### uses
- [Entity](Entity.md) `INFERRED`
- [Model](Model.md) `INFERRED`
- SAMapper `INFERRED`
- BaseSAMapper `INFERRED`
- BaseSAMapperFactory `INFERRED`
- EngineFactory `INFERRED`

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*