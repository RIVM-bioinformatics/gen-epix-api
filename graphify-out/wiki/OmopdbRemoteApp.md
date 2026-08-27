# OmopdbRemoteApp

> 19 nodes · cohesion 0.13

## Key Concepts

- **OmopdbRemoteApp** (12 connections) — `gen_epix/omopdb/services/remote_app.py`
- **test_omopdb_remote_app.py** (11 connections) — `test/omopdb/unit/services/test_omopdb_remote_app.py`
- **_make_app()** (5 connections) — `test/omopdb/unit/services/test_omopdb_remote_app.py`
- **.retrieve_persons_by_id()** (4 connections) — `gen_epix/omopdb/services/remote_app.py`
- **.retrieve_persons_by_query()** (4 connections) — `gen_epix/omopdb/services/remote_app.py`
- **.retrieve_specimen_ids_by_cohort_ids()** (4 connections) — `gen_epix/omopdb/services/remote_app.py`
- **_fake_app_init()** (4 connections) — `test/omopdb/unit/services/test_omopdb_remote_app.py`
- **.__init__()** (3 connections) — `gen_epix/omopdb/services/remote_app.py`
- **.setup_method()** (3 connections) — `test/commondb/unit/remote_app/test_commondb_remote_app.py`
- **.setup_method()** (3 connections) — `test/fastapp/unit/test_fastapp_remote_app.py`
- **test_registers_person_retrieval_routes_and_handlers()** (2 connections) — `test/omopdb/unit/services/test_omopdb_remote_app.py`
- **test_retrieve_persons_by_query_posts_query_body()** (2 connections) — `test/omopdb/unit/services/test_omopdb_remote_app.py`
- **Any** (1 connections)
- **Retrieve specimen IDs for the given cohort IDs.** (1 connections) — `gen_epix/omopdb/services/remote_app.py`
- **Remote app client for the omopdb service.** (1 connections) — `gen_epix/omopdb/services/remote_app.py`
- **Register all omopdb routes and command handlers.** (1 connections) — `gen_epix/omopdb/services/remote_app.py`
- **Retrieve persons matching the given query.** (1 connections) — `gen_epix/omopdb/services/remote_app.py`
- **Retrieve full person records by their IDs.** (1 connections) — `gen_epix/omopdb/services/remote_app.py`
- **Set up test fixtures by mocking dependencies to avoid side effects.** (1 connections) — `test/commondb/unit/remote_app/test_commondb_remote_app.py`

## Relationships

- [CrudOperation](CrudOperation.md) (7 shared connections)
- [omopdb/domain/model/__init__.py](omopdb-domain-model-__init__.py.md) (4 shared connections)
- [omopdb/domain/command/__init__.py](omopdb-domain-command-__init__.py.md) (3 shared connections)
- [CommondbRemoteApp](CommondbRemoteApp.md) (1 shared connections)
- [test_omopdb_upload.py](test_omopdb_upload.py.md) (1 shared connections)
- [OmopdbEndpointTestClient](OmopdbEndpointTestClient.md) (1 shared connections)
- [BaseCommondbRemoteAppTestCase](BaseCommondbRemoteAppTestCase.md) (1 shared connections)
- [RemoteApp](RemoteApp.md) (1 shared connections)
- [DummyCmd](DummyCmd.md) (1 shared connections)

## Source Files

- `gen_epix/omopdb/services/remote_app.py`
- `test/commondb/unit/remote_app/test_commondb_remote_app.py`
- `test/fastapp/unit/test_fastapp_remote_app.py`
- `test/omopdb/unit/services/test_omopdb_remote_app.py`

## Audit Trail

- EXTRACTED: 38 (90%)
- INFERRED: 4 (10%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*