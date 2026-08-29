# .get_test_client

> 19 nodes

## Key Concepts

- **.get_test_client()** (10 connections) — `test/casedb/casedb_test_client.py`
- **.__init__()** (8 connections) — `test/casedb/casedb_test_client.py`
- **TestStartup** (7 connections) — `test/casedb/performance/startup/test_casedb_startup_performance.py`
- **TestRead** (6 connections) — `test/casedb/performance/repository/test_casedb_repository_performance.py`
- **parse_stats()** (6 connections) — `gen_epix/commondb/test/util.py`
- **.finalize_outputs()** (3 connections) — `test/casedb/performance/startup/test_casedb_startup_performance.py`
- **.test_startup_cprofile()** (3 connections) — `test/casedb/performance/startup/test_casedb_startup_performance.py`
- **.test_journeys()** (3 connections) — `test/casedb/performance/user_journey/test_casedb_user_journey_performance.py`
- **.finalize_outputs()** (2 connections) — `test/casedb/performance/repository/test_casedb_repository_performance.py`
- **.test_read_case_sets()** (2 connections) — `test/casedb/performance/repository/test_casedb_repository_performance.py`
- **.test_startup_pyinstrument()** (2 connections) — `test/casedb/performance/startup/test_casedb_startup_performance.py`
- **.test_tear_down()** (2 connections) — `test/casedb/performance/startup/test_casedb_startup_performance.py`
- **Any** (2 connections)
- **.test_tear_down()** (1 connections) — `test/casedb/performance/repository/test_casedb_repository_performance.py`
- **Any** (1 connections)
- **Path** (1 connections)
- **scenario_ids** (1 connections)
- **scenario_ids** (1 connections)
- **Create a test environment for the given test type and repository type. A single…** (1 connections) — `test/casedb/casedb_test_client.py`

## Relationships

- [commondb/domain/enum.py](commondb-domain-enum.py.md) (4 shared connections)
- [CasedbTestClient](CasedbTestClient.md) (4 shared connections)
- [test/test_client/util.py](test-test_client-util.py.md) (4 shared connections)
- [AppCfg](AppCfg.md) (4 shared connections)
- [log_parser_v2.py](log_parser_v2.py.md) (2 shared connections)
- [ServiceTestClient](ServiceTestClient.md) (1 shared connections)
- [EndpointTestClient](EndpointTestClient.md) (1 shared connections)
- [BaseAppCfg](BaseAppCfg.md) (1 shared connections)
- [CrudEndpointGenerator](CrudEndpointGenerator.md) (1 shared connections)

## Source Files

- `gen_epix/commondb/test/util.py`
- `test/casedb/casedb_test_client.py`
- `test/casedb/performance/repository/test_casedb_repository_performance.py`
- `test/casedb/performance/startup/test_casedb_startup_performance.py`
- `test/casedb/performance/user_journey/test_casedb_user_journey_performance.py`

## Audit Trail

- EXTRACTED: 38 (90%)
- INFERRED: 4 (10%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*