# BasePersonUploadTestCase

> 25 nodes · cohesion 0.10

## Key Concepts

- **BasePersonUploadTestCase** (30 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **scenario_ids** (9 connections)
- **.setup_method()** (8 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **Test5FieldMutability** (8 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **.test_8_person_with_n_measurements()** (8 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **.create_command_for_persons()** (7 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **Test4PersonLinks** (7 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **Test6Identifiers** (7 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **Test1PersonExistence** (6 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **Test8ParametrizedBatchSizes** (6 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **.test_5_2_1_mutable_if_empty_stored_empty_updated()** (2 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **.test_5_2_2_mutable_if_empty_stored_not_empty_new_empty()** (2 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **.test_5_2_3_mutable_if_empty_stored_not_empty_new_not_empty_fails()** (2 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **Base test case with common fixtures and utilities for person upload tests.** (1 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **Set up test fixtures.** (1 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **Create a test UploadPersonsCommand.** (1 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **Test scenarios related to person existence in repository.** (1 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **Test scenarios related to person_id links in child objects.** (1 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **Test scenarios related to field mutability for existing Person objects.** (1 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **Test 5.2.1: Mutable if empty field - stored value is empty, should succeed.** (1 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **Test 5.2.2: Mutable if empty field - stored not empty, new empty, should…** (1 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **Test 5.2.3: Mutable if empty field - stored not empty, new not empty, should…** (1 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **Test scenarios related to Identifiers for persons.** (1 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **Test upload with varying batch sizes.** (1 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **Test 8: Upload person with varying number of measurements.** (1 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`

## Relationships

- [.create_person_for_upload](create_person_for_upload.md) (23 shared connections)
- [.create_measurement_for_upload](create_measurement_for_upload.md) (10 shared connections)
- [test_omopdb_upload.py](test_omopdb_upload.py.md) (7 shared connections)
- [IdentifierForUpload](IdentifierForUpload.md) (6 shared connections)
- [ModelFieldProps](ModelFieldProps.md) (2 shared connections)
- [PersonBatchForUpload](PersonBatchForUpload.md) (2 shared connections)
- [commondb/domain/enum.py](commondb-domain-enum.py.md) (2 shared connections)
- [Role](Role.md) (1 shared connections)
- [App](App.md) (1 shared connections)
- [seqdb/domain/model/__init__.py](seqdb-domain-model-__init__.py.md) (1 shared connections)
- [BaseUnitOfWork](BaseUnitOfWork.md) (1 shared connections)

## Source Files

- `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`

## Audit Trail

- EXTRACTED: 82 (96%)
- INFERRED: 3 (4%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*