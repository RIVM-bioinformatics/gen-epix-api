# Casedb Test Fixtures

> 8 nodes · cohesion 0.29

## Key Concepts

- **get_test_client()** (5 connections) — `test/casedb/integration/data_access/test_casedb_refdata_access.py`
- **.setup()** (4 connections) — `test/casedb/integration/data_access/test_casedb_refdata_access.py`
- **fixture** (3 connections)
- **.print_edge_cases()** (3 connections) — `test/casedb/integration/data_access/test_casedb_refdata_access.py`
- **Env** (2 connections)
- **Print the active edge cases once per class run when VERBOSE is enabled.** (1 connections) — `test/casedb/integration/data_access/test_casedb_refdata_access.py`
- **Auto-inject the env fixture into the class.** (1 connections) — `test/casedb/integration/data_access/test_casedb_refdata_access.py`
- **Get a test client for casedb integration tests. This fixture initializes a test…** (1 connections) — `test/casedb/integration/data_access/test_casedb_refdata_access.py`

## Relationships

- [Reference Data ABAC Tests](Reference_Data_ABAC_Tests.md) (2 shared connections)
- [Casedb Domain CRUD Commands](Casedb_Domain_CRUD_Commands.md) (1 shared connections)
- [Casedb Test Client Helpers](Casedb_Test_Client_Helpers.md) (1 shared connections)

## Source Files

- `test/casedb/integration/data_access/test_casedb_refdata_access.py`

## Audit Trail

- EXTRACTED: 11 (92%)
- INFERRED: 1 (8%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*