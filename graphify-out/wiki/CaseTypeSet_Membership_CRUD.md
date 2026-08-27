# CaseTypeSet Membership CRUD

> 14 nodes · cohesion 0.23

## Key Concepts

- **case_service_crud_case_type_set_member()** (11 connections) — `gen_epix/casedb/services/case/crud_case_type_set_member.py`
- **_crud_case_type_set_member_with_abac()** (10 connections) — `gen_epix/casedb/services/case/crud_case_type_set_member.py`
- **CaseTypeSetMemberCrudCommand** (9 connections) — `gen_epix/casedb/domain/command/case.py`
- **_crud_case_type_set_member_without_abac()** (9 connections) — `gen_epix/casedb/services/case/crud_case_type_set_member.py`
- **.crud_case_type_set_member()** (6 connections) — `gen_epix/casedb/services/case/service.py`
- **UUID** (4 connections)
- **BaseCaseService** (3 connections)
- **CaseTypeSetMember** (3 connections)
- **Manage which CaseTypes belong to a case-type set.** (1 connections) — `gen_epix/casedb/domain/command/case.py`
- **Handle CRUD operations for CaseTypeSetMember entities.** (1 connections) — `gen_epix/casedb/services/case/crud_case_type_set_member.py`
- **CaseTypeSetMember admin command handling, no ABAC applied.** (1 connections) — `gen_epix/casedb/services/case/crud_case_type_set_member.py`
- **CaseTypeSetMember user command handling, ABAC applied.** (1 connections) — `gen_epix/casedb/services/case/crud_case_type_set_member.py`
- **CaseTypeSetMember** (1 connections)
- **Handle CRUD operations for CaseTypeSetMember entities.** (1 connections) — `gen_epix/casedb/services/case/service.py`

## Relationships

- [Casedb Case CRUD Commands](Casedb_Case_CRUD_Commands.md) (13 shared connections)
- [Casedb Domain CRUD Commands](Casedb_Domain_CRUD_Commands.md) (3 shared connections)
- [Casedb Case Service](Casedb_Case_Service.md) (2 shared connections)
- [Case Service CRUD](Case_Service_CRUD.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/domain/command/case.py`
- `gen_epix/casedb/services/case/crud_case_type_set_member.py`
- `gen_epix/casedb/services/case/service.py`

## Audit Trail

- EXTRACTED: 37 (92%)
- INFERRED: 3 (8%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*