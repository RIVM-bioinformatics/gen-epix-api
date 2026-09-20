# Case Repository

> 20 nodes · cohesion 0.12

## Key Concepts

- **datetime_range.py** (15 connections) — `gen_epix/filter/datetime_range.py`
- **repository/case.py** (13 connections) — `gen_epix/casedb/domain/repository/case.py`
- **BaseCaseRepository** (10 connections) — `gen_epix/casedb/domain/repository/case.py`
- **case_dict.py** (10 connections) — `gen_epix/casedb/repositories/case_dict.py`
- **CaseDictRepository** (8 connections) — `gen_epix/casedb/repositories/case_dict.py`
- **.retrieve_case_stats()** (7 connections) — `gen_epix/casedb/domain/repository/case.py`
- **.retrieve_case_stats()** (6 connections) — `gen_epix/casedb/repositories/case_dict.py`
- **._get_date_mappers()** (4 connections) — `gen_epix/casedb/domain/repository/case.py`
- **datetime** (2 connections)
- **UUID** (2 connections)
- **UUID** (2 connections)
- **Define backend-independent persistence operations for Casedb case data.** (1 connections) — `gen_epix/casedb/domain/repository/case.py`
- **Encapsulates case persistence and aggregate statistics reads. Concrete…** (1 connections) — `gen_epix/casedb/domain/repository/case.py`
- **Build temporal-resolution date normalization functions. Returns: A mapper for…** (1 connections) — `gen_epix/casedb/domain/repository/case.py`
- **Read aggregate statistics for a case type within a unit of work.…** (1 connections) — `gen_epix/casedb/domain/repository/case.py`
- **BaseCaseRepository** (1 connections)
- **ColType** (1 connections)
- **Provide dictionary-backed persistence for casedb case data.** (1 connections) — `gen_epix/casedb/repositories/case_dict.py`
- **Encapsulates dictionary-backed persistence for casedb case data.** (1 connections) — `gen_epix/casedb/repositories/case_dict.py`
- **Datetime-valued inclusive and exclusive range filters.** (1 connections) — `gen_epix/filter/datetime_range.py`

## Relationships

- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (10 shared connections)
- [SQLAlchemy Case Repository](SQLAlchemy_Case_Repository.md) (9 shared connections)
- [Case Statistics Tests](Case_Statistics_Tests.md) (7 shared connections)
- [Filter Base Abstractions](Filter_Base_Abstractions.md) (5 shared connections)
- [Casedb Repository Contracts](Casedb_Repository_Contracts.md) (4 shared connections)
- [Generic Repository Base](Generic_Repository_Base.md) (2 shared connections)
- [Column & Dimension Enums](Column_&_Dimension_Enums.md) (2 shared connections)
- [Case Statistics](Case_Statistics.md) (2 shared connections)
- [In-Memory Dict Repository](In-Memory_Dict_Repository.md) (1 shared connections)
- [Casedb Case API Models](Casedb_Case_API_Models.md) (1 shared connections)
- [Case Access Rights](Case_Access_Rights.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/domain/repository/case.py`
- `gen_epix/casedb/repositories/case_dict.py`
- `gen_epix/filter/datetime_range.py`

## Audit Trail

- EXTRACTED: 61 (92%)
- INFERRED: 5 (8%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*