# Record Metadata Stamping Tests

> 28 nodes · cohesion 0.08

## Key Concepts

- **TestCommondbModelProcessMetadata** (13 connections) — `test/commondb/integration/metadata/test_commondb_metadata.py`
- **TestCasedbModelProcessMetadata** (12 connections) — `test/casedb/integration/metadata/test_casedb_metadata.py`
- **setup_users()** (4 connections) — `test/commondb/integration/metadata/test_commondb_metadata.py`
- **.test_update_case_type_does_not_accept_arbitrary_modified_at()** (3 connections) — `test/casedb/integration/metadata/test_casedb_metadata.py`
- **.test_update_case_type_preserves_created_at()** (3 connections) — `test/casedb/integration/metadata/test_casedb_metadata.py`
- **.test_update_case_type_updates_modified_by()** (3 connections) — `test/casedb/integration/metadata/test_casedb_metadata.py`
- **fixture** (3 connections)
- **.setup()** (3 connections) — `test/commondb/integration/metadata/test_commondb_metadata.py`
- **.test_create_case_type_stamps_all_metadata()** (2 connections) — `test/casedb/integration/metadata/test_casedb_metadata.py`
- **created_at must not change when a record is updated.** (2 connections) — `test/commondb/integration/metadata/test_commondb_metadata.py`
- **modified_by must be stamped with the updating user, not the creating user.** (2 connections) — `test/commondb/integration/metadata/test_commondb_metadata.py`
- **modified_at supplied in the update payload must be ignored by the backend.** (2 connections) — `test/commondb/integration/metadata/test_commondb_metadata.py`
- **Verifies that the CommondbSAMapper (SA backend) and CommondbDictModelModifier…** (2 connections) — `test/commondb/integration/metadata/test_commondb_metadata.py`
- **.test_create_data_collection_stamps_created_at()** (2 connections) — `test/commondb/integration/metadata/test_commondb_metadata.py`
- **.test_create_data_collection_stamps_modified_at()** (2 connections) — `test/commondb/integration/metadata/test_commondb_metadata.py`
- **.test_create_data_collection_stamps_modified_by()** (2 connections) — `test/commondb/integration/metadata/test_commondb_metadata.py`
- **.test_update_data_collection_does_not_accept_arbitrary_modified_at()** (2 connections) — `test/commondb/integration/metadata/test_commondb_metadata.py`
- **.test_update_data_collection_preserves_created_at()** (2 connections) — `test/commondb/integration/metadata/test_commondb_metadata.py`
- **.test_update_data_collection_updates_modified_by()** (2 connections) — `test/commondb/integration/metadata/test_commondb_metadata.py`
- **integration** (1 connections)
- **scenario_ids** (1 connections)
- **created_at, modified_at, and modified_by must all be set by the backend on…** (1 connections) — `test/casedb/integration/metadata/test_casedb_metadata.py`
- **integration** (1 connections)
- **scenario_ids** (1 connections)
- **modified_at must be set by the backend on creation.** (1 connections) — `test/commondb/integration/metadata/test_commondb_metadata.py`
- *... and 3 more nodes in this community*

## Relationships

- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (4 shared connections)
- [Case Type & Column Commands](Case_Type_&_Column_Commands.md) (4 shared connections)
- [Integration Test Client](Integration_Test_Client.md) (3 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (2 shared connections)
- [Reference Data Setup](Reference_Data_Setup.md) (1 shared connections)
- [Casedb Endpoint Test Client](Casedb_Endpoint_Test_Client.md) (1 shared connections)

## Source Files

- `test/casedb/integration/metadata/test_casedb_metadata.py`
- `test/commondb/integration/metadata/test_commondb_metadata.py`

## Audit Trail

- EXTRACTED: 39 (87%)
- INFERRED: 6 (13%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*