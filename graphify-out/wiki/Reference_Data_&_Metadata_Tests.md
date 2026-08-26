# Reference Data & Metadata Tests

> 18 nodes · cohesion 0.12

## Key Concepts

- **TestCasedbModelProcessMetadata** (10 connections) — `test/casedb/integration/metadata/test_casedb_metadata.py`
- **get_test_client()** (5 connections) — `test/casedb/integration/metadata/test_casedb_metadata.py`
- **setup_reference_data()** (5 connections) — `test/casedb/integration/metadata/test_casedb_metadata.py`
- **Env** (3 connections)
- **fixture** (3 connections)
- **.setup()** (3 connections) — `test/casedb/integration/metadata/test_casedb_metadata.py`
- **.test_update_case_type_does_not_accept_arbitrary_modified_at()** (3 connections) — `test/casedb/integration/metadata/test_casedb_metadata.py`
- **.test_update_case_type_preserves_created_at()** (3 connections) — `test/casedb/integration/metadata/test_casedb_metadata.py`
- **.test_update_case_type_updates_modified_by()** (3 connections) — `test/casedb/integration/metadata/test_casedb_metadata.py`
- **.test_create_case_type_stamps_all_metadata()** (2 connections) — `test/casedb/integration/metadata/test_casedb_metadata.py`
- **integration** (1 connections)
- **scenario_ids** (1 connections)
- **created_at, modified_at, and modified_by must all be set by the backend on…** (1 connections) — `test/casedb/integration/metadata/test_casedb_metadata.py`
- **created_at must not change when a record is updated.** (1 connections) — `test/casedb/integration/metadata/test_casedb_metadata.py`
- **modified_at supplied in the update payload must be ignored by the backend.** (1 connections) — `test/casedb/integration/metadata/test_casedb_metadata.py`
- **modified_by must be stamped with the updating user, not the creating user.** (1 connections) — `test/casedb/integration/metadata/test_casedb_metadata.py`
- **Register root1_1 + org1, invite root1_2, and create minimum CaseType…** (1 connections) — `test/casedb/integration/metadata/test_casedb_metadata.py`
- **Verifies that the CommondbSAMapper (SA backend) and CommondbDictModelModifier…** (1 connections) — `test/casedb/integration/metadata/test_casedb_metadata.py`

## Relationships

- [Commondb Enums & Demo Data](Commondb_Enums_&_Demo_Data.md) (4 shared connections)
- [Casedb Test Client Helpers](Casedb_Test_Client_Helpers.md) (3 shared connections)
- [Casedb Domain CRUD Commands](Casedb_Domain_CRUD_Commands.md) (3 shared connections)

## Source Files

- `test/casedb/integration/metadata/test_casedb_metadata.py`

## Audit Trail

- EXTRACTED: 25 (86%)
- INFERRED: 4 (14%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*