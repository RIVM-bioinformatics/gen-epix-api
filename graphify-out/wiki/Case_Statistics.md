# Case Statistics

> 21 nodes · cohesion 0.14

## Key Concepts

- **CaseStats** (14 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **retrieve_case_type_stats_profiled()** (9 connections) — `test/casedb/performance/retrieve_stats/test_retrieve_stats.py`
- **retrieve_case_type_stats()** (8 connections) — `test/casedb/performance/retrieve_stats/test_retrieve_stats.py`
- **get_all_case_type_ids()** (7 connections) — `test/casedb/performance/retrieve_stats/test_retrieve_stats.py`
- **test_retrieve_case_type_stats_scaled_profiled()** (7 connections) — `test/casedb/performance/retrieve_stats/test_retrieve_stats.py`
- **get_user_for_test()** (5 connections) — `test/casedb/performance/retrieve_stats/test_retrieve_stats.py`
- **User** (5 connections)
- **UUID** (5 connections)
- **._validate_model()** (4 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **.retrieve_case_set_stats()** (3 connections) — `gen_epix/casedb/services/client.py`
- **.retrieve_case_type_stats()** (3 connections) — `gen_epix/casedb/services/client.py`
- **get_test_client()** (3 connections) — `test/casedb/performance/retrieve_stats/test_retrieve_stats.py`
- **fixture** (3 connections)
- **model_validator** (1 connections)
- **Self** (1 connections)
- **Represents aggregate statistics for cases or a case set. Model validation: Own…** (1 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **Validate count and case-date invariants.** (1 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **parametrize** (1 connections)
- **Profiled version of retrieve_case_type_stats.** (1 connections) — `test/casedb/performance/retrieve_stats/test_retrieve_stats.py`
- **Fetch and return the target organization user once per test module.** (1 connections) — `test/casedb/performance/retrieve_stats/test_retrieve_stats.py`
- **Fetch and return all case type IDs once per test module.** (1 connections) — `test/casedb/performance/retrieve_stats/test_retrieve_stats.py`

## Relationships

- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (7 shared connections)
- [Casedb Endpoint Test Client](Casedb_Endpoint_Test_Client.md) (6 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (5 shared connections)
- [Case Repository](Case_Repository.md) (2 shared connections)
- [Casedb Client Handlers](Casedb_Client_Handlers.md) (2 shared connections)
- [Complete Case Type Models](Complete_Case_Type_Models.md) (1 shared connections)
- [SQLAlchemy Case Repository](SQLAlchemy_Case_Repository.md) (1 shared connections)
- [Case Access Rights](Case_Access_Rights.md) (1 shared connections)
- [Dependency List Checks](Dependency_List_Checks.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/domain/model/case/non_persistable.py`
- `gen_epix/casedb/services/client.py`
- `test/casedb/performance/retrieve_stats/test_retrieve_stats.py`

## Audit Trail

- EXTRACTED: 49 (89%)
- INFERRED: 6 (11%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*