# Reference Data Setup

> 5 nodes · cohesion 0.40

## Key Concepts

- **setup_reference_data()** (4 connections) — `test/casedb/integration/metadata/test_casedb_metadata.py`
- **get_test_client()** (3 connections) — `test/casedb/integration/metadata/test_casedb_metadata.py`
- **fixture** (3 connections)
- **.setup()** (3 connections) — `test/casedb/integration/metadata/test_casedb_metadata.py`
- **Register root1_1 + org1, invite root1_2, and create minimum CaseType…** (1 connections) — `test/casedb/integration/metadata/test_casedb_metadata.py`

## Relationships

- [Casedb Endpoint Test Client](Casedb_Endpoint_Test_Client.md) (3 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (2 shared connections)
- [Record Metadata Stamping Tests](Record_Metadata_Stamping_Tests.md) (1 shared connections)

## Source Files

- `test/casedb/integration/metadata/test_casedb_metadata.py`

## Audit Trail

- EXTRACTED: 8 (80%)
- INFERRED: 2 (20%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*