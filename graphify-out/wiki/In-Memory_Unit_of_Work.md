# In-Memory Unit of Work

> 7 nodes · cohesion 0.33

## Key Concepts

- **DictUnitOfWork** (12 connections) — `gen_epix/fastapp/repositories/dict/unit_of_work.py`
- **.uow()** (6 connections) — `gen_epix/fastapp/repositories/dict/repository.py`
- **dict/unit_of_work.py** (6 connections) — `gen_epix/fastapp/repositories/dict/unit_of_work.py`
- **dict/__init__.py** (5 connections) — `gen_epix/fastapp/repositories/dict/__init__.py`
- **Return a no-op unit-of-work suitable for the in-memory backend.** (1 connections) — `gen_epix/fastapp/repositories/dict/repository.py`
- **.commit()** (1 connections) — `gen_epix/fastapp/repositories/dict/unit_of_work.py`
- **.rollback()** (1 connections) — `gen_epix/fastapp/repositories/dict/unit_of_work.py`

## Relationships

- [In-Memory Dict Repository](In-Memory_Dict_Repository.md) (6 shared connections)
- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (4 shared connections)
- [Casedb Case CRUD Commands](Casedb_Case_CRUD_Commands.md) (4 shared connections)
- [SA Model Mapping Utils](SA_Model_Mapping_Utils.md) (2 shared connections)
- [Repository CRUD Base](Repository_CRUD_Base.md) (1 shared connections)
- [Fastapp CRUD Command Tests](Fastapp_CRUD_Command_Tests.md) (1 shared connections)

## Source Files

- `gen_epix/fastapp/repositories/dict/__init__.py`
- `gen_epix/fastapp/repositories/dict/repository.py`
- `gen_epix/fastapp/repositories/dict/unit_of_work.py`

## Audit Trail

- EXTRACTED: 22 (88%)
- INFERRED: 3 (12%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*