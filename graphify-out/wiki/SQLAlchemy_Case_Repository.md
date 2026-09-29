# SQLAlchemy Case Repository

> 95 nodes · cohesion 0.04

## Key Concepts

- **BaseUnitOfWork** (286 connections) — `gen_epix/fastapp/unit_of_work.py`
- **fastapp/unit_of_work.py** (54 connections) — `gen_epix/fastapp/unit_of_work.py`
- **test_get_full_persons_by_person_ids.py** (18 connections) — `test/omopdb/unit/repositories/test_get_full_persons_by_person_ids.py`
- **test_get_specimen_ids_by_cohort_ids.py** (15 connections) — `test/omopdb/unit/repositories/test_get_specimen_ids_by_cohort_ids.py`
- **BaseOmopRepository** (14 connections) — `gen_epix/omopdb/domain/repository/omop.py`
- **omop_sa.py** (14 connections) — `gen_epix/omopdb/repositories/omop_sa.py`
- **case_sa.py** (13 connections) — `gen_epix/casedb/repositories/case_sa.py`
- **sa/unit_of_work.py** (13 connections) — `gen_epix/fastapp/repositories/sa/unit_of_work.py`
- **OmopDictRepository** (13 connections) — `gen_epix/omopdb/repositories/omop_dict.py`
- **OmopSARepository** (13 connections) — `gen_epix/omopdb/repositories/omop_sa.py`
- **repository/omop.py** (12 connections) — `gen_epix/omopdb/domain/repository/omop.py`
- **omop_dict.py** (12 connections) — `gen_epix/omopdb/repositories/omop_dict.py`
- **CaseSARepository** (9 connections) — `gen_epix/casedb/repositories/case_sa.py`
- **_make_sa_repo()** (8 connections) — `test/omopdb/unit/repositories/test_get_full_persons_by_person_ids.py`
- **.retrieve_case_stats()** (6 connections) — `gen_epix/casedb/repositories/case_sa.py`
- **.__exit__()** (6 connections) — `gen_epix/fastapp/unit_of_work.py`
- **_make_sa_repo()** (6 connections) — `test/omopdb/unit/repositories/test_get_specimen_ids_by_cohort_ids.py`
- **.get_person_ids_modified_in_range()** (5 connections) — `gen_epix/omopdb/domain/repository/omop.py`
- **.get_person_ids_modified_in_range()** (5 connections) — `gen_epix/omopdb/repositories/omop_dict.py`
- **.get_person_ids_modified_in_range()** (5 connections) — `gen_epix/omopdb/repositories/omop_sa.py`
- **_make_dict_repo()** (5 connections) — `test/omopdb/unit/repositories/test_get_full_persons_by_person_ids.py`
- **_make_dict_repo()** (5 connections) — `test/omopdb/unit/repositories/test_get_specimen_ids_by_cohort_ids.py`
- **.get_full_persons_by_person_ids()** (4 connections) — `gen_epix/omopdb/domain/repository/omop.py`
- **UUID** (4 connections)
- **.get_full_persons_by_person_ids()** (4 connections) — `gen_epix/omopdb/repositories/omop_dict.py`
- *... and 70 more nodes in this community*

## Relationships

- [Case Type & Column Commands](Case_Type_&_Column_Commands.md) (30 shared connections)
- [Sequence Repository Queries](Sequence_Repository_Queries.md) (24 shared connections)
- [Case Upload Batch Mixin](Case_Upload_Batch_Mixin.md) (24 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (21 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (19 shared connections)
- [Case CRUD Service Operations](Case_CRUD_Service_Operations.md) (19 shared connections)
- [Sample Batch Upload](Sample_Batch_Upload.md) (17 shared connections)
- [Case Service Implementation](Case_Service_Implementation.md) (12 shared connections)
- [Database Session Isolation](Database_Session_Isolation.md) (11 shared connections)
- [In-Memory Dict Repository](In-Memory_Dict_Repository.md) (11 shared connections)
- [Seq Repository Queries](Seq_Repository_Queries.md) (11 shared connections)
- [Dimension CRUD Service](Dimension_CRUD_Service.md) (10 shared connections)

## Source Files

- `gen_epix/casedb/repositories/case_sa.py`
- `gen_epix/commondb/repositories/organization_dict.py`
- `gen_epix/commondb/repositories/organization_sa.py`
- `gen_epix/fastapp/repositories/sa/unit_of_work.py`
- `gen_epix/fastapp/unit_of_work.py`
- `gen_epix/omopdb/domain/repository/omop.py`
- `gen_epix/omopdb/repositories/omop_dict.py`
- `gen_epix/omopdb/repositories/omop_sa.py`
- `test/omopdb/unit/repositories/test_get_full_persons_by_person_ids.py`
- `test/omopdb/unit/repositories/test_get_specimen_ids_by_cohort_ids.py`

## Audit Trail

- EXTRACTED: 438 (83%)
- INFERRED: 87 (17%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*