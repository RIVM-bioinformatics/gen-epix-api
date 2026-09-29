# CrudOperation

> God node · 234 connections · `gen_epix/fastapp/enum.py`

**Community:** [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md)

## Connections by Relation

### contains
- gen_epix/fastapp/enum.py `EXTRACTED`

### imports
- gen_epix/fastapp/model.py `EXTRACTED`
- case/service.py `EXTRACTED`
- test_fastapp_dict_repository.py `EXTRACTED`
- gen_epix/fastapp/__init__.py `EXTRACTED`
- commondb/domain/util.py `EXTRACTED`
- sa/repository.py `EXTRACTED`
- test_casedb_upload.py `EXTRACTED`
- test_fastapp_sa_repository.py `EXTRACTED`
- test_seqdb_calculate_seq_distance.py `EXTRACTED`
- test_fastapp_api.py `EXTRACTED`
- calculate_seq_distance.py `EXTRACTED`
- casedb_test_client.py `EXTRACTED`
- case/crud_common.py `EXTRACTED`
- test_seqdb_distance_optimization_benchmark.py `EXTRACTED`
- test_fastapp_domain.py `EXTRACTED`
- test_commondb_auth.py `EXTRACTED`
- test_client.py `EXTRACTED`
- test_omopdb_upload.py `EXTRACTED`
- retrieve_case.py `EXTRACTED`
- seqdb_test_client.py `EXTRACTED`
- *…and 97 more `imports` connection(s) not listed (lowest-degree first to go)*

### inherits
- Enum `EXTRACTED`

### rationale_for
- Encapsulates identifying a supported create, read, update, delete, or existence… `EXTRACTED`

### references
- .create_crud_endpoint_set_for_domain() `EXTRACTED`
- .crud() `EXTRACTED`
- .crud() `EXTRACTED`
- .create_crud_cmd() `EXTRACTED`
- ._make_user_cmd() `EXTRACTED`
- .verify_crud_args() `EXTRACTED`
- .get_crud_endpoint_set_for_entity() `EXTRACTED`
- .crud() `EXTRACTED`
- .create_crud_command() `EXTRACTED`
- .crud() `EXTRACTED`
- .crud() `EXTRACTED`
- .get_crud_endpoint_types_for_operations() `EXTRACTED`
- .get_crud_operations_for_permissions() `EXTRACTED`
- .expectCrudCalled() `EXTRACTED`
- .__init__() `EXTRACTED`
- .crud() `EXTRACTED`
- .repository_crud() `EXTRACTED`
- .crud() `EXTRACTED`

### uses
- [TestClient](TestClient.md) `INFERRED`
- DictRepository `INFERRED`
- SARepository `INFERRED`
- Domain `INFERRED`
- SeqdbTestClient `INFERRED`
- BaseService `INFERRED`
- BaseRepository `INFERRED`
- CrudEndpointGenerator `INFERRED`
- Client `INFERRED`
- SeqdbClient `INFERRED`
- [CrudCommand](CrudCommand.md) `INFERRED`
- CaseBatchUploader `INFERRED`
- seq_service_calculate_seq_distances_for_new_profiles() `INFERRED`
- RBACTestClient `INFERRED`
- _calculate_and_store_distances() `INFERRED`
- TestRegistrationAndLookups `INFERRED`
- SeqDictRepository `INFERRED`
- ReadUserPolicy `INFERRED`
- _make_crud_side_effect() `INFERRED`
- _verify_batch_refdata_snp_profiles() `INFERRED`
- *…and 76 more `uses` connection(s) not listed (lowest-degree first to go)*

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*