# Manual Read Policy Tests

> 10 nodes · cohesion 0.40

## Key Concepts

- **.get_user()** (10 connections) — `test/casedb/custom/test_casedb_custom.py`
- **TestManual** (8 connections) — `test/casedb/custom/test_casedb_custom.py`
- **.test_retrieve_cases_by_query()** (6 connections) — `test/casedb/custom/test_casedb_custom.py`
- **skip** (5 connections)
- **.test_read_organization_access_case_policy()** (4 connections) — `test/casedb/custom/test_casedb_custom.py`
- **.test_read_organization_admin_policy()** (4 connections) — `test/casedb/custom/test_casedb_custom.py`
- **.test_read_user_case_policy()** (4 connections) — `test/casedb/custom/test_casedb_custom.py`
- **.test_retrieve_phylogenetic_tree()** (4 connections) — `test/casedb/custom/test_casedb_custom.py`
- **UUID** (2 connections)
- **User** (1 connections)

## Relationships

- [Integration Test Client](Integration_Test_Client.md) (7 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (2 shared connections)
- [Benchmark Chart Generation](Benchmark_Chart_Generation.md) (1 shared connections)
- [Composite Filters](Composite_Filters.md) (1 shared connections)
- [Range Filters](Range_Filters.md) (1 shared connections)

## Source Files

- `test/casedb/custom/test_casedb_custom.py`

## Audit Trail

- EXTRACTED: 28 (93%)
- INFERRED: 2 (7%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*