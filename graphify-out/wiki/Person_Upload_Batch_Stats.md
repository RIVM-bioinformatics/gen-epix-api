# Person Upload Batch Stats

> 69 nodes · cohesion 0.05

## Key Concepts

- **OmopdbTestClient** (30 connections) — `test/omopdb/omopdb_test_client.py`
- **PersonBatchForUpload** (25 connections) — `gen_epix/omopdb/domain/model/omop/upload.py`
- **TestPersonBatchUploadHappyPath** (13 connections) — `test/omopdb/integration/person_upload/test_omopdb_person_batch_upload.py`
- **_make_person()** (11 connections) — `test/omopdb/integration/person_upload/test_omopdb_person_batch_upload.py`
- **.upload_summary()** (10 connections) — `gen_epix/omopdb/domain/model/omop/upload.py`
- **TestPersonBatchUploadFailureModes** (9 connections) — `test/omopdb/integration/person_upload/test_omopdb_person_batch_upload.py`
- **env()** (9 connections) — `test/omopdb/integration/retrieve_persons/test_omopdb_retrieve_persons.py`
- **.test_upload_person_twice_with_on_exists_update_returns_updated()** (7 connections) — `test/omopdb/integration/person_upload/test_omopdb_person_batch_upload.py`
- **TestRetrievePersons** (7 connections) — `test/omopdb/integration/retrieve_persons/test_omopdb_retrieve_persons.py`
- **.test_on_exists_error_default_returns_failed()** (6 connections) — `test/omopdb/integration/person_upload/test_omopdb_person_batch_upload.py`
- **.test_on_new_error_returns_failed()** (6 connections) — `test/omopdb/integration/person_upload/test_omopdb_person_batch_upload.py`
- **.test_on_exists_skip_returns_skipped()** (6 connections) — `test/omopdb/integration/person_upload/test_omopdb_person_batch_upload.py`
- **.test_on_new_skip_returns_skipped()** (6 connections) — `test/omopdb/integration/person_upload/test_omopdb_person_batch_upload.py`
- **.test_upload_multiple_persons_returns_created()** (6 connections) — `test/omopdb/integration/person_upload/test_omopdb_person_batch_upload.py`
- **.test_upload_single_person_returns_created()** (6 connections) — `test/omopdb/integration/person_upload/test_omopdb_person_batch_upload.py`
- **.test_verify_only_does_not_persist()** (6 connections) — `test/omopdb/integration/person_upload/test_omopdb_person_batch_upload.py`
- **TestContent** (4 connections) — `test/omopdb/integration/content/test_omopdb_content.py`
- **.test_malformed_body_returns_422()** (4 connections) — `test/omopdb/integration/person_upload/test_omopdb_person_batch_upload.py`
- **.test_upload_empty_batch_returns_skipped()** (4 connections) — `test/omopdb/integration/person_upload/test_omopdb_person_batch_upload.py`
- **._load_persons()** (4 connections) — `test/omopdb/integration/retrieve_persons/test_omopdb_retrieve_persons.py`
- **.has_measurements()** (3 connections) — `gen_epix/omopdb/domain/model/omop/upload.py`
- **.has_observations()** (3 connections) — `gen_epix/omopdb/domain/model/omop/upload.py`
- **.has_specimens()** (3 connections) — `gen_epix/omopdb/domain/model/omop/upload.py`
- **.measurement_distribution()** (3 connections) — `gen_epix/omopdb/domain/model/omop/upload.py`
- **.observation_distribution()** (3 connections) — `gen_epix/omopdb/domain/model/omop/upload.py`
- *... and 44 more nodes in this community*

## Relationships

- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (16 shared connections)
- [Upload Identifier Models](Upload_Identifier_Models.md) (9 shared connections)
- [Sample Batch Upload](Sample_Batch_Upload.md) (4 shared connections)
- [FastAPI App Composition](FastAPI_App_Composition.md) (3 shared connections)
- [Case Upload Batch Models](Case_Upload_Batch_Models.md) (2 shared connections)
- [OMOP Clinical Data Models](OMOP_Clinical_Data_Models.md) (1 shared connections)
- [SeqDB Demo Content Test](SeqDB_Demo_Content_Test.md) (1 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (1 shared connections)
- [Integration Test Client](Integration_Test_Client.md) (1 shared connections)

## Source Files

- `gen_epix/omopdb/domain/model/omop/upload.py`
- `test/omopdb/integration/content/test_omopdb_content.py`
- `test/omopdb/integration/person_upload/test_omopdb_person_batch_upload.py`
- `test/omopdb/integration/retrieve_persons/test_omopdb_retrieve_persons.py`
- `test/omopdb/omopdb_test_client.py`

## Audit Trail

- EXTRACTED: 115 (78%)
- INFERRED: 33 (22%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*