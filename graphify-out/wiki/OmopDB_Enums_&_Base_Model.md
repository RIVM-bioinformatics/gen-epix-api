# OmopDB Enums & Base Model

> 60 nodes · cohesion 0.05

## Key Concepts

- **Model** (15 connections) — `gen_epix/omopdb/domain/model/base.py`
- **model_anonymizer.py** (14 connections) — `test/omopdb/test_client/model_anonymizer.py`
- **ModelAnonymizer** (13 connections) — `test/omopdb/test_client/model_anonymizer.py`
- **BaseAnonymizer** (10 connections) — `test/omopdb/test_client/model_anonymizer.py`
- **ServiceType** (9 connections) — `gen_epix/omopdb/domain/enum.py`
- **.anonymize()** (8 connections) — `test/omopdb/test_client/model_anonymizer.py`
- **omopdb/domain/model/base.py** (7 connections) — `gen_epix/omopdb/domain/model/base.py`
- **SpecimenIdsByCohortResult** (7 connections) — `gen_epix/omopdb/domain/model/omop/non_persistable.py`
- **AnonMethod** (6 connections) — `gen_epix/omopdb/domain/enum.py`
- **AnonStrictness** (6 connections) — `gen_epix/omopdb/domain/enum.py`
- **Enum** (6 connections)
- **PersonQuery** (6 connections) — `gen_epix/omopdb/domain/model/omop/non_persistable.py`
- **.create_anonymization_map()** (6 connections) — `test/omopdb/test_client/model_anonymizer.py`
- **.__init__()** (6 connections) — `test/omopdb/test_client/model_anonymizer.py`
- **test_omopdb_matches_spec.py** (6 connections) — `test/omopdb/unit/domain/test_omopdb_matches_spec.py`
- **Collection** (5 connections)
- **.anonymize_categorical()** (5 connections) — `test/omopdb/test_client/model_anonymizer.py`
- **.anonymize_dates()** (5 connections) — `test/omopdb/test_client/model_anonymizer.py`
- **TestOmopSpecification** (5 connections) — `test/omopdb/unit/domain/test_omopdb_matches_spec.py`
- **._validate_some_criteria()** (4 connections) — `gen_epix/omopdb/domain/model/omop/non_persistable.py`
- **.anonymize_ints()** (4 connections) — `test/omopdb/test_client/model_anonymizer.py`
- **.anonymize_uuids()** (4 connections) — `test/omopdb/test_client/model_anonymizer.py`
- **Any** (4 connections)
- **RepositoryType** (3 connections) — `gen_epix/omopdb/domain/enum.py`
- **.retrieve_specimen_ids_by_cohort_ids()** (3 connections) — `gen_epix/omopdb/services/client.py`
- *... and 35 more nodes in this community*

## Relationships

- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (9 shared connections)
- [OMOP Clinical Data Models](OMOP_Clinical_Data_Models.md) (9 shared connections)
- [SQLAlchemy Case Repository](SQLAlchemy_Case_Repository.md) (2 shared connections)
- [Audit Timestamp Model Tests](Audit_Timestamp_Model_Tests.md) (2 shared connections)
- [Domain & Entity Registry](Domain_&_Entity_Registry.md) (2 shared connections)
- [Geographic Region Commands](Geographic_Region_Commands.md) (2 shared connections)
- [Generic Repository Base](Generic_Repository_Base.md) (2 shared connections)
- [Case Upload Batch Models](Case_Upload_Batch_Models.md) (1 shared connections)
- [Commondb Base Models](Commondb_Base_Models.md) (1 shared connections)
- [User & Person Commands](User_&_Person_Commands.md) (1 shared connections)
- [OMOP DB HTTP Client](OMOP_DB_HTTP_Client.md) (1 shared connections)
- [Domain Registry & ABAC Policies](Domain_Registry_&_ABAC_Policies.md) (1 shared connections)

## Source Files

- `gen_epix/omopdb/domain/enum.py`
- `gen_epix/omopdb/domain/model/base.py`
- `gen_epix/omopdb/domain/model/omop/non_persistable.py`
- `gen_epix/omopdb/services/client.py`
- `test/omopdb/test_client/model_anonymizer.py`
- `test/omopdb/unit/domain/test_omopdb_matches_spec.py`

## Audit Trail

- EXTRACTED: 113 (92%)
- INFERRED: 10 (8%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*