# CLI Test Runner

> 80 nodes · cohesion 0.03

## Key Concepts

- **Run** (96 connections) — `run.py`
- **.api()** (2 connections) — `run.py`
- **.other_general_generate_hex_strings()** (2 connections) — `run.py`
- **.other_general_generate_uuids()** (2 connections) — `run.py`
- **.other_oauth_server_start()** (2 connections) — `run.py`
- **.env_casedb()** (1 connections) — `run.py`
- **.env_commondb()** (1 connections) — `run.py`
- **.env_omopdb()** (1 connections) — `run.py`
- **.env_seqdb()** (1 connections) — `run.py`
- **.test_all()** (1 connections) — `run.py`
- **.test_all_incl_performance()** (1 connections) — `run.py`
- **.test_all_integration()** (1 connections) — `run.py`
- **.test_all_performance()** (1 connections) — `run.py`
- **.test_all_unit()** (1 connections) — `run.py`
- **.test_casedb_custom()** (1 connections) — `run.py`
- **.test_casedb_integration()** (1 connections) — `run.py`
- **.test_casedb_integration_build_db()** (1 connections) — `run.py`
- **.test_casedb_integration_case_upload()** (1 connections) — `run.py`
- **.test_casedb_integration_content()** (1 connections) — `run.py`
- **.test_casedb_integration_data_access()** (1 connections) — `run.py`
- **.test_casedb_performance()** (1 connections) — `run.py`
- **.test_casedb_performance_repository()** (1 connections) — `run.py`
- **.test_casedb_performance_retrieve_stats()** (1 connections) — `run.py`
- **.test_casedb_performance_startup()** (1 connections) — `run.py`
- **.test_casedb_performance_user_journey()** (1 connections) — `run.py`
- *... and 55 more nodes in this community*

## Relationships

- [Linter Utilities](Linter_Utilities.md) (5 shared connections)
- [Log Parsing & User Journey Analysis](Log_Parsing_&_User_Journey_Analysis.md) (5 shared connections)
- [App Composition & Startup](App_Composition_&_Startup.md) (4 shared connections)
- [Commondb Enums & Demo Data](Commondb_Enums_&_Demo_Data.md) (3 shared connections)
- [Graphviz ERM Generator](Graphviz_ERM_Generator.md) (2 shared connections)
- [Mermaid ERM Generator](Mermaid_ERM_Generator.md) (1 shared connections)
- [OAuth Flow Integration Tests](OAuth_Flow_Integration_Tests.md) (1 shared connections)

## Source Files

- `run.py`

## Audit Trail

- EXTRACTED: 93 (93%)
- INFERRED: 7 (7%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*