# Casedb Metadata Masking Tests

> 17 nodes · cohesion 0.14

## Key Concepts

- **TestCasedbMetadataMasking** (12 connections) — `test/casedb/integration/metadata/test_casedb_metadata_masking.py`
- **._read_all_case_types()** (7 connections) — `test/casedb/integration/metadata/test_casedb_metadata_masking.py`
- **setup_users_and_data()** (4 connections) — `test/casedb/integration/metadata/test_casedb_metadata_masking.py`
- **get_test_client()** (3 connections) — `test/casedb/integration/metadata/test_casedb_metadata_masking.py`
- **fixture** (3 connections)
- **.setup()** (3 connections) — `test/casedb/integration/metadata/test_casedb_metadata_masking.py`
- **.test_read_all_case_types_org_admin_does_not_see_masked_metadata()** (3 connections) — `test/casedb/integration/metadata/test_casedb_metadata_masking.py`
- **.test_read_all_case_types_org_user_does_not_see_masked_metadata()** (3 connections) — `test/casedb/integration/metadata/test_casedb_metadata_masking.py`
- **.test_read_all_case_types_root_user_sees_all_metadata()** (3 connections) — `test/casedb/integration/metadata/test_casedb_metadata_masking.py`
- **integration** (1 connections)
- **scenario_ids** (1 connections)
- **User** (1 connections)
- **Verifies that MaskModelProcessMetadataPolicy is correctly wired in casedb. Root…** (1 connections) — `test/casedb/integration/metadata/test_casedb_metadata_masking.py`
- **Root user must see all three metadata fields populated — superusers bypass…** (1 connections) — `test/casedb/integration/metadata/test_casedb_metadata_masking.py`
- **Org admin must see all three metadata fields masked to None by…** (1 connections) — `test/casedb/integration/metadata/test_casedb_metadata_masking.py`
- **Org user must see all three metadata fields masked to None by…** (1 connections) — `test/casedb/integration/metadata/test_casedb_metadata_masking.py`
- **Minimal setup: root + org1 (from bootstrap), invite org_admin and org_user,…** (1 connections) — `test/casedb/integration/metadata/test_casedb_metadata_masking.py`

## Relationships

- [Casedb Endpoint Test Client](Casedb_Endpoint_Test_Client.md) (4 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (3 shared connections)
- [Case Type & Column Commands](Case_Type_&_Column_Commands.md) (2 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (1 shared connections)
- [Case SQLAlchemy Tables](Case_SQLAlchemy_Tables.md) (1 shared connections)

## Source Files

- `test/casedb/integration/metadata/test_casedb_metadata_masking.py`

## Audit Trail

- EXTRACTED: 25 (83%)
- INFERRED: 5 (17%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*