# App

> God node · 214 connections · `gen_epix/fastapp/app.py`

**Community:** [Seqdb Sequence Retrieval Commands](Seqdb_Sequence_Retrieval_Commands.md)

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
- test_commondb_upload.py `EXTRACTED`
- test_casedb_upload.py `EXTRACTED`
- test_fastapp_api.py `EXTRACTED`
- test_commondb_auth.py `EXTRACTED`
- test_omopdb_upload.py `EXTRACTED`
- test_seqdb_upload.py `EXTRACTED`
- api/case.py `EXTRACTED`
- test_crud_endpoint_generator.py `EXTRACTED`
- commondb/api/organization.py `EXTRACTED`
- crud_endpoint_generator.py `EXTRACTED`
- gen_epix/fastapp/service.py `EXTRACTED`
- api/system.py `EXTRACTED`
- commondb/services/client.py `EXTRACTED`
- auth/service.py `EXTRACTED`
- api/seq.py `EXTRACTED`
- test_seqdb_upload_verify_batch_refdata.py `EXTRACTED`
- test_fastapp_app_log_summarise.py `EXTRACTED`
- casedb/api/router.py `EXTRACTED`
- commondb/services/abac.py `EXTRACTED`
- *…and 25 more `imports` connection(s) not listed (lowest-degree first to go)*

### inherits
- Client `EXTRACTED`

### method
- .create_log_message() `EXTRACTED`
- .__init__() `EXTRACTED`
- .handle() `EXTRACTED`
- ._execute_command() `EXTRACTED`
- .register_listener() `EXTRACTED`
- .unregister_listener() `EXTRACTED`
- ._get_command_handler() `EXTRACTED`
- .register_policy() `EXTRACTED`
- .unregister_policy() `EXTRACTED`
- ._handle_initial_command() `EXTRACTED`
- ._summarise_command_object_for_log() `EXTRACTED`
- .create_static_log_message() `EXTRACTED`
- .user_manager() `EXTRACTED`
- .logger() `EXTRACTED`
- .register_cache_invalidator() `EXTRACTED`
- .invalidate_cache() `EXTRACTED`
- .register_handler() `EXTRACTED`
- .get_handler() `EXTRACTED`
- ._log_command_finish() `EXTRACTED`
- ._log_command_start() `EXTRACTED`
- *…and 21 more `method` connection(s) not listed (lowest-degree first to go)*

### rationale_for
- Encapsulates a Mediator for handling Commands, which represent a unit of… `EXTRACTED`

### references
- .create_crud_endpoint_set_for_domain() `EXTRACTED`
- .get_crud_endpoint_set_for_entity() `EXTRACTED`
- .create_local_or_remote() `EXTRACTED`
- .__init__() `EXTRACTED`
- .test_generates_multiple_endpoint_types() `EXTRACTED`
- ._create_local_client() `EXTRACTED`
- .test_generates_delete_all_endpoint_on_app() `EXTRACTED`
- .test_generates_delete_one_endpoint_on_app() `EXTRACTED`
- .test_generates_delete_some_endpoint_on_app() `EXTRACTED`
- .test_generates_get_all_endpoint_on_app() `EXTRACTED`
- .test_generates_get_one_endpoint_on_app() `EXTRACTED`
- .test_generates_post_one_endpoint_on_app() `EXTRACTED`
- .test_generates_post_some_endpoint_on_app() `EXTRACTED`
- .test_generates_put_one_endpoint_on_app() `EXTRACTED`
- .test_get_some_uses_default_batch_suffix() `EXTRACTED`
- .test_post_query_uses_default_query_suffix() `EXTRACTED`
- .test_generate_delete_some_with_batch_suffix() `EXTRACTED`
- .test_generate_get_some_with_batch_suffix() `EXTRACTED`
- .test_get_all_handles_command_creation_error() `EXTRACTED`
- .test_model_conversion_when_read_differs_from_model_class() `EXTRACTED`
- *…and 35 more `references` connection(s) not listed (lowest-degree first to go)*

### uses
- Domain `INFERRED`
- BaseService `INFERRED`
- CrudEndpointSet `INFERRED`
- CommondbClient `INFERRED`
- BaseUploadTestCase `INFERRED`
- CrudEndpointGenerator `INFERRED`
- BasePersonUploadTestCase `INFERRED`
- BaseUploadTestCase `INFERRED`
- AuthEnv `INFERRED`
- BaseUploadTestCase `INFERRED`
- EventTiming `INFERRED`
- LogItem `INFERRED`
- BaseUserManager `INFERRED`
- OrganizationService `INFERRED`
- AuthTestClient `INFERRED`
- SystemService `INFERRED`
- RbacService `INFERRED`
- BaseLogItem `INFERRED`
- BaseSnpUploadTestCase `INFERRED`
- BaseRbacService `INFERRED`
- *…and 40 more `uses` connection(s) not listed (lowest-degree first to go)*

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*