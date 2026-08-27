# OMOP Repository

> 44 nodes · cohesion 0.07

## Key Concepts

- **omop_sa.py** (15 connections) — `gen_epix/omopdb/repositories/omop_sa.py`
- **test_get_specimen_ids_by_cohort_ids.py** (15 connections) — `test/omopdb/unit/repositories/test_get_specimen_ids_by_cohort_ids.py`
- **omop_dict.py** (12 connections) — `gen_epix/omopdb/repositories/omop_dict.py`
- **repository/omop.py** (11 connections) — `gen_epix/omopdb/domain/repository/omop.py`
- **BaseOmopRepository** (11 connections) — `gen_epix/omopdb/domain/repository/omop.py`
- **OmopDictRepository** (11 connections) — `gen_epix/omopdb/repositories/omop_dict.py`
- **OmopSARepository** (11 connections) — `gen_epix/omopdb/repositories/omop_sa.py`
- **service/omop.py** (9 connections) — `gen_epix/omopdb/domain/service/omop.py`
- **_make_sa_repo()** (6 connections) — `test/omopdb/unit/repositories/test_get_specimen_ids_by_cohort_ids.py`
- **.get_person_ids_modified_in_range()** (5 connections) — `gen_epix/omopdb/domain/repository/omop.py`
- **.get_person_ids_modified_in_range()** (5 connections) — `gen_epix/omopdb/repositories/omop_dict.py`
- **_make_dict_repo()** (5 connections) — `test/omopdb/unit/repositories/test_get_specimen_ids_by_cohort_ids.py`
- **.get_full_persons_by_person_ids()** (4 connections) — `gen_epix/omopdb/domain/repository/omop.py`
- **UUID** (4 connections)
- **.get_full_persons_by_person_ids()** (4 connections) — `gen_epix/omopdb/repositories/omop_dict.py`
- **UUID** (4 connections)
- **.get_person_ids_modified_in_range()** (4 connections) — `gen_epix/omopdb/repositories/omop_sa.py`
- **UUID** (4 connections)
- **_sa_session()** (4 connections) — `test/omopdb/unit/repositories/test_get_specimen_ids_by_cohort_ids.py`
- **.get_specimen_ids_by_cohort_ids()** (3 connections) — `gen_epix/omopdb/domain/repository/omop.py`
- **.get_specimen_ids_by_cohort_ids()** (3 connections) — `gen_epix/omopdb/repositories/omop_dict.py`
- **.get_full_persons_by_person_ids()** (3 connections) — `gen_epix/omopdb/repositories/omop_sa.py`
- **.get_specimen_ids_by_cohort_ids()** (3 connections) — `gen_epix/omopdb/repositories/omop_sa.py`
- **Session** (3 connections)
- **TestDictRepositoryGetSpecimenIdsByCohortIds** (3 connections) — `test/omopdb/unit/repositories/test_get_specimen_ids_by_cohort_ids.py`
- *... and 19 more nodes in this community*

## Relationships

- [Casedb Case CRUD Commands](Casedb_Case_CRUD_Commands.md) (9 shared connections)
- [SQLAlchemy Unit of Work](SQLAlchemy_Unit_of_Work.md) (9 shared connections)
- [Base Model & Identifiers](Base_Model_&_Identifiers.md) (8 shared connections)
- [Casedb Repository Implementations](Casedb_Repository_Implementations.md) (6 shared connections)
- [OMOP SQLAlchemy Models](OMOP_SQLAlchemy_Models.md) (3 shared connections)
- [Repository Association Handling](Repository_Association_Handling.md) (2 shared connections)
- [Commondb Enums & Demo Data](Commondb_Enums_&_Demo_Data.md) (2 shared connections)
- [In-Memory Dict Repository](In-Memory_Dict_Repository.md) (2 shared connections)
- [FastApp SA Repository Core](FastApp_SA_Repository_Core.md) (2 shared connections)
- [Organization Service](Organization_Service.md) (1 shared connections)
- [Base Service Class](Base_Service_Class.md) (1 shared connections)
- [Data Anonymization](Data_Anonymization.md) (1 shared connections)

## Source Files

- `gen_epix/omopdb/domain/repository/omop.py`
- `gen_epix/omopdb/domain/service/omop.py`
- `gen_epix/omopdb/repositories/omop_dict.py`
- `gen_epix/omopdb/repositories/omop_sa.py`
- `test/omopdb/unit/repositories/test_get_specimen_ids_by_cohort_ids.py`

## Audit Trail

- EXTRACTED: 115 (97%)
- INFERRED: 4 (3%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*