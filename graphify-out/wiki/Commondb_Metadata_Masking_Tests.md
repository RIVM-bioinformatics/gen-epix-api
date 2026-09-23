# Commondb Metadata Masking Tests

> 13 nodes · cohesion 0.17

## Key Concepts

- **TestCommondbMetadataMasking** (9 connections) — `test/commondb/integration/metadata/test_commondb_metadata_masking.py`
- **setup_users()** (4 connections) — `test/commondb/integration/metadata/test_commondb_metadata_masking.py`
- **._read_all_data_collections()** (4 connections) — `test/commondb/integration/metadata/test_commondb_metadata_masking.py`
- **fixture** (3 connections)
- **.setup()** (3 connections) — `test/commondb/integration/metadata/test_commondb_metadata_masking.py`
- **.test_read_all_data_collections()** (3 connections) — `test/commondb/integration/metadata/test_commondb_metadata_masking.py`
- **DataCollection** (1 connections)
- **integration** (1 connections)
- **scenario_ids** (1 connections)
- **User** (1 connections)
- **Only APP_ADMIN or ROOT users can see created_at, modified_at, and modified_by,…** (1 connections) — `test/commondb/integration/metadata/test_commondb_metadata_masking.py`
- **Register root1_1 + org1, then invite an org_user and an org_admin.** (1 connections) — `test/commondb/integration/metadata/test_commondb_metadata_masking.py`
- **Verifies that commondb does NOT mask metadata fields for any user role. In…** (1 connections) — `test/commondb/integration/metadata/test_commondb_metadata_masking.py`

## Relationships

- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (3 shared connections)
- [Integration Test Client](Integration_Test_Client.md) (3 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (1 shared connections)

## Source Files

- `test/commondb/integration/metadata/test_commondb_metadata_masking.py`

## Audit Trail

- EXTRACTED: 17 (85%)
- INFERRED: 3 (15%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*