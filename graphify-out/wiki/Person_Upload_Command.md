# Person Upload Command

> 23 nodes · cohesion 0.14

## Key Concepts

- **UploadPersonsCommand** (18 connections) — `gen_epix/omopdb/domain/command/omop.py`
- **PersonBatchUploadResult** (15 connections) — `gen_epix/omopdb/domain/model/omop/upload.py`
- **PersonValidator** (10 connections) — `gen_epix/omopdb/services/omop/person_validator.py`
- **PersonDataIssue** (7 connections) — `gen_epix/omopdb/domain/model/omop/upload.py`
- **.validate_and_transform()** (7 connections) — `gen_epix/omopdb/services/omop/person_validator.py`
- **._get_data_issues()** (6 connections) — `gen_epix/omopdb/services/omop/person_validator.py`
- **.transform_individual_values()** (5 connections) — `gen_epix/omopdb/services/omop/person_validator.py`
- **.transform_value_pairs()** (5 connections) — `gen_epix/omopdb/services/omop/person_validator.py`
- **.upload_persons()** (4 connections) — `gen_epix/omopdb/domain/service/omop.py`
- **.__init__()** (4 connections) — `gen_epix/omopdb/services/omop/person_validator.py`
- **.upload_persons()** (4 connections) — `gen_epix/omopdb/services/omop/service.py`
- **.upload_persons()** (4 connections) — `gen_epix/omopdb/services/remote_app.py`
- **._init_metadata()** (2 connections) — `gen_epix/omopdb/services/omop/person_validator.py`
- **UUID** (2 connections)
- **Upload a batch of persons along with their associated data. The data are…** (1 connections) — `gen_epix/omopdb/domain/command/omop.py`
- **The result of uploading a batch of persons.** (1 connections) — `gen_epix/omopdb/domain/model/omop/upload.py`
- **Upload persons in batch.** (1 connections) — `gen_epix/omopdb/domain/service/omop.py`
- **BaseOmopService** (1 connections)
- **Validate and transform the content of the persons in batch upload command.…** (1 connections) — `gen_epix/omopdb/services/omop/person_validator.py`
- **Get references to data_issues for all persons, as a convenience for easily…** (1 connections) — `gen_epix/omopdb/services/omop/person_validator.py`
- **Validate and transform individual values.** (1 connections) — `gen_epix/omopdb/services/omop/person_validator.py`
- **Validate and transform pairs of values.** (1 connections) — `gen_epix/omopdb/services/omop/person_validator.py`
- **Upload a batch of persons.** (1 connections) — `gen_epix/omopdb/services/remote_app.py`

## Relationships

- [Seqdb Upload Batch Processing](Seqdb_Upload_Batch_Processing.md) (12 shared connections)
- [Omopdb Upload Test Suite](Omopdb_Upload_Test_Suite.md) (7 shared connections)
- [OMOP Domain CRUD Commands](OMOP_Domain_CRUD_Commands.md) (4 shared connections)
- [Base Model & Identifiers](Base_Model_&_Identifiers.md) (4 shared connections)
- [Endpoint Test Client](Endpoint_Test_Client.md) (1 shared connections)
- [Commondb Enums & Demo Data](Commondb_Enums_&_Demo_Data.md) (1 shared connections)
- [Commondb Organization Domain Models](Commondb_Organization_Domain_Models.md) (1 shared connections)
- [OMOP Person/Specimen Retrieval](OMOP_Person-Specimen_Retrieval.md) (1 shared connections)
- [Omopdb Remote App Client](Omopdb_Remote_App_Client.md) (1 shared connections)

## Source Files

- `gen_epix/omopdb/domain/command/omop.py`
- `gen_epix/omopdb/domain/model/omop/upload.py`
- `gen_epix/omopdb/domain/service/omop.py`
- `gen_epix/omopdb/services/omop/person_validator.py`
- `gen_epix/omopdb/services/omop/service.py`
- `gen_epix/omopdb/services/remote_app.py`

## Audit Trail

- EXTRACTED: 66 (99%)
- INFERRED: 1 (1%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*