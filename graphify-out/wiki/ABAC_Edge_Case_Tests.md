# ABAC Edge Case Tests

> 20 nodes · cohesion 0.16

## Key Concepts

- **EdgeCaseSpec** (14 connections) — `test/casedb/integration/data_access/setup/define_edge_cases_reference.py`
- **.get_user()** (12 connections) — `test/casedb/integration/data_access/test_casedb_refdata_access.py`
- **.test_case_type_set_access_matches_expected()** (7 connections) — `test/casedb/integration/data_access/test_casedb_refdata_access.py`
- **parametrize** (6 connections)
- **.test_case_type_access_matches_expected()** (6 connections) — `test/casedb/integration/data_access/test_casedb_refdata_access.py`
- **.test_col_access_matches_expected()** (6 connections) — `test/casedb/integration/data_access/test_casedb_refdata_access.py`
- **.test_col_set_access_matches_expected()** (6 connections) — `test/casedb/integration/data_access/test_casedb_refdata_access.py`
- **.test_ref_col_access_matches_expected()** (6 connections) — `test/casedb/integration/data_access/test_casedb_refdata_access.py`
- **.test_ref_dim_access_matches_expected()** (6 connections) — `test/casedb/integration/data_access/test_casedb_refdata_access.py`
- **skip** (2 connections)
- **.description()** (1 connections) — `test/casedb/integration/data_access/setup/define_edge_cases_reference.py`
- **Declarative specification for a single ABAC edge case. Captures all relevant…** (1 connections) — `test/casedb/integration/data_access/setup/define_edge_cases_reference.py`
- **User** (1 connections)
- **Helper method to retrieve a user by name from the test client environment.** (1 connections) — `test/casedb/integration/data_access/test_casedb_refdata_access.py`
- **For each edge case, assert that the set of accessible CaseTypes exactly matches…** (1 connections) — `test/casedb/integration/data_access/test_casedb_refdata_access.py`
- **For each edge case, assert that the set of accessible CaseTypeSets exactly…** (1 connections) — `test/casedb/integration/data_access/test_casedb_refdata_access.py`
- **For each edge case, assert that the set of accessible ColSets exactly matches…** (1 connections) — `test/casedb/integration/data_access/test_casedb_refdata_access.py`
- **For each edge case, assert that the set of accessible cols exactly matches the…** (1 connections) — `test/casedb/integration/data_access/test_casedb_refdata_access.py`
- **For each edge case, assert that the set of accessible ref_dims exactly matches…** (1 connections) — `test/casedb/integration/data_access/test_casedb_refdata_access.py`
- **For each edge case, assert that the set of accessible cols exactly matches the…** (1 connections) — `test/casedb/integration/data_access/test_casedb_refdata_access.py`

## Relationships

- [Reference Data ABAC Tests](Reference_Data_ABAC_Tests.md) (11 shared connections)
- [Casedb Domain CRUD Commands](Casedb_Domain_CRUD_Commands.md) (5 shared connections)
- [Casedb Case CRUD Commands](Casedb_Case_CRUD_Commands.md) (2 shared connections)
- [Commondb Enums & Demo Data](Commondb_Enums_&_Demo_Data.md) (1 shared connections)
- [Edge Cases Reference Generator](Edge_Cases_Reference_Generator.md) (1 shared connections)
- [Casedb Access Integration Tests](Casedb_Access_Integration_Tests.md) (1 shared connections)

## Source Files

- `test/casedb/integration/data_access/setup/define_edge_cases_reference.py`
- `test/casedb/integration/data_access/test_casedb_refdata_access.py`

## Audit Trail

- EXTRACTED: 49 (96%)
- INFERRED: 2 (4%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*