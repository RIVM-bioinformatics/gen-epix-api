# SQLAlchemy Unit of Work

> 33 nodes · cohesion 0.09

## Key Concepts

- **SAUnitOfWork** (28 connections) — `gen_epix/fastapp/repositories/sa/unit_of_work.py`
- **test_get_full_persons_by_person_ids.py** (18 connections) — `test/omopdb/unit/repositories/test_get_full_persons_by_person_ids.py`
- **_make_sa_repo()** (8 connections) — `test/omopdb/unit/repositories/test_get_full_persons_by_person_ids.py`
- **.__exit__()** (6 connections) — `gen_epix/fastapp/repositories/sa/unit_of_work.py`
- **._handle_exception()** (5 connections) — `gen_epix/fastapp/repositories/sa/unit_of_work.py`
- **_make_dict_repo()** (5 connections) — `test/omopdb/unit/repositories/test_get_full_persons_by_person_ids.py`
- **_col_mapper()** (4 connections) — `test/omopdb/unit/repositories/test_get_full_persons_by_person_ids.py`
- **Session** (4 connections)
- **_sa_session()** (4 connections) — `test/omopdb/unit/repositories/test_get_full_persons_by_person_ids.py`
- **.__init__()** (3 connections) — `gen_epix/fastapp/repositories/sa/unit_of_work.py`
- **TestDictRepositoryGetFullPersonsByPersonIds** (3 connections) — `test/omopdb/unit/repositories/test_get_full_persons_by_person_ids.py`
- **TestSARepositoryGetFullPersonsByPersonIds** (3 connections) — `test/omopdb/unit/repositories/test_get_full_persons_by_person_ids.py`
- **.test_no_person_returns_empty_list()** (3 connections) — `test/omopdb/unit/repositories/test_get_full_persons_by_person_ids.py`
- **.test_specimen_identifiers_populated()** (3 connections) — `test/omopdb/unit/repositories/test_get_full_persons_by_person_ids.py`
- **Exception** (2 connections)
- **Session** (2 connections)
- **TracebackType** (2 connections)
- **.commit()** (2 connections) — `gen_epix/fastapp/repositories/sa/unit_of_work.py`
- **.__enter__()** (2 connections) — `gen_epix/fastapp/repositories/sa/unit_of_work.py`
- **.rollback()** (2 connections) — `gen_epix/fastapp/repositories/sa/unit_of_work.py`
- **.session()** (2 connections) — `gen_epix/fastapp/repositories/sa/unit_of_work.py`
- **.test_no_specimen_yields_empty_identifiers()** (2 connections) — `test/omopdb/unit/repositories/test_get_full_persons_by_person_ids.py`
- **.test_specimen_identifiers_populated()** (2 connections) — `test/omopdb/unit/repositories/test_get_full_persons_by_person_ids.py`
- **Self** (1 connections)
- **Unit of work class wrapping the SQLAlchemy session. The context stack that can…** (1 connections) — `gen_epix/fastapp/repositories/sa/unit_of_work.py`
- *... and 8 more nodes in this community*

## Relationships

- [OMOP Repository](OMOP_Repository.md) (9 shared connections)
- [Case Domain Enums](Case_Domain_Enums.md) (4 shared connections)
- [FastApp SA Repository Core](FastApp_SA_Repository_Core.md) (2 shared connections)
- [SA Model Mapping Utils](SA_Model_Mapping_Utils.md) (2 shared connections)
- [Commondb Enums & Demo Data](Commondb_Enums_&_Demo_Data.md) (2 shared connections)
- [Casedb Case CRUD Commands](Casedb_Case_CRUD_Commands.md) (2 shared connections)
- [SQL Injection Tests](SQL_Injection_Tests.md) (1 shared connections)
- [Casedb Repository Implementations](Casedb_Repository_Implementations.md) (1 shared connections)
- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (1 shared connections)
- [Seq SA Repository](Seq_SA_Repository.md) (1 shared connections)
- [Seq Dict Repository](Seq_Dict_Repository.md) (1 shared connections)
- [Data Anonymization](Data_Anonymization.md) (1 shared connections)

## Source Files

- `gen_epix/fastapp/repositories/sa/unit_of_work.py`
- `test/omopdb/unit/repositories/test_get_full_persons_by_person_ids.py`

## Audit Trail

- EXTRACTED: 75 (96%)
- INFERRED: 3 (4%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*