# Metadata Masking Policy Tests

> 19 nodes · cohesion 0.13

## Key Concepts

- **TestCasedbMetadataMasking** (10 connections) — `test/casedb/integration/metadata/test_casedb_metadata_masking.py`
- **._read_all_case_types()** (7 connections) — `test/casedb/integration/metadata/test_casedb_metadata_masking.py`
- **get_test_client()** (5 connections) — `test/casedb/integration/metadata/test_casedb_metadata_masking.py`
- **setup_users_and_data()** (5 connections) — `test/casedb/integration/metadata/test_casedb_metadata_masking.py`
- **Env** (3 connections)
- **fixture** (3 connections)
- **.setup()** (3 connections) — `test/casedb/integration/metadata/test_casedb_metadata_masking.py`
- **.test_read_all_case_types_org_admin_does_not_see_masked_metadata()** (3 connections) — `test/casedb/integration/metadata/test_casedb_metadata_masking.py`
- **.test_read_all_case_types_org_user_does_not_see_masked_metadata()** (3 connections) — `test/casedb/integration/metadata/test_casedb_metadata_masking.py`
- **.test_read_all_case_types_root_user_sees_all_metadata()** (3 connections) — `test/casedb/integration/metadata/test_casedb_metadata_masking.py`
- **CaseType** (1 connections)
- **integration** (1 connections)
- **scenario_ids** (1 connections)
- **User** (1 connections)
- **Verifies that MaskModelProcessMetadataPolicy is correctly wired in casedb. Root…** (1 connections) — `test/casedb/integration/metadata/test_casedb_metadata_masking.py`
- **Root user must see all three metadata fields populated — superusers bypass…** (1 connections) — `test/casedb/integration/metadata/test_casedb_metadata_masking.py`
- **Org admin must see all three metadata fields masked to None by…** (1 connections) — `test/casedb/integration/metadata/test_casedb_metadata_masking.py`
- **Org user must see all three metadata fields masked to None by…** (1 connections) — `test/casedb/integration/metadata/test_casedb_metadata_masking.py`
- **Minimal setup: root + org1 (from bootstrap), invite org_admin and org_user,…** (1 connections) — `test/casedb/integration/metadata/test_casedb_metadata_masking.py`

## Relationships

- [Commondb Enums & Demo Data](Commondb_Enums_&_Demo_Data.md) (4 shared connections)
- [Casedb Test Client Helpers](Casedb_Test_Client_Helpers.md) (3 shared connections)
- [Casedb Domain CRUD Commands](Casedb_Domain_CRUD_Commands.md) (1 shared connections)

## Source Files

- `test/casedb/integration/metadata/test_casedb_metadata_masking.py`

## Audit Trail

- EXTRACTED: 27 (87%)
- INFERRED: 4 (13%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*