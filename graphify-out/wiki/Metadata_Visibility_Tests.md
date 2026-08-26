# Metadata Visibility Tests

> 16 nodes · cohesion 0.15

## Key Concepts

- **TestCommondbMetadataMasking** (8 connections) — `test/commondb/integration/metadata/test_commondb_metadata_masking.py`
- **get_test_client()** (6 connections) — `test/commondb/integration/metadata/test_commondb_metadata_masking.py`
- **setup_users()** (5 connections) — `test/commondb/integration/metadata/test_commondb_metadata_masking.py`
- **._read_all_data_collections()** (4 connections) — `test/commondb/integration/metadata/test_commondb_metadata_masking.py`
- **Env** (3 connections)
- **fixture** (3 connections)
- **.setup()** (3 connections) — `test/commondb/integration/metadata/test_commondb_metadata_masking.py`
- **.test_read_all_data_collections()** (3 connections) — `test/commondb/integration/metadata/test_commondb_metadata_masking.py`
- **DataCollection** (1 connections)
- **FixtureRequest** (1 connections)
- **integration** (1 connections)
- **scenario_ids** (1 connections)
- **User** (1 connections)
- **Only APP_ADMIN or ROOT users can see created_at, modified_at, and modified_by,…** (1 connections) — `test/commondb/integration/metadata/test_commondb_metadata_masking.py`
- **Register root1_1 + org1, then invite an org_user and an org_admin.** (1 connections) — `test/commondb/integration/metadata/test_commondb_metadata_masking.py`
- **Verifies that commondb does NOT mask metadata fields for any user role. In…** (1 connections) — `test/commondb/integration/metadata/test_commondb_metadata_masking.py`

## Relationships

- [Commondb Enums & Demo Data](Commondb_Enums_&_Demo_Data.md) (4 shared connections)
- [Integration Test Client Helpers](Integration_Test_Client_Helpers.md) (3 shared connections)

## Source Files

- `test/commondb/integration/metadata/test_commondb_metadata_masking.py`

## Audit Trail

- EXTRACTED: 21 (84%)
- INFERRED: 4 (16%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*