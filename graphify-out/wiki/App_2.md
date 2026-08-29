# App

> God node · 126 connections · `gen_epix/fastapp/app.py`

**Community:** [App](App.md)

## Connections by Relation

### calls
- .__init__() `EXTRACTED`
- .__init__() `EXTRACTED`
- .__init__() `EXTRACTED`
- test_auto_invalidation_runs_after_success_only() `EXTRACTED`
- test_auto_invalidation_runs_for_nested_commands() `EXTRACTED`
- test_invalidate_cache_uses_exact_command_type_and_propagates_errors() `EXTRACTED`
- test_app_starts_with_empty_cache_registries() `EXTRACTED`
- test_register_cache_invalidator_allows_multiple_and_rejects_duplicates() `EXTRACTED`
- test_register_cache_invalidator_logs_at_debug_level() `EXTRACTED`
- test_set_auto_invalidate_cache_toggles_without_removing_registrations() `EXTRACTED`

### contains
- fastapp/app.py `EXTRACTED`

### imports
- gen_epix/fastapp/__init__.py `EXTRACTED`
- [test_commondb_upload.py](test_commondb_upload.py.md) `EXTRACTED`
- [test_casedb_upload.py](test_casedb_upload.py.md) `EXTRACTED`
- [test_omopdb_upload.py](test_omopdb_upload.py.md) `EXTRACTED`
- crud_endpoint_generator.py `EXTRACTED`
- test_commondb_auth.py `EXTRACTED`
- [test_seqdb_upload.py](test_seqdb_upload.py.md) `EXTRACTED`
- gen_epix/fastapp/service.py `EXTRACTED`
- commondb/services/remote_app.py `EXTRACTED`
- test_seqdb_upload_verify_batch_refdata.py `EXTRACTED`
- fastapp/remote_app.py `EXTRACTED`
- test_fastapp_app_log_summarise.py `EXTRACTED`
- test_casedb_retrieve_similar_cases.py `EXTRACTED`
- commondb/services/organization.py `EXTRACTED`
- services/system.py `EXTRACTED`
- auth_test_client.py `EXTRACTED`
- commondb/services/rbac.py `EXTRACTED`
- test_fastapp_app_cache.py `EXTRACTED`
- service/rbac.py `EXTRACTED`
- casedb_endpoint_test_client.py `EXTRACTED`

### method
- .create_log_message() `EXTRACTED`
- .__init__() `EXTRACTED`
- .handle() `EXTRACTED`
- ._execute_command() `EXTRACTED`
- .register_listener() `EXTRACTED`
- .register_policy() `EXTRACTED`
- .unregister_policy() `EXTRACTED`
- .unregister_listener() `EXTRACTED`
- ._get_command_handler() `EXTRACTED`
- .register_cache_invalidator() `EXTRACTED`
- .invalidate_cache() `EXTRACTED`
- ._log_command_finish() `EXTRACTED`
- ._handle_initial_command() `EXTRACTED`
- ._log_command_start() `EXTRACTED`
- .apply_handler() `EXTRACTED`
- ._summarise_command_object_for_log() `EXTRACTED`
- .create_static_log_message() `EXTRACTED`
- .user_manager() `EXTRACTED`
- .logger() `EXTRACTED`
- .log_item_class() `EXTRACTED`

### rationale_for
- Implementation of the Mediator pattern for handling Commands, which represent a… `EXTRACTED`

### uses
- [Model](Model.md) `INFERRED`
- [Domain](Domain.md) `INFERRED`
- [Command](Command.md) `INFERRED`
- [CommondbRemoteApp](CommondbRemoteApp.md) `INFERRED`
- [BaseService](BaseService.md) `INFERRED`
- [CrudCommand](CrudCommand.md) `INFERRED`
- [RemoteApp](RemoteApp.md) `INFERRED`
- [CrudEndpointGenerator](CrudEndpointGenerator.md) `INFERRED`
- [Policy](Policy.md) `INFERRED`
- [AuthEnv](AuthEnv.md) `INFERRED`
- BaseUploadTestCase `INFERRED`
- BaseUploadTestCase `INFERRED`
- LogItem `INFERRED`
- BaseUploadTestCase `INFERRED`
- [BasePersonUploadTestCase](BasePersonUploadTestCase.md) `INFERRED`
- [OrganizationService](OrganizationService.md) `INFERRED`
- [AuthTestClient](AuthTestClient.md) `INFERRED`
- CrudEndpointSet `INFERRED`
- RbacService `INFERRED`
- [BaseLogItem](BaseLogItem.md) `INFERRED`

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*