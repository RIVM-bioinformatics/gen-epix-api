# TestClient

> God node · 205 connections · `gen_epix/commondb/test/test_client.py`

**Community:** [Integration Test Client](Integration_Test_Client.md)

## Connections by Relation

### calls
- .__init__() `INFERRED`
- get_test_client() `EXTRACTED`

### contains
- test_client.py `EXTRACTED`

### imports
- casedb_test_client.py `EXTRACTED`
- seqdb_test_client.py `EXTRACTED`
- test_commondb_build.py `EXTRACTED`
- commondb/test_client/util.py `EXTRACTED`
- test_commondb_metadata.py `EXTRACTED`
- test_commondb_metadata_masking.py `EXTRACTED`
- test_commondb_sql_injection.py `EXTRACTED`
- omopdb_test_client.py `EXTRACTED`
- test_casedb_custom.py `EXTRACTED`
- omopdb/integration/build_db/create.py `EXTRACTED`
- commondb/integration/build_db/update.py `EXTRACTED`
- omopdb/integration/build_db/update.py `EXTRACTED`
- seqdb/integration/build_db/update.py `EXTRACTED`
- commondb/util.py `EXTRACTED`
- commondb/integration/build_db/create.py `EXTRACTED`
- commondb/integration/build_db/delete.py `EXTRACTED`
- commondb/integration/build_db/read.py `EXTRACTED`
- omopdb/integration/build_db/delete.py `EXTRACTED`
- omopdb/integration/build_db/read.py `EXTRACTED`
- seqdb/integration/build_db/delete.py `EXTRACTED`
- *…and 1 more `imports` connection(s) not listed (lowest-degree first to go)*

### inherits
- [CasedbTestClient](CasedbTestClient.md) `EXTRACTED`
- SeqdbTestClient `EXTRACTED`
- OmopdbTestClient `EXTRACTED`

### method
- .get_obj() `EXTRACTED`
- .handle() `EXTRACTED`
- .read_all() `EXTRACTED`
- .set_obj() `EXTRACTED`
- .update_object() `EXTRACTED`
- .create_data_collection() `EXTRACTED`
- .read_some() `EXTRACTED`
- .verify_read_all() `EXTRACTED`
- ._update_object_properties() `EXTRACTED`
- ._get_resolved_link_value() `EXTRACTED`
- .invite_and_register_user() `EXTRACTED`
- .create_organization_identifier_issuer_link() `EXTRACTED`
- .update_user() `EXTRACTED`
- .get_root_user() `EXTRACTED`
- .delete_object() `EXTRACTED`
- ._set_log_level() `EXTRACTED`
- ._verify_updated_obj() `EXTRACTED`
- .create_org_admin_policy() `EXTRACTED`
- .__init__() `EXTRACTED`
- .create_identifier_issuer() `EXTRACTED`
- *…and 29 more `method` connection(s) not listed (lowest-degree first to go)*

### rationale_for
- Encapsulates integration-test helpers for querying and verifying application… `EXTRACTED`

### references
- client() `EXTRACTED`
- .get_user() `EXTRACTED`
- .test_retrieve_cases_by_query() `EXTRACTED`
- .test_read_organization_access_case_policy() `EXTRACTED`
- .test_read_organization_admin_policy() `EXTRACTED`
- .test_read_user_case_policy() `EXTRACTED`
- .test_retrieve_phylogenetic_tree() `EXTRACTED`
- .session() `EXTRACTED`
- .test_sql_injection_is_existing_user_by_key() `EXTRACTED`
- .test_create_object_already_exists() `EXTRACTED`
- .test_create_object_invalid_reference() `EXTRACTED`
- .test_create_org_admin_policy_raise() `EXTRACTED`
- .test_create_organization_raise() `EXTRACTED`
- .test_create_user_raise() `EXTRACTED`
- .test_delete_organization_raise() `EXTRACTED`
- .test_delete_user() `EXTRACTED`
- .test_delete_user_raise() `EXTRACTED`
- .test_read_organization_admin_emails_raise() `EXTRACTED`
- .test_read_user_raise() `EXTRACTED`
- .test_anonymize_user() `EXTRACTED`
- *…and 81 more `references` connection(s) not listed (lowest-degree first to go)*

### uses
- [CrudOperation](CrudOperation.md) `INFERRED`
- AppImplDetails `INFERRED`
- EndpointTestClient `INFERRED`
- TestCreate `INFERRED`
- TestCreate `INFERRED`
- BaseAppComposer `INFERRED`
- TestCommondbModelProcessMetadata `INFERRED`
- TestUpdate `INFERRED`
- TestUpdate `INFERRED`
- TestUpdate `INFERRED`
- retrieve_db_data_from_file() `INFERRED`
- TestDelete `INFERRED`
- TestRead `INFERRED`
- TestCommondbMetadataMasking `INFERRED`
- TestSQLInjection `INFERRED`
- TestDelete `INFERRED`
- TestRead `INFERRED`
- TestDelete `INFERRED`
- TestRead `INFERRED`
- TestManual `INFERRED`
- *…and 7 more `uses` connection(s) not listed (lowest-degree first to go)*

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*