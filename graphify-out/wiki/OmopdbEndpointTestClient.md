# OmopdbEndpointTestClient

> 20 nodes

## Key Concepts

- **OmopdbEndpointTestClient** (11 connections) — `test/omopdb/omopdb_endpoint_test_client.py`
- **RetrievePersonsByQueryCommand** (9 connections) — `gen_epix/omopdb/domain/command/omop.py`
- **BaseOmopService** (9 connections) — `gen_epix/omopdb/domain/service/omop.py`
- **.handle_update_user_own_organization()** (5 connections) — `test/omopdb/omopdb_endpoint_test_client.py`
- **Any** (5 connections)
- **.retrieve_persons_by_id()** (4 connections) — `gen_epix/omopdb/domain/service/omop.py`
- **.retrieve_persons_by_query()** (4 connections) — `gen_epix/omopdb/domain/service/omop.py`
- **.retrieve_specimen_ids_by_cohort_ids()** (4 connections) — `gen_epix/omopdb/domain/service/omop.py`
- **.handle_retrieve_person_ids_by_query()** (4 connections) — `test/omopdb/omopdb_endpoint_test_client.py`
- **.handle_retrieve_persons_by_id()** (4 connections) — `test/omopdb/omopdb_endpoint_test_client.py`
- **.handle_upload_persons()** (4 connections) — `test/omopdb/omopdb_endpoint_test_client.py`
- **.__init__()** (4 connections) — `test/omopdb/omopdb_endpoint_test_client.py`
- **Response** (4 connections)
- **FastAPI** (2 connections)
- **.register_handlers()** (1 connections) — `gen_epix/omopdb/domain/service/omop.py`
- **App** (1 connections)
- **Retrieve person IDs based on a query. These IDs can then be used to retrieve…** (1 connections) — `gen_epix/omopdb/domain/command/omop.py`
- **Retrieve persons by their IDs.** (1 connections) — `gen_epix/omopdb/domain/service/omop.py`
- **Retrieve persons matching query criteria.** (1 connections) — `gen_epix/omopdb/domain/service/omop.py`
- **Retrieve specimen IDs grouped by cohort ID.** (1 connections) — `gen_epix/omopdb/domain/service/omop.py`

## Relationships

- [omopdb/domain/command/__init__.py](omopdb-domain-command-__init__.py.md) (6 shared connections)
- [omop/service.py](omop-service.py.md) (3 shared connections)
- [AppCfg](AppCfg.md) (3 shared connections)
- [api/case.py](api-case.py.md) (3 shared connections)
- [omopdb/domain/model/__init__.py](omopdb-domain-model-__init__.py.md) (3 shared connections)
- [test_omopdb_upload.py](test_omopdb_upload.py.md) (2 shared connections)
- [OmopdbRemoteApp](OmopdbRemoteApp.md) (1 shared connections)
- [services/user_manager.py](services-user_manager.py.md) (1 shared connections)
- [test_get_full_persons_by_person_ids.py](test_get_full_persons_by_person_ids.py.md) (1 shared connections)
- [casedb/domain/enum.py](casedb-domain-enum.py.md) (1 shared connections)
- [EndpointTestClient](EndpointTestClient.md) (1 shared connections)
- [App](App.md) (1 shared connections)

## Source Files

- `gen_epix/omopdb/domain/command/omop.py`
- `gen_epix/omopdb/domain/service/omop.py`
- `test/omopdb/omopdb_endpoint_test_client.py`

## Audit Trail

- EXTRACTED: 50 (94%)
- INFERRED: 3 (6%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*