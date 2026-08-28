# test_omopdb_upload.py

> 31 nodes · cohesion 0.10

## Key Concepts

- **test_omopdb_upload.py** (49 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **UploadPersonsCommand** (18 connections) — `gen_epix/omopdb/domain/command/omop.py`
- **PersonBatchUploadResult** (15 connections) — `gen_epix/omopdb/domain/model/omop/upload.py`
- **PersonValidator** (10 connections) — `gen_epix/omopdb/services/omop/person_validator.py`
- **.validate_and_transform()** (7 connections) — `gen_epix/omopdb/services/omop/person_validator.py`
- **omop_service_upload_persons()** (7 connections) — `gen_epix/omopdb/services/omop/upload.py`
- **.verify_person_content()** (7 connections) — `gen_epix/omopdb/services/omop/upload.py`
- **._get_data_issues()** (6 connections) — `gen_epix/omopdb/services/omop/person_validator.py`
- **.transform_individual_values()** (5 connections) — `gen_epix/omopdb/services/omop/person_validator.py`
- **.transform_value_pairs()** (5 connections) — `gen_epix/omopdb/services/omop/person_validator.py`
- **._get_person_validator()** (5 connections) — `gen_epix/omopdb/services/omop/upload.py`
- **.upload_persons()** (4 connections) — `gen_epix/omopdb/domain/service/omop.py`
- **.__init__()** (4 connections) — `gen_epix/omopdb/services/omop/person_validator.py`
- **.upload_persons()** (4 connections) — `gen_epix/omopdb/services/omop/service.py`
- **.upload_persons()** (4 connections) — `gen_epix/omopdb/services/remote_app.py`
- **._init_metadata()** (2 connections) — `gen_epix/omopdb/services/omop/person_validator.py`
- **UUID** (2 connections)
- **UUID** (2 connections)
- **Upload a batch of persons along with their associated data. The data are…** (1 connections) — `gen_epix/omopdb/domain/command/omop.py`
- **The result of uploading a batch of persons.** (1 connections) — `gen_epix/omopdb/domain/model/omop/upload.py`
- **Upload persons in batch.** (1 connections) — `gen_epix/omopdb/domain/service/omop.py`
- **BaseOmopService** (1 connections)
- **Validate and transform the content of the persons in batch upload command.…** (1 connections) — `gen_epix/omopdb/services/omop/person_validator.py`
- **Get references to data_issues for all persons, as a convenience for easily…** (1 connections) — `gen_epix/omopdb/services/omop/person_validator.py`
- **Validate and transform individual values.** (1 connections) — `gen_epix/omopdb/services/omop/person_validator.py`
- *... and 6 more nodes in this community*

## Relationships

- [BaseUnitOfWork](BaseUnitOfWork.md) (18 shared connections)
- [model/omop/upload.py](model-omop-upload.py.md) (8 shared connections)
- [BasePersonUploadTestCase](BasePersonUploadTestCase.md) (7 shared connections)
- [omopdb/domain/model/__init__.py](omopdb-domain-model-__init__.py.md) (6 shared connections)
- [commondb/domain/enum.py](commondb-domain-enum.py.md) (6 shared connections)
- [omop/service.py](omop-service.py.md) (6 shared connections)
- [.create_person_for_upload](create_person_for_upload.md) (4 shared connections)
- [omopdb/domain/command/__init__.py](omopdb-domain-command-__init__.py.md) (3 shared connections)
- [.create_measurement_for_upload](create_measurement_for_upload.md) (3 shared connections)
- [CrudOperation](CrudOperation.md) (3 shared connections)
- [OmopdbEndpointTestClient](OmopdbEndpointTestClient.md) (2 shared connections)
- [IdentifierForUpload](IdentifierForUpload.md) (2 shared connections)

## Source Files

- `gen_epix/omopdb/domain/command/omop.py`
- `gen_epix/omopdb/domain/model/omop/upload.py`
- `gen_epix/omopdb/domain/service/omop.py`
- `gen_epix/omopdb/services/omop/person_validator.py`
- `gen_epix/omopdb/services/omop/service.py`
- `gen_epix/omopdb/services/omop/upload.py`
- `gen_epix/omopdb/services/remote_app.py`
- `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`

## Audit Trail

- EXTRACTED: 122 (99%)
- INFERRED: 1 (1%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*