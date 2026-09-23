# Case Type Access Tests

> 34 nodes · cohesion 0.08

## Key Concepts

- **TestcasedbEdgeCasesRefDataAccess** (21 connections) — `test/casedb/integration/data_access/test_casedb_refdata_access.py`
- **.get_user()** (12 connections) — `test/casedb/integration/data_access/test_casedb_refdata_access.py`
- **.test_case_type_set_access_matches_expected()** (7 connections) — `test/casedb/integration/data_access/test_casedb_refdata_access.py`
- **parametrize** (6 connections)
- **.test_case_type_access_matches_expected()** (6 connections) — `test/casedb/integration/data_access/test_casedb_refdata_access.py`
- **.test_col_access_matches_expected()** (6 connections) — `test/casedb/integration/data_access/test_casedb_refdata_access.py`
- **.test_col_set_access_matches_expected()** (6 connections) — `test/casedb/integration/data_access/test_casedb_refdata_access.py`
- **.test_ref_col_access_matches_expected()** (6 connections) — `test/casedb/integration/data_access/test_casedb_refdata_access.py`
- **get_test_client()** (4 connections) — `test/casedb/integration/data_access/test_casedb_refdata_access.py`
- **.setup()** (4 connections) — `test/casedb/integration/data_access/test_casedb_refdata_access.py`
- **.test_case_type_set_category_access_matches_all()** (4 connections) — `test/casedb/integration/data_access/test_casedb_refdata_access.py`
- **fixture** (3 connections)
- **.print_edge_cases()** (3 connections) — `test/casedb/integration/data_access/test_casedb_refdata_access.py`
- **.test_disease_access_matches_all()** (3 connections) — `test/casedb/integration/data_access/test_casedb_refdata_access.py`
- **.test_etiological_agent_access_matches_all()** (3 connections) — `test/casedb/integration/data_access/test_casedb_refdata_access.py`
- **.test_root_user_has_access_to_all_case_types()** (3 connections) — `test/casedb/integration/data_access/test_casedb_refdata_access.py`
- **skip** (2 connections)
- **integration** (1 connections)
- **scenario_ids** (1 connections)
- **User** (1 connections)
- **Print the active edge cases once per class run when VERBOSE is enabled.** (1 connections) — `test/casedb/integration/data_access/test_casedb_refdata_access.py`
- **Auto-inject the env fixture into the class.** (1 connections) — `test/casedb/integration/data_access/test_casedb_refdata_access.py`
- **Helper method to retrieve a user by name from the test client environment.** (1 connections) — `test/casedb/integration/data_access/test_casedb_refdata_access.py`
- **Root user should have access to all CaseTypes regardless of policies (superuser…** (1 connections) — `test/casedb/integration/data_access/test_casedb_refdata_access.py`
- **For each edge case, assert that the set of accessible CaseTypes exactly matches…** (1 connections) — `test/casedb/integration/data_access/test_casedb_refdata_access.py`
- *... and 9 more nodes in this community*

## Relationships

- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (12 shared connections)
- [Case Type & Column Commands](Case_Type_&_Column_Commands.md) (5 shared connections)
- [Casedb Endpoint Test Client](Casedb_Endpoint_Test_Client.md) (3 shared connections)
- [Case SQLAlchemy Tables](Case_SQLAlchemy_Tables.md) (1 shared connections)
- [Reference Column CRUD](Reference_Column_CRUD.md) (1 shared connections)

## Source Files

- `test/casedb/integration/data_access/test_casedb_refdata_access.py`

## Audit Trail

- EXTRACTED: 64 (93%)
- INFERRED: 5 (7%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*