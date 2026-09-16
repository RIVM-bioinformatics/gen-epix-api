# Policy Interface

> 12 nodes · cohesion 0.18

## Key Concepts

- **.filter()** (4 connections) — `gen_epix/fastapp/model.py`
- **.get_content()** (4 connections) — `gen_epix/fastapp/model.py`
- **Command** (4 connections)
- **.is_mutable_value()** (3 connections) — `gen_epix/fastapp/model.py`
- **.get_content_return_type()** (3 connections) — `gen_epix/fastapp/model.py`
- **.is_allowed()** (3 connections) — `gen_epix/fastapp/model.py`
- **Any** (3 connections)
- **Return whether the command is allowed by this policy.** (1 connections) — `gen_epix/fastapp/model.py`
- **Return policy content associated with a command.** (1 connections) — `gen_epix/fastapp/model.py`
- **Return the type of content produced by this policy.** (1 connections) — `gen_epix/fastapp/model.py`
- **Filter a command result according to this policy.** (1 connections) — `gen_epix/fastapp/model.py`
- **Determine if a stored value for this field is mutable.** (1 connections) — `gen_epix/fastapp/model.py`

## Relationships

- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (4 shared connections)
- [Model Field Validation](Model_Field_Validation.md) (1 shared connections)

## Source Files

- `gen_epix/fastapp/model.py`

## Audit Trail

- EXTRACTED: 17 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*