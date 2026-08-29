# model/omop/upload.py

> 21 nodes

## Key Concepts

- **model/omop/upload.py** (25 connections) — `gen_epix/omopdb/domain/model/omop/upload.py`
- **IdentifiersMixin** (18 connections) — `gen_epix/commondb/domain/model/upload.py`
- **DataIssue** (11 connections) — `gen_epix/commondb/domain/model/upload.py`
- **MeasurementForUpload** (8 connections) — `gen_epix/omopdb/domain/model/omop/upload.py`
- **MeasurementRelationForUpload** (8 connections) — `gen_epix/omopdb/domain/model/omop/upload.py`
- **ObservationForUpload** (8 connections) — `gen_epix/omopdb/domain/model/omop/upload.py`
- **SpecimenForUpload** (8 connections) — `gen_epix/omopdb/domain/model/omop/upload.py`
- **PersonDataIssue** (7 connections) — `gen_epix/omopdb/domain/model/omop/upload.py`
- **PersonUploadResult** (6 connections) — `gen_epix/omopdb/domain/model/omop/upload.py`
- **.get_error_data_issues()** (3 connections) — `gen_epix/commondb/domain/model/upload.py`
- **PydanticBaseModel** (1 connections)
- **ParentUploadResult** (1 connections)
- **Mixin that adds identifiers fields and validation. Assumes that the inheriting…** (1 connections) — `gen_epix/commondb/domain/model/upload.py`
- **Get all data issues that are errors.** (1 connections) — `gen_epix/commondb/domain/model/upload.py`
- **Describes an issue with a single value** (1 connections) — `gen_epix/commondb/domain/model/upload.py`
- **# TODO: add other associated data types when needed** (1 connections) — `gen_epix/omopdb/domain/model/omop/upload.py`
- **The result of uploading a single person.** (1 connections) — `gen_epix/omopdb/domain/model/omop/upload.py`
- **An measurement record intended for upload. Equal to a Measurement, with…** (1 connections) — `gen_epix/omopdb/domain/model/omop/upload.py`
- **An observation record intended for upload. Equal to an Observation, with…** (1 connections) — `gen_epix/omopdb/domain/model/omop/upload.py`
- **A specimen record intended for upload. Equal to a Specimen, with additional…** (1 connections) — `gen_epix/omopdb/domain/model/omop/upload.py`
- **A measurement relation record intended for upload. Equal to a…** (1 connections) — `gen_epix/omopdb/domain/model/omop/upload.py`

## Relationships

- [omopdb/domain/model/__init__.py](omopdb-domain-model-__init__.py.md) (14 shared connections)
- [test_omopdb_upload.py](test_omopdb_upload.py.md) (8 shared connections)
- [BaseUnitOfWork](BaseUnitOfWork.md) (7 shared connections)
- [entity.py](entity.py.md) (4 shared connections)
- [BaseBatchForUpload](BaseBatchForUpload.md) (4 shared connections)
- [.create_person_for_upload](create_person_for_upload.md) (4 shared connections)
- [SeqProfileForUpload](SeqProfileForUpload.md) (3 shared connections)
- [.create_measurement_for_upload](create_measurement_for_upload.md) (3 shared connections)
- [casedb/domain/model/__init__.py](casedb-domain-model-__init__.py.md) (2 shared connections)
- [commondb/domain/model/__init__.py](commondb-domain-model-__init__.py.md) (2 shared connections)
- [ETL Log Item Base Model](ETL_Log_Item_Base_Model.md) (2 shared connections)
- [ParentUploadResult](ParentUploadResult.md) (2 shared connections)

## Source Files

- `gen_epix/commondb/domain/model/upload.py`
- `gen_epix/omopdb/domain/model/omop/upload.py`

## Audit Trail

- EXTRACTED: 88 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*