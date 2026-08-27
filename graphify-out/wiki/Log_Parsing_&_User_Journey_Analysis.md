# Log Parsing & User Journey Analysis

> 100 nodes · cohesion 0.04

## Key Concepts

- **log_parser_v2.py** (22 connections) — `test/test_client/log_parser_v2.py`
- **log_parser_v1.py** (21 connections) — `test/test_client/log_parser_v1.py`
- **V2LogParser** (20 connections) — `test/test_client/log_parser_v2.py`
- **V1LogParser** (19 connections) — `test/test_client/log_parser_v1.py`
- **NoFilter** (18 connections) — `gen_epix/filter/no_filter.py`
- **TestRead** (12 connections) — `test/casedb/performance/user_journey/test_casedb_user_journey_performance.py`
- **LogParser** (12 connections) — `test/test_client/log_parser.py`
- **UserJourney** (12 connections) — `test/test_client/user_journey.py`
- **LogType** (11 connections) — `test/test_client/log_parser.py`
- **V1UserJourney** (11 connections) — `test/test_client/user_journey_v1.py`
- **V2UserJourney** (11 connections) — `test/test_client/user_journey_v2.py`
- **log_parser.py** (9 connections) — `test/test_client/log_parser.py`
- **user_journey_v1.py** (8 connections) — `test/test_client/user_journey_v1.py`
- **user_journey_v2.py** (8 connections) — `test/test_client/user_journey_v2.py`
- **UserJourneyColumn** (7 connections) — `test/test_client/user_journey_v1.py`
- **UserJourneyColumn** (7 connections) — `test/test_client/user_journey_v2.py`
- **Any** (6 connections)
- **AzureColumn** (6 connections) — `test/test_client/log_parser.py`
- **LogCode** (6 connections) — `test/test_client/log_parser.py`
- **._azure_lines_parser()** (6 connections) — `test/test_client/log_parser_v1.py`
- **.parse()** (6 connections) — `test/test_client/log_parser_v1.py`
- **._azure_lines_parser()** (6 connections) — `test/test_client/log_parser_v2.py`
- **.parse()** (6 connections) — `test/test_client/log_parser_v2.py`
- **._direct_lines_parser()** (5 connections) — `test/test_client/log_parser_v1.py`
- **._direct_lines_parser()** (5 connections) — `test/test_client/log_parser_v2.py`
- *... and 75 more nodes in this community*

## Relationships

- [Casedb ABAC & Filter Logic](Casedb_ABAC_&_Filter_Logic.md) (21 shared connections)
- [Commondb Enums & Demo Data](Commondb_Enums_&_Demo_Data.md) (13 shared connections)
- [Query Filter Engine](Query_Filter_Engine.md) (7 shared connections)
- [CLI Test Runner](CLI_Test_Runner.md) (5 shared connections)
- [Casedb Domain CRUD Commands](Casedb_Domain_CRUD_Commands.md) (3 shared connections)
- [App Composition & Startup](App_Composition_&_Startup.md) (2 shared connections)
- [Log Parsing Utility](Log_Parsing_Utility.md) (2 shared connections)
- [Casedb Test Client Helpers](Casedb_Test_Client_Helpers.md) (1 shared connections)

## Source Files

- `gen_epix/filter/no_filter.py`
- `run.py`
- `test/casedb/performance/user_journey/test_casedb_user_journey_performance.py`
- `test/test_client/log_parser.py`
- `test/test_client/log_parser_v1.py`
- `test/test_client/log_parser_v2.py`
- `test/test_client/user_journey.py`
- `test/test_client/user_journey_v1.py`
- `test/test_client/user_journey_v2.py`

## Audit Trail

- EXTRACTED: 226 (91%)
- INFERRED: 21 (9%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*