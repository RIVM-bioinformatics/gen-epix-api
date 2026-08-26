# Case Date Calculation Utils

> 25 nodes · cohesion 0.17

## Key Concepts

- **case_date.py** (27 connections) — `gen_epix/casedb/services/case/case_date.py`
- **case_service_get_case_date_col_mappers()** (12 connections) — `gen_epix/casedb/services/case/case_date.py`
- **case_service_calculate_case_date()** (11 connections) — `gen_epix/casedb/services/case/case_date.py`
- **datetime** (9 connections)
- **case_service_get_case_date_col_mappers_from_cols()** (8 connections) — `gen_epix/casedb/services/case/case_date.py`
- **test_casedb_get_case_date.py** (7 connections) — `test/casedb/unit/case_date/test_casedb_get_case_date.py`
- **TestGetCaseDate** (7 connections) — `test/casedb/unit/case_date/test_casedb_get_case_date.py`
- **convert_iso_date_to_datetime()** (6 connections) — `gen_epix/casedb/services/case/case_date.py`
- **convert_iso_week_to_first_day_datetime()** (5 connections) — `gen_epix/casedb/services/case/case_date.py`
- **._make_case()** (5 connections) — `test/casedb/unit/case_date/test_casedb_get_case_date.py`
- **.test_falls_back_to_lower_resolution_when_higher_is_none()** (5 connections) — `test/casedb/unit/case_date/test_casedb_get_case_date.py`
- **.test_stops_at_highest_resolution_when_both_day_and_week_present()** (5 connections) — `test/casedb/unit/case_date/test_casedb_get_case_date.py`
- **UUID** (4 connections)
- **.test_all_cols_none_leaves_case_date_unchanged()** (4 connections) — `test/casedb/unit/case_date/test_casedb_get_case_date.py`
- **convert_iso_month_to_first_day_datetime()** (2 connections) — `gen_epix/casedb/services/case/case_date.py`
- **convert_iso_quarter_to_first_day_datetime()** (2 connections) — `gen_epix/casedb/services/case/case_date.py`
- **convert_iso_year_to_first_day_datetime()** (2 connections) — `gen_epix/casedb/services/case/case_date.py`
- **BaseCaseService** (1 connections)
- **Case** (1 connections)
- **Col** (1 connections)
- **RefCol** (1 connections)
- **Calculate and set the case date for each case in the provided list of cases,…** (1 connections) — `gen_epix/casedb/services/case/case_date.py`
- **Retrieve all Col IDs for the given CaseType that can be used to compute case…** (1 connections) — `gen_epix/casedb/services/case/case_date.py`
- **Case** (1 connections)
- **Unit tests for case_service_calculate_case_date() function.** (1 connections) — `test/casedb/unit/case_date/test_casedb_get_case_date.py`

## Relationships

- [Casedb ABAC & Filter Logic](Casedb_ABAC_&_Filter_Logic.md) (11 shared connections)
- [Casedb Case CRUD Commands](Casedb_Case_CRUD_Commands.md) (5 shared connections)
- [Case Data Serialization](Case_Data_Serialization.md) (4 shared connections)
- [Case Domain Enums](Case_Domain_Enums.md) (3 shared connections)
- [Casedb Case Service](Casedb_Case_Service.md) (2 shared connections)
- [Case Service CRUD](Case_Service_CRUD.md) (1 shared connections)
- [Casedb CaseSet CRUD & Tests](Casedb_CaseSet_CRUD_&_Tests.md) (1 shared connections)
- [Abac Service Access Control](Abac_Service_Access_Control.md) (1 shared connections)
- [Case Data Validator](Case_Data_Validator.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/services/case/case_date.py`
- `test/casedb/unit/case_date/test_casedb_get_case_date.py`

## Audit Trail

- EXTRACTED: 68 (86%)
- INFERRED: 11 (14%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*