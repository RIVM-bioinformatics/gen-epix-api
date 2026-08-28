# SAUnitOfWork

> 15 nodes · cohesion 0.19

## Key Concepts

- **SAUnitOfWork** (25 connections) — `gen_epix/fastapp/repositories/sa/unit_of_work.py`
- **.__exit__()** (6 connections) — `gen_epix/fastapp/repositories/sa/unit_of_work.py`
- **._handle_exception()** (5 connections) — `gen_epix/fastapp/repositories/sa/unit_of_work.py`
- **.__init__()** (3 connections) — `gen_epix/fastapp/repositories/sa/unit_of_work.py`
- **Exception** (2 connections)
- **Session** (2 connections)
- **TracebackType** (2 connections)
- **.commit()** (2 connections) — `gen_epix/fastapp/repositories/sa/unit_of_work.py`
- **.__enter__()** (2 connections) — `gen_epix/fastapp/repositories/sa/unit_of_work.py`
- **.rollback()** (2 connections) — `gen_epix/fastapp/repositories/sa/unit_of_work.py`
- **.session()** (2 connections) — `gen_epix/fastapp/repositories/sa/unit_of_work.py`
- **Self** (1 connections)
- **Unit of work class wrapping the SQLAlchemy session. The context stack that can…** (1 connections) — `gen_epix/fastapp/repositories/sa/unit_of_work.py`
- **Handle exceptions raised during a unit of work, converting them into a domain…** (1 connections) — `gen_epix/fastapp/repositories/sa/unit_of_work.py`
- **.flush()** (1 connections) — `gen_epix/fastapp/repositories/sa/unit_of_work.py`

## Relationships

- [test_get_full_persons_by_person_ids.py](test_get_full_persons_by_person_ids.py.md) (3 shared connections)
- [test_get_specimen_ids_by_cohort_ids.py](test_get_specimen_ids_by_cohort_ids.py.md) (2 shared connections)
- [casedb/repositories/__init__.py](casedb-repositories-__init__.py.md) (2 shared connections)
- [sa/util.py](sa-util.py.md) (2 shared connections)
- [BaseUnitOfWork](BaseUnitOfWork.md) (2 shared connections)
- [TestSQLInjection](TestSQLInjection.md) (1 shared connections)
- [DatetimeRangeFilter](DatetimeRangeFilter.md) (1 shared connections)
- [CrudOperation](CrudOperation.md) (1 shared connections)
- [SeqSARepository](SeqSARepository.md) (1 shared connections)
- [commondb/domain/enum.py](commondb-domain-enum.py.md) (1 shared connections)
- [seqdb_test_client.py](seqdb_test_client.py.md) (1 shared connections)

## Source Files

- `gen_epix/fastapp/repositories/sa/unit_of_work.py`

## Audit Trail

- EXTRACTED: 37 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*