# Person Upload Batch Model

> 60 nodes · cohesion 0.06

## Key Concepts

- **PersonBatchForUpload** (28 connections) — `gen_epix/omopdb/domain/model/omop/upload.py`
- **PersonForUpload** (19 connections) — `gen_epix/omopdb/domain/model/omop/upload.py`
- **_make_person()** (12 connections) — `test/omopdb/integration/person_upload/test_omopdb_person_batch_upload.py`
- **Env** (11 connections)
- **TestPersonBatchUploadHappyPath** (11 connections) — `test/omopdb/integration/person_upload/test_omopdb_person_batch_upload.py`
- **.upload_summary()** (10 connections) — `gen_epix/omopdb/domain/model/omop/upload.py`
- **TestPersonBatchUploadFailureModes** (7 connections) — `test/omopdb/integration/person_upload/test_omopdb_person_batch_upload.py`
- **.test_upload_person_twice_with_on_exists_update_returns_updated()** (7 connections) — `test/omopdb/integration/person_upload/test_omopdb_person_batch_upload.py`
- **.test_on_exists_error_default_returns_failed()** (6 connections) — `test/omopdb/integration/person_upload/test_omopdb_person_batch_upload.py`
- **.test_on_new_error_returns_failed()** (6 connections) — `test/omopdb/integration/person_upload/test_omopdb_person_batch_upload.py`
- **.test_on_exists_skip_returns_skipped()** (6 connections) — `test/omopdb/integration/person_upload/test_omopdb_person_batch_upload.py`
- **.test_on_new_skip_returns_skipped()** (6 connections) — `test/omopdb/integration/person_upload/test_omopdb_person_batch_upload.py`
- **.test_upload_multiple_persons_returns_created()** (6 connections) — `test/omopdb/integration/person_upload/test_omopdb_person_batch_upload.py`
- **.test_upload_single_person_returns_created()** (6 connections) — `test/omopdb/integration/person_upload/test_omopdb_person_batch_upload.py`
- **.test_verify_only_does_not_persist()** (6 connections) — `test/omopdb/integration/person_upload/test_omopdb_person_batch_upload.py`
- **.test_malformed_body_returns_422()** (4 connections) — `test/omopdb/integration/person_upload/test_omopdb_person_batch_upload.py`
- **.test_upload_empty_batch_returns_skipped()** (4 connections) — `test/omopdb/integration/person_upload/test_omopdb_person_batch_upload.py`
- **.has_measurements()** (3 connections) — `gen_epix/omopdb/domain/model/omop/upload.py`
- **.has_observations()** (3 connections) — `gen_epix/omopdb/domain/model/omop/upload.py`
- **.has_specimens()** (3 connections) — `gen_epix/omopdb/domain/model/omop/upload.py`
- **.measurement_distribution()** (3 connections) — `gen_epix/omopdb/domain/model/omop/upload.py`
- **.observation_distribution()** (3 connections) — `gen_epix/omopdb/domain/model/omop/upload.py`
- **.specimen_distribution()** (3 connections) — `gen_epix/omopdb/domain/model/omop/upload.py`
- **.total_measurements()** (3 connections) — `gen_epix/omopdb/domain/model/omop/upload.py`
- **.total_observations()** (3 connections) — `gen_epix/omopdb/domain/model/omop/upload.py`
- *... and 35 more nodes in this community*

## Relationships

- [Omopdb Upload Test Suite](Omopdb_Upload_Test_Suite.md) (9 shared connections)
- [Base Model & Identifiers](Base_Model_&_Identifiers.md) (5 shared connections)
- [Commondb Enums & Demo Data](Commondb_Enums_&_Demo_Data.md) (5 shared connections)
- [Retrieve Persons Tests](Retrieve_Persons_Tests.md) (3 shared connections)
- [Case Upload Batch Model](Case_Upload_Batch_Model.md) (1 shared connections)

## Source Files

- `gen_epix/omopdb/domain/model/omop/upload.py`
- `test/omopdb/integration/person_upload/test_omopdb_person_batch_upload.py`

## Audit Trail

- EXTRACTED: 120 (98%)
- INFERRED: 2 (2%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*