# Regex & Passthrough Filters

> 101 nodes · cohesion 0.04

## Key Concepts

- **log_parser_v2.py** (22 connections) — `test/test_client/log_parser_v2.py`
- **log_parser_v1.py** (20 connections) — `test/test_client/log_parser_v1.py`
- **V1LogParser** (19 connections) — `test/test_client/log_parser_v1.py`
- **NoFilter** (17 connections) — `gen_epix/filter/no_filter.py`
- **V2LogParser** (17 connections) — `test/test_client/log_parser_v2.py`
- **RegexFilter** (15 connections) — `gen_epix/filter/regex.py`
- **TestRead** (14 connections) — `test/casedb/performance/user_journey/test_casedb_user_journey_performance.py`
- **LogParser** (12 connections) — `test/test_client/log_parser.py`
- **UserJourney** (12 connections) — `test/test_client/user_journey.py`
- **LogType** (11 connections) — `test/test_client/log_parser.py`
- **V1UserJourney** (11 connections) — `test/test_client/user_journey_v1.py`
- **V2UserJourney** (11 connections) — `test/test_client/user_journey_v2.py`
- **log_parser.py** (9 connections) — `test/test_client/log_parser.py`
- **user_journey_v1.py** (8 connections) — `test/test_client/user_journey_v1.py`
- **user_journey_v2.py** (8 connections) — `test/test_client/user_journey_v2.py`
- **._azure_lines_parser()** (7 connections) — `test/test_client/log_parser_v1.py`
- **.parse()** (7 connections) — `test/test_client/log_parser_v1.py`
- **UserJourneyColumn** (7 connections) — `test/test_client/user_journey_v1.py`
- **UserJourneyColumn** (7 connections) — `test/test_client/user_journey_v2.py`
- **AzureColumn** (6 connections) — `test/test_client/log_parser.py`
- **LogCode** (6 connections) — `test/test_client/log_parser.py`
- **._direct_lines_parser()** (6 connections) — `test/test_client/log_parser_v1.py`
- **._azure_lines_parser()** (6 connections) — `test/test_client/log_parser_v2.py`
- **.parse()** (6 connections) — `test/test_client/log_parser_v2.py`
- **.create_command_from_dict()** (6 connections) — `test/test_client/user_journey_v1.py`
- *... and 76 more nodes in this community*

## Relationships

- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (18 shared connections)
- [Row Filter Matching](Row_Filter_Matching.md) (8 shared connections)
- [Filter Base Abstractions](Filter_Base_Abstractions.md) (6 shared connections)
- [Column & Row Filtering](Column_&_Row_Filtering.md) (6 shared connections)
- [Range Filters](Range_Filters.md) (5 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (4 shared connections)
- [Task Runner Commands](Task_Runner_Commands.md) (4 shared connections)
- [Composite Filters](Composite_Filters.md) (4 shared connections)
- [Seqdb Sequence Retrieval Commands](Seqdb_Sequence_Retrieval_Commands.md) (3 shared connections)
- [User Journey Log Parser](User_Journey_Log_Parser.md) (2 shared connections)
- [Domain & Entity Registry](Domain_&_Entity_Registry.md) (2 shared connections)
- [Filter Test Base](Filter_Test_Base.md) (1 shared connections)

## Source Files

- `gen_epix/filter/no_filter.py`
- `gen_epix/filter/regex.py`
- `test/casedb/performance/user_journey/test_casedb_user_journey_performance.py`
- `test/commondb/unit/services/test_system.py`
- `test/test_client/log_parser.py`
- `test/test_client/log_parser_v1.py`
- `test/test_client/log_parser_v2.py`
- `test/test_client/user_journey.py`
- `test/test_client/user_journey_v1.py`
- `test/test_client/user_journey_v2.py`

## Audit Trail

- EXTRACTED: 231 (90%)
- INFERRED: 27 (10%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*