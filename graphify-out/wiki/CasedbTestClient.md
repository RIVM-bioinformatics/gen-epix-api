# CasedbTestClient

> God node · 259 connections · `test/casedb/casedb_test_client.py`

**Community:** [Casedb Endpoint Test Client](Casedb_Endpoint_Test_Client.md)

## Connections by Relation

### contains
- casedb_test_client.py `EXTRACTED`

### imports
- test_casedb_case_upload.py `EXTRACTED`
- test_casedb_content.py `EXTRACTED`
- test_casedb_refdata_access.py `EXTRACTED`
- test_casedb_user_journey_performance.py `EXTRACTED`
- test_retrieve_stats.py `EXTRACTED`
- test_casedb_opsdata_access.py `EXTRACTED`
- test_casedb_case_upload_content_deletion.py `EXTRACTED`
- test_casedb_metadata.py `EXTRACTED`
- test_casedb_metadata_masking.py `EXTRACTED`
- test_casedb_build.py `EXTRACTED`
- test_casedb_repository_performance.py `EXTRACTED`
- test_casedb_startup_performance.py `EXTRACTED`
- casedb/integration/build_db/update.py `EXTRACTED`
- casedb/integration/build_db/create.py `EXTRACTED`
- casedb/integration/build_db/read.py `EXTRACTED`
- setup_case_data_reference.py `EXTRACTED`
- casedb/integration/build_db/delete.py `EXTRACTED`
- setup_case_data_operational.py `EXTRACTED`
- setup_test_users_and_organizations_operational.py `EXTRACTED`
- setup_test_users_and_organizations_reference.py `EXTRACTED`

### inherits
- [TestClient](TestClient.md) `EXTRACTED`

### method
- .get_obj() `EXTRACTED`
- .create_case_set() `EXTRACTED`
- .create_ref_col() `EXTRACTED`
- .get_test_client() `EXTRACTED`
- .update_association_case_data_collection() `EXTRACTED`
- .create_concept_set() `EXTRACTED`
- .create_case() `EXTRACTED`
- .create_case_data_collection_link() `EXTRACTED`
- .read_case_types_with_any_right() `EXTRACTED`
- .__init__() `EXTRACTED`
- .create_organization_access_case_policy() `EXTRACTED`
- .create_user_access_case_policy() `EXTRACTED`
- .create_user_share_case_policy() `EXTRACTED`
- .read_user_access_case_policies_with_any_right() `EXTRACTED`
- .create_concept() `EXTRACTED`
- .create_genetic_distance_protocol() `EXTRACTED`
- .create_etiology() `EXTRACTED`
- .create_case_type() `EXTRACTED`
- .create_case_type_set_member() `EXTRACTED`
- .create_case_type_set() `EXTRACTED`
- *…and 38 more `method` connection(s) not listed (lowest-degree first to go)*

### references
- .setup() `EXTRACTED`
- ._setup_casedb_app() `EXTRACTED`
- ._setup_seqdb_app() `EXTRACTED`
- .test_case_upload() `EXTRACTED`
- .test_case_validation() `EXTRACTED`
- .test_content() `EXTRACTED`
- .setup() `EXTRACTED`
- .setup() `EXTRACTED`
- .test_create_case_set_category() `EXTRACTED`
- .test_create_case_set_category_raise() `EXTRACTED`
- .test_create_case_set_status() `EXTRACTED`
- .test_create_case_set_status_raise() `EXTRACTED`
- .test_create_case_type() `EXTRACTED`
- .test_create_case_type_raise() `EXTRACTED`
- .test_create_case_type_set() `EXTRACTED`
- .test_create_case_type_set_category() `EXTRACTED`
- .test_create_case_type_set_category_raise() `EXTRACTED`
- .test_create_case_type_set_member_raise() `EXTRACTED`
- .test_create_case_type_set_raise() `EXTRACTED`
- .test_create_col() `EXTRACTED`
- *…and 120 more `references` connection(s) not listed (lowest-degree first to go)*

### uses
- TestCreate `INFERRED`
- Role `INFERRED`
- AppComposer `INFERRED`
- TestUpdate `INFERRED`
- TestDelete `INFERRED`
- TestcasedbEdgeCasesRefDataAccess `INFERRED`
- TestRead `INFERRED`
- TestCasedbEdgeCasesAccess `INFERRED`
- TestRead `INFERRED`
- CasedbEndpointTestClient `INFERRED`
- TestCaseUpload `INFERRED`
- TestCasedbMetadataMasking `INFERRED`
- TestCasedbModelProcessMetadata `INFERRED`
- CaseDataCollectionLink `INFERRED`
- CaseUploadSetup `INFERRED`
- retrieve_case_type_stats_profiled() `INFERRED`
- TestContent `INFERRED`
- TestStartup `INFERRED`
- retrieve_case_type_stats() `INFERRED`
- TestRead `INFERRED`
- *…and 19 more `uses` connection(s) not listed (lowest-degree first to go)*

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*