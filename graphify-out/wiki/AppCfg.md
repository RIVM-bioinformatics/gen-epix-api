# AppCfg

> 171 nodes

## Key Concepts

- **AppCfg** (56 connections) — `gen_epix/commondb/config/cfg.py`
- **ServerManager** (44 connections) — `test/test_client/server_manager.py`
- **test_casedb_seqdb_connection.py** (31 connections) — `test/end_to_end/casedb_seqdb_connection/test_casedb_seqdb_connection.py`
- **create_fast_api()** (30 connections) — `gen_epix/commondb/app_setup.py`
- **start_all_services.py** (30 connections) — `test/test_client/start_all_services.py`
- **AppComposer** (26 connections) — `gen_epix/commondb/env.py`
- **app_setup.py** (25 connections) — `gen_epix/commondb/app_setup.py`
- **AppComposer** (22 connections) — `gen_epix/casedb/env.py`
- **omopdb_test_client.py** (22 connections) — `test/omopdb/omopdb_test_client.py`
- **commondb/test_client/util.py** (21 connections) — `test/commondb/test_client/util.py`
- **OmopdbTestClient** (18 connections) — `test/omopdb/omopdb_test_client.py`
- **get_test_client()** (17 connections) — `test/commondb/test_client/util.py`
- **seqdb/env.py** (14 connections) — `gen_epix/seqdb/env.py`
- **casedb/env.py** (13 connections) — `gen_epix/casedb/env.py`
- **get_test_output_dir()** (12 connections) — `test/test_client/util.py`
- **omopdb/env.py** (12 connections) — `gen_epix/omopdb/env.py`
- **HandleAuthExceptionMiddleware** (11 connections) — `gen_epix/fastapp/middleware/handle_auth_exception.py`
- **AppComposer** (11 connections) — `gen_epix/seqdb/env.py`
- **casedb/app.py** (11 connections) — `gen_epix/casedb/app.py`
- **omopdb/app.py** (11 connections) — `gen_epix/omopdb/app.py`
- **seqdb/app.py** (11 connections) — `gen_epix/seqdb/app.py`
- **test_client_credential_flow.py** (11 connections) — `test/end_to_end/client_credential_flow/test_client_credential_flow.py`
- **AppComposer** (9 connections) — `gen_epix/omopdb/env.py`
- **ServerType** (9 connections) — `test/test_client/enum.py`
- **commondb/app.py** (9 connections) — `gen_epix/commondb/app.py`
- *... and 146 more nodes in this community*

## Relationships

- [commondb/domain/enum.py](commondb-domain-enum.py.md) (50 shared connections)
- [CrudOperation](CrudOperation.md) (26 shared connections)
- [BaseAppCfg](BaseAppCfg.md) (21 shared connections)
- [CrudEndpointGenerator](CrudEndpointGenerator.md) (20 shared connections)
- [RequestorApp](RequestorApp.md) (12 shared connections)
- [Commondb App Composition (env.py)](Commondb_App_Composition_env.py.md) (10 shared connections)
- [test/test_client/util.py](test-test_client-util.py.md) (10 shared connections)
- [seqdb_test_client.py](seqdb_test_client.py.md) (6 shared connections)
- [gen_epix/util.py](gen_epix-util.py.md) (6 shared connections)
- [SeqdbTestClient](SeqdbTestClient.md) (5 shared connections)
- [commondb/api/exc.py](commondb-api-exc.py.md) (5 shared connections)
- [casedb/domain/enum.py](casedb-domain-enum.py.md) (4 shared connections)

## Source Files

- `gen_epix/casedb/app.py`
- `gen_epix/casedb/domain/policy/permission.py`
- `gen_epix/casedb/env.py`
- `gen_epix/commondb/app.py`
- `gen_epix/commondb/app_setup.py`
- `gen_epix/commondb/config/cfg.py`
- `gen_epix/commondb/env.py`
- `gen_epix/fastapp/api/openapi.py`
- `gen_epix/fastapp/middleware/__init__.py`
- `gen_epix/fastapp/middleware/handle_auth_exception.py`
- `gen_epix/fastapp/middleware/limiter.py`
- `gen_epix/fastapp/middleware/update_response_header.py`
- `gen_epix/omopdb/app.py`
- `gen_epix/omopdb/env.py`
- `gen_epix/seqdb/app.py`
- `gen_epix/seqdb/env.py`
- `gen_epix/util.py`
- `run.py`
- `test/commondb/test_client/util.py`
- `test/end_to_end/casedb_seqdb_connection/envvar.py`

## Audit Trail

- EXTRACTED: 514 (91%)
- INFERRED: 49 (9%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*