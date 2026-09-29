# Case Set CRUD Handling

> 14 nodes · cohesion 0.27

## Key Concepts

- **crud_case_set.py** (21 connections) — `gen_epix/casedb/services/case/crud_case_set.py`
- **_crud_case_set_with_abac()** (11 connections) — `gen_epix/casedb/services/case/crud_case_set.py`
- **CaseSetCrudCommand** (10 connections) — `gen_epix/casedb/domain/command/case.py`
- **case_service_crud_case_set()** (10 connections) — `gen_epix/casedb/services/case/crud_case_set.py`
- **_crud_case_set_without_abac()** (8 connections) — `gen_epix/casedb/services/case/crud_case_set.py`
- **_validate_case_set_deletion()** (8 connections) — `gen_epix/casedb/services/case/crud_case_set.py`
- **UUID** (5 connections)
- **CaseSet** (3 connections)
- **Represents a request to execute a CRUD operation on CaseSets.** (1 connections) — `gen_epix/casedb/domain/command/case.py`
- **Handle CRUD operations for case-set entities.** (1 connections) — `gen_epix/casedb/services/case/crud_case_set.py`
- **Require remove access for every collection of each requested case set. Args:…** (1 connections) — `gen_epix/casedb/services/case/crud_case_set.py`
- **Handle CRUD operations for CaseSet entities.** (1 connections) — `gen_epix/casedb/services/case/crud_case_set.py`
- **CaseSet admin command handling, no ABAC applied.** (1 connections) — `gen_epix/casedb/services/case/crud_case_set.py`
- **Handle case-set CRUD with operation-specific content rights. Reads are access-…** (1 connections) — `gen_epix/casedb/services/case/crud_case_set.py`

## Relationships

- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (7 shared connections)
- [Case CRUD Service Operations](Case_CRUD_Service_Operations.md) (7 shared connections)
- [SQLAlchemy Case Repository](SQLAlchemy_Case_Repository.md) (5 shared connections)
- [Case Type & Column Commands](Case_Type_&_Column_Commands.md) (5 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (3 shared connections)
- [Base Case Service Interface](Base_Case_Service_Interface.md) (1 shared connections)
- [Case Service Implementation](Case_Service_Implementation.md) (1 shared connections)
- [Geographic Region Commands](Geographic_Region_Commands.md) (1 shared connections)
- [Sequence File Creation](Sequence_File_Creation.md) (1 shared connections)
- [Case Access Rights ABAC](Case_Access_Rights_ABAC.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/domain/command/case.py`
- `gen_epix/casedb/services/case/crud_case_set.py`

## Audit Trail

- EXTRACTED: 49 (86%)
- INFERRED: 8 (14%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*