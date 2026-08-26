# Metadata Stamping Tests

> 22 nodes · cohesion 0.10

## Key Concepts

- **TestCommondbModelProcessMetadata** (12 connections) — `test/commondb/integration/metadata/test_commondb_metadata.py`
- **get_test_client()** (5 connections) — `test/commondb/integration/metadata/test_commondb_metadata.py`
- **setup_users()** (5 connections) — `test/commondb/integration/metadata/test_commondb_metadata.py`
- **Env** (3 connections)
- **fixture** (3 connections)
- **.setup()** (3 connections) — `test/commondb/integration/metadata/test_commondb_metadata.py`
- **.test_create_data_collection_stamps_created_at()** (2 connections) — `test/commondb/integration/metadata/test_commondb_metadata.py`
- **.test_create_data_collection_stamps_modified_at()** (2 connections) — `test/commondb/integration/metadata/test_commondb_metadata.py`
- **.test_create_data_collection_stamps_modified_by()** (2 connections) — `test/commondb/integration/metadata/test_commondb_metadata.py`
- **.test_update_data_collection_does_not_accept_arbitrary_modified_at()** (2 connections) — `test/commondb/integration/metadata/test_commondb_metadata.py`
- **.test_update_data_collection_preserves_created_at()** (2 connections) — `test/commondb/integration/metadata/test_commondb_metadata.py`
- **.test_update_data_collection_updates_modified_by()** (2 connections) — `test/commondb/integration/metadata/test_commondb_metadata.py`
- **integration** (1 connections)
- **scenario_ids** (1 connections)
- **modified_at must be set by the backend on creation.** (1 connections) — `test/commondb/integration/metadata/test_commondb_metadata.py`
- **modified_by must be set to the creating user's id.** (1 connections) — `test/commondb/integration/metadata/test_commondb_metadata.py`
- **created_at must not change when a record is updated.** (1 connections) — `test/commondb/integration/metadata/test_commondb_metadata.py`
- **modified_by must be stamped with the updating user, not the creating user.** (1 connections) — `test/commondb/integration/metadata/test_commondb_metadata.py`
- **modified_at supplied in the update payload must be ignored by the backend.** (1 connections) — `test/commondb/integration/metadata/test_commondb_metadata.py`
- **Register root1_1 + org1, then invite root1_2 so tests have two distinct users.** (1 connections) — `test/commondb/integration/metadata/test_commondb_metadata.py`
- **Verifies that the CommondbSAMapper (SA backend) and CommondbDictModelModifier…** (1 connections) — `test/commondb/integration/metadata/test_commondb_metadata.py`
- **created_at must be set by the backend on creation.** (1 connections) — `test/commondb/integration/metadata/test_commondb_metadata.py`

## Relationships

- [Commondb Enums & Demo Data](Commondb_Enums_&_Demo_Data.md) (4 shared connections)
- [Integration Test Client Helpers](Integration_Test_Client_Helpers.md) (3 shared connections)

## Source Files

- `test/commondb/integration/metadata/test_commondb_metadata.py`

## Audit Trail

- EXTRACTED: 26 (87%)
- INFERRED: 4 (13%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*