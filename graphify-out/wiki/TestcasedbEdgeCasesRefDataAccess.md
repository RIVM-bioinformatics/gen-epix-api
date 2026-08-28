# TestcasedbEdgeCasesRefDataAccess

> 58 nodes · cohesion 0.05

## Key Concepts

- **TestcasedbEdgeCasesRefDataAccess** (19 connections) — `test/casedb/integration/data_access/test_casedb_refdata_access.py`
- **EdgeCaseSpec** (14 connections) — `test/casedb/integration/data_access/setup/define_edge_cases_reference.py`
- **TestCasedbEdgeCasesAccess** (12 connections) — `test/casedb/integration/data_access/test_casedb_opsdata_access.py`
- **.get_user()** (12 connections) — `test/casedb/integration/data_access/test_casedb_refdata_access.py`
- **RefColCrudCommand** (9 connections) — `gen_epix/casedb/domain/command/case.py`
- **.test_case_and_content_cols_access_matches_expected()** (7 connections) — `test/casedb/integration/data_access/test_casedb_opsdata_access.py`
- **.test_case_type_set_access_matches_expected()** (7 connections) — `test/casedb/integration/data_access/test_casedb_refdata_access.py`
- **.get_user()** (6 connections) — `test/casedb/integration/data_access/test_casedb_opsdata_access.py`
- **parametrize** (6 connections)
- **For each edge case, assert that the set of accessible CaseTypes exactly matches…** (6 connections) — `test/casedb/integration/data_access/test_casedb_refdata_access.py`
- **.test_case_type_access_matches_expected()** (6 connections) — `test/casedb/integration/data_access/test_casedb_refdata_access.py`
- **.test_col_access_matches_expected()** (6 connections) — `test/casedb/integration/data_access/test_casedb_refdata_access.py`
- **.test_col_set_access_matches_expected()** (6 connections) — `test/casedb/integration/data_access/test_casedb_refdata_access.py`
- **.test_ref_col_access_matches_expected()** (6 connections) — `test/casedb/integration/data_access/test_casedb_refdata_access.py`
- **.test_ref_dim_access_matches_expected()** (6 connections) — `test/casedb/integration/data_access/test_casedb_refdata_access.py`
- **get_test_client()** (5 connections) — `test/casedb/integration/data_access/test_casedb_opsdata_access.py`
- **get_test_client()** (5 connections) — `test/casedb/integration/data_access/test_casedb_refdata_access.py`
- **.setup()** (4 connections) — `test/casedb/integration/data_access/test_casedb_opsdata_access.py`
- **.setup()** (4 connections) — `test/casedb/integration/data_access/test_casedb_refdata_access.py`
- **.test_case_type_set_category_access_matches_all()** (4 connections) — `test/casedb/integration/data_access/test_casedb_refdata_access.py`
- **.test_org_user_1_exists()** (3 connections) — `test/casedb/integration/data_access/test_casedb_opsdata_access.py`
- **.test_root_user_can_create_case()** (3 connections) — `test/casedb/integration/data_access/test_casedb_opsdata_access.py`
- **fixture** (3 connections)
- **.print_edge_cases()** (3 connections) — `test/casedb/integration/data_access/test_casedb_refdata_access.py`
- **.test_disease_access_matches_all()** (3 connections) — `test/casedb/integration/data_access/test_casedb_refdata_access.py`
- *... and 33 more nodes in this community*

## Relationships

- [commondb/domain/enum.py](commondb-domain-enum.py.md) (7 shared connections)
- [BaseCaseService](BaseCaseService.md) (4 shared connections)
- [CasedbTestClient](CasedbTestClient.md) (4 shared connections)
- [_crud_cascade_delete](_crud_cascade_delete.md) (3 shared connections)
- [casedb/domain/command/__init__.py](casedb-domain-command-__init__.py.md) (2 shared connections)
- [Command](Command.md) (2 shared connections)
- [CaseTypeCrudCommand](CaseTypeCrudCommand.md) (2 shared connections)
- [case_service_crud_ref_col](case_service_crud_ref_col.md) (1 shared connections)
- [CaseService](CaseService.md) (1 shared connections)
- [define_edge_cases_reference.py](define_edge_cases_reference.py.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/domain/command/case.py`
- `test/casedb/integration/data_access/setup/define_edge_cases_reference.py`
- `test/casedb/integration/data_access/test_casedb_opsdata_access.py`
- `test/casedb/integration/data_access/test_casedb_refdata_access.py`

## Audit Trail

- EXTRACTED: 111 (95%)
- INFERRED: 6 (5%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*