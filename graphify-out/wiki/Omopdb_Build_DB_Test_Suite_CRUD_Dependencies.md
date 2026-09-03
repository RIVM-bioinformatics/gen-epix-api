# Omopdb Build DB Test Suite (CRUD Dependencies)

> 9 nodes

## Key Concepts

- **TestCreate** (4 connections) — `test/omopdb/integration/build_db/test_omopdb_build.py`
- **TestDelete** (4 connections) — `test/omopdb/integration/build_db/test_omopdb_build.py`
- **TestRead** (4 connections) — `test/omopdb/integration/build_db/test_omopdb_build.py`
- **TestUpdate** (4 connections) — `test/omopdb/integration/build_db/test_omopdb_build.py`
- **dependency** (4 connections)
- **ModuleTestCreate** (1 connections)
- **ModuleTestDelete** (1 connections)
- **ModuleTestRead** (1 connections)
- **ModuleTestUpdate** (1 connections)

## Relationships

- [commondb/domain/enum.py](commondb-domain-enum.py.md) (4 shared connections)
- [Casedb Integration Create Tests](Casedb_Integration_Create_Tests.md) (1 shared connections)
- [Casedb Integration Delete Tests](Casedb_Integration_Delete_Tests.md) (1 shared connections)
- [Casedb Integration Read Tests](Casedb_Integration_Read_Tests.md) (1 shared connections)
- [Casedb Integration Update Tests](Casedb_Integration_Update_Tests.md) (1 shared connections)

## Source Files

- `test/omopdb/integration/build_db/test_omopdb_build.py`

## Audit Trail

- EXTRACTED: 12 (75%)
- INFERRED: 4 (25%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*