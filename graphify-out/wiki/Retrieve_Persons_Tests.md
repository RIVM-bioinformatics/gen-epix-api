# Retrieve Persons Tests

> 19 nodes · cohesion 0.14

## Key Concepts

- **OmopdbTestClient** (18 connections) — `test/omopdb/omopdb_test_client.py`
- **env()** (9 connections) — `test/omopdb/integration/retrieve_persons/test_omopdb_retrieve_persons.py`
- **TestRetrievePersons** (6 connections) — `test/omopdb/integration/retrieve_persons/test_omopdb_retrieve_persons.py`
- **get_test_client()** (5 connections) — `test/omopdb/integration/build_db/test_omopdb_build.py`
- **get_test_client()** (4 connections) — `test/omopdb/integration/person_upload/test_omopdb_person_batch_upload.py`
- **get_test_client()** (4 connections) — `test/omopdb/integration/person_upload/test_omopdb_person_upload.py`
- **._load_persons()** (4 connections) — `test/omopdb/integration/retrieve_persons/test_omopdb_retrieve_persons.py`
- **fixture** (2 connections)
- **FixtureRequest** (2 connections)
- **.test_retrieve_full_persons_by_ids()** (2 connections) — `test/omopdb/integration/retrieve_persons/test_omopdb_retrieve_persons.py`
- **.test_retrieve_full_persons_by_modified_range()** (2 connections) — `test/omopdb/integration/retrieve_persons/test_omopdb_retrieve_persons.py`
- **.test_retrieve_full_persons_with_duplicate_ids()** (2 connections) — `test/omopdb/integration/retrieve_persons/test_omopdb_retrieve_persons.py`
- **Env** (1 connections)
- **fixture** (1 connections)
- **fixture** (1 connections)
- **Env** (1 connections)
- **fixture** (1 connections)
- **Return a test client configured for either DICT or SA_SQLITE demo repos. The…** (1 connections) — `test/omopdb/integration/retrieve_persons/test_omopdb_retrieve_persons.py`
- **TestClient** (1 connections)

## Relationships

- [Commondb Enums & Demo Data](Commondb_Enums_&_Demo_Data.md) (10 shared connections)
- [App Composition & Startup](App_Composition_&_Startup.md) (4 shared connections)
- [Person Upload Batch Model](Person_Upload_Batch_Model.md) (3 shared connections)
- [Integration Test Client Helpers](Integration_Test_Client_Helpers.md) (1 shared connections)
- [Endpoint Test Client](Endpoint_Test_Client.md) (1 shared connections)

## Source Files

- `test/omopdb/integration/build_db/test_omopdb_build.py`
- `test/omopdb/integration/person_upload/test_omopdb_person_batch_upload.py`
- `test/omopdb/integration/person_upload/test_omopdb_person_upload.py`
- `test/omopdb/integration/retrieve_persons/test_omopdb_retrieve_persons.py`
- `test/omopdb/omopdb_test_client.py`

## Audit Trail

- EXTRACTED: 32 (74%)
- INFERRED: 11 (26%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*