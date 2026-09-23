# Case ID Validation

> 8 nodes · cohesion 0.32

## Key Concepts

- **UUID** (4 connections)
- **._validate_case_ids()** (4 connections) — `gen_epix/casedb/domain/command/case.py`
- **._validate_case_ids()** (4 connections) — `gen_epix/casedb/domain/command/case.py`
- **._validate_case_set_ids()** (4 connections) — `gen_epix/casedb/domain/command/case.py`
- **field_validator** (3 connections)
- **Ensure the requested case IDs are unique.** (1 connections) — `gen_epix/casedb/domain/command/case.py`
- **Ensure the case IDs used for access lookup are unique.** (1 connections) — `gen_epix/casedb/domain/command/case.py`
- **Ensure the case-set IDs used for access lookup are unique.** (1 connections) — `gen_epix/casedb/domain/command/case.py`

## Relationships

- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (3 shared connections)
- [Case Access Rights](Case_Access_Rights.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/domain/command/case.py`

## Audit Trail

- EXTRACTED: 13 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*