# Case Identifier CRUD

> 13 nodes · cohesion 0.27

## Key Concepts

- **crud_case_identifier.py** (16 connections) — `gen_epix/casedb/services/case/crud_case_identifier.py`
- **case_service_crud_case_identifier()** (10 connections) — `gen_epix/casedb/services/case/crud_case_identifier.py`
- **CaseIdentifierCrudCommand** (9 connections) — `gen_epix/casedb/domain/command/case.py`
- **_crud_case_identifier_with_abac()** (9 connections) — `gen_epix/casedb/services/case/crud_case_identifier.py`
- **_crud_case_identifier_without_abac()** (8 connections) — `gen_epix/casedb/services/case/crud_case_identifier.py`
- **UUID** (4 connections)
- **CaseIdentifier** (3 connections)
- **Represents a request to execute a CRUD operation on CaseIdentifiers.** (1 connections) — `gen_epix/casedb/domain/command/case.py`
- **Handle case-identifier CRUD with admin bypass and user restrictions.** (1 connections) — `gen_epix/casedb/services/case/crud_case_identifier.py`
- **# TODO: Implement the complex ABAC logic from the main crud.py file** (1 connections) — `gen_epix/casedb/services/case/crud_case_identifier.py`
- **Handle CRUD operations for CaseIdentifier entities.** (1 connections) — `gen_epix/casedb/services/case/crud_case_identifier.py`
- **CaseIdentifier user command handling, no ABAC applied.** (1 connections) — `gen_epix/casedb/services/case/crud_case_identifier.py`
- **Handle a case-identifier command subject to current user restrictions. Commands…** (1 connections) — `gen_epix/casedb/services/case/crud_case_identifier.py`

## Relationships

- [Case CRUD Service Operations](Case_CRUD_Service_Operations.md) (7 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (4 shared connections)
- [SQLAlchemy Case Repository](SQLAlchemy_Case_Repository.md) (4 shared connections)
- [Case Type & Column Commands](Case_Type_&_Column_Commands.md) (4 shared connections)
- [Base Case Service Interface](Base_Case_Service_Interface.md) (1 shared connections)
- [Case Service Implementation](Case_Service_Implementation.md) (1 shared connections)
- [Geographic Region Commands](Geographic_Region_Commands.md) (1 shared connections)
- [Sequence File Creation](Sequence_File_Creation.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/domain/command/case.py`
- `gen_epix/casedb/services/case/crud_case_identifier.py`

## Audit Trail

- EXTRACTED: 39 (89%)
- INFERRED: 5 (11%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*