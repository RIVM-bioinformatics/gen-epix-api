# Edge Cases Reference Generator

> 21 nodes · cohesion 0.12

## Key Concepts

- **define_edge_cases_reference.py** (16 connections) — `test/casedb/integration/data_access/setup/define_edge_cases_reference.py`
- **_compute_expected_cols()** (5 connections) — `test/casedb/integration/data_access/setup/define_edge_cases_reference.py`
- **_parse_col()** (4 connections) — `test/casedb/integration/data_access/setup/define_edge_cases_reference.py`
- **_compute_expected_case_types()** (3 connections) — `test/casedb/integration/data_access/setup/define_edge_cases_reference.py`
- **_compute_expected_col_sets()** (3 connections) — `test/casedb/integration/data_access/setup/define_edge_cases_reference.py`
- **_compute_expected_ref_cols()** (3 connections) — `test/casedb/integration/data_access/setup/define_edge_cases_reference.py`
- **_compute_expected_ref_dims()** (3 connections) — `test/casedb/integration/data_access/setup/define_edge_cases_reference.py`
- **_get_case_type_from_col()** (3 connections) — `test/casedb/integration/data_access/setup/define_edge_cases_reference.py`
- **_compute_expected_case_type_sets()** (2 connections) — `test/casedb/integration/data_access/setup/define_edge_cases_reference.py`
- **_compute_expected_cases()** (2 connections) — `test/casedb/integration/data_access/setup/define_edge_cases_reference.py`
- **_generate_label()** (1 connections) — `test/casedb/integration/data_access/setup/define_edge_cases_reference.py`
- **This module defines the EDGE_CASES data structure, both used to: 1) generate…** (1 connections) — `test/casedb/integration/data_access/setup/define_edge_cases_reference.py`
- **For reference data access, only org-level policies determine access (union of…** (1 connections) — `test/casedb/integration/data_access/setup/define_edge_cases_reference.py`
- **Only the CaseTypeSets referenced in org-level policies (access ∪ share) are…** (1 connections) — `test/casedb/integration/data_access/setup/define_edge_cases_reference.py`
- **ColSet access comes exclusively from org access policies — not from share…** (1 connections) — `test/casedb/integration/data_access/setup/define_edge_cases_reference.py`
- **Extract the CaseType name from a Col code by naming convention:…** (1 connections) — `test/casedb/integration/data_access/setup/define_edge_cases_reference.py`
- **Accessible Cols = those in accessible ColSets whose embedded CaseType is…** (1 connections) — `test/casedb/integration/data_access/setup/define_edge_cases_reference.py`
- **Parse col{ct}_{ref_dim}_{occ}_{rank} → (ct, ref_dim, occ, rank).** (1 connections) — `test/casedb/integration/data_access/setup/define_edge_cases_reference.py`
- **RefCols referenced by the accessible Cols: ref_col{ref_dim}_{rank}.** (1 connections) — `test/casedb/integration/data_access/setup/define_edge_cases_reference.py`
- **RefDims referenced by the accessible Cols: ref_dim{ref_dim}.** (1 connections) — `test/casedb/integration/data_access/setup/define_edge_cases_reference.py`
- **Determine the expected cases accessible for operational data. For operational…** (1 connections) — `test/casedb/integration/data_access/setup/define_edge_cases_reference.py`

## Relationships

- [ABAC Operational Data Edge Cases](ABAC_Operational_Data_Edge_Cases.md) (2 shared connections)
- [Commondb Enums & Demo Data](Commondb_Enums_&_Demo_Data.md) (1 shared connections)
- [Casedb Domain CRUD Commands](Casedb_Domain_CRUD_Commands.md) (1 shared connections)
- [ABAC Edge Case Tests](ABAC_Edge_Case_Tests.md) (1 shared connections)

## Source Files

- `test/casedb/integration/data_access/setup/define_edge_cases_reference.py`

## Audit Trail

- EXTRACTED: 30 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*