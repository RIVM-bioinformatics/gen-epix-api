# CasedbTestClient

> God node · 120 connections · `test/casedb/casedb_test_client.py`

**Community:** [CasedbTestClient](CasedbTestClient.md)

## Connections by Relation

### contains
- casedb_test_client.py `EXTRACTED`

### imports
- test_casedb_case_upload.py `EXTRACTED`
- test_casedb_content.py `EXTRACTED`
- test_casedb_refdata_access.py `EXTRACTED`
- test_casedb_user_journey_performance.py `EXTRACTED`
- test_casedb_build.py `EXTRACTED`
- [test_retrieve_stats.py](test_retrieve_stats.py.md) `EXTRACTED`
- test_casedb_opsdata_access.py `EXTRACTED`
- test_casedb_metadata.py `EXTRACTED`
- test_casedb_metadata_masking.py `EXTRACTED`
- test_casedb_case_upload_content_deletion.py `EXTRACTED`
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
- .get_test_client() `EXTRACTED`
- .create_case_set() `EXTRACTED`
- .__init__() `EXTRACTED`
- .update_association_case_data_collection() `EXTRACTED`
- .create_ref_col() `EXTRACTED`
- .create_case() `EXTRACTED`
- .create_case_data_collection_link() `EXTRACTED`
- .read_case_types_with_any_right() `EXTRACTED`
- .create_concept_set() `EXTRACTED`
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

### uses
- [TestClient](TestClient.md) `INFERRED`
- TestCreate `INFERRED`
- TestUpdate `INFERRED`
- [Role](Role.md) `INFERRED`
- TestDelete `INFERRED`
- AppComposer `INFERRED`
- TestRead `INFERRED`
- [TestcasedbEdgeCasesRefDataAccess](TestcasedbEdgeCasesRefDataAccess.md) `INFERRED`
- TestCasedbEdgeCasesAccess `INFERRED`
- TestRead `INFERRED`
- CasedbEndpointTestClient `INFERRED`
- [TestCaseUpload](TestCaseUpload.md) `INFERRED`
- [TestCasedbMetadataMasking](TestCasedbMetadataMasking.md) `INFERRED`
- TestCasedbModelProcessMetadata `INFERRED`
- retrieve_case_type_stats_profiled() `INFERRED`
- retrieve_case_type_stats() `INFERRED`
- [TestContent](TestContent.md) `INFERRED`
- get_all_case_type_ids() `INFERRED`
- test_retrieve_case_type_stats_scaled_profiled() `INFERRED`
- CaseDataCollectionLink `INFERRED`

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*