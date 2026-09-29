# CRUD Argument Verification

> 9 nodes · cohesion 0.39

## Key Concepts

- **.verify_crud_args()** (16 connections) — `gen_epix/fastapp/repository.py`
- **_verify_no_obj_ids()** (4 connections) — `gen_epix/fastapp/repository.py`
- **_verify_no_objs()** (4 connections) — `gen_epix/fastapp/repository.py`
- **_verify_no_data()** (3 connections) — `gen_epix/fastapp/repository.py`
- **_verify_one_id()** (2 connections) — `gen_epix/fastapp/repository.py`
- **_verify_one_obj()** (2 connections) — `gen_epix/fastapp/repository.py`
- **_verify_some_ids()** (2 connections) — `gen_epix/fastapp/repository.py`
- **_verify_some_objs()** (2 connections) — `gen_epix/fastapp/repository.py`
- **Validate that CRUD arguments match the requested operation.** (1 connections) — `gen_epix/fastapp/repository.py`

## Relationships

- [Generic Repository Base](Generic_Repository_Base.md) (3 shared connections)
- [Domain Registry & ABAC Policies](Domain_Registry_&_ABAC_Policies.md) (2 shared connections)
- [Generic Repository CRUD](Generic_Repository_CRUD.md) (1 shared connections)
- [SQLAlchemy Repository Queries](SQLAlchemy_Repository_Queries.md) (1 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (1 shared connections)

## Source Files

- `gen_epix/fastapp/repository.py`

## Audit Trail

- EXTRACTED: 22 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*