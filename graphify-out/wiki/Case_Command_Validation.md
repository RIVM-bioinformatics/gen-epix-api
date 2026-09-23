# Case Command Validation

> 6 nodes · cohesion 0.40

## Key Concepts

- **._validate_state()** (4 connections) — `gen_epix/casedb/domain/command/case.py`
- **._validate_cases()** (4 connections) — `gen_epix/casedb/domain/command/case.py`
- **model_validator** (2 connections)
- **Self** (2 connections)
- **Ensure every supplied case belongs to the command's case type.** (1 connections) — `gen_epix/casedb/domain/command/case.py`
- **Remove the creating data collection from additional associations.** (1 connections) — `gen_epix/casedb/domain/command/case.py`

## Relationships

- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (2 shared connections)

## Source Files

- `gen_epix/casedb/domain/command/case.py`

## Audit Trail

- EXTRACTED: 8 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*