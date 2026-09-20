# Range Filters

> 58 nodes · cohesion 0.05

## Key Concepts

- **StringSetFilter** (41 connections) — `gen_epix/filter/string_set.py`
- **DateRangeFilter** (17 connections) — `gen_epix/filter/date_range.py`
- **NumberRangeFilter** (17 connections) — `gen_epix/filter/number_range.py`
- **TestFilterMatch** (16 connections) — `test/filter/unit/test_filter_match.py`
- **test_filter_match.py** (15 connections) — `test/filter/unit/test_filter_match.py`
- **PartialDateRangeFilter** (12 connections) — `gen_epix/filter/partial_date_range.py`
- **test_filter_map_function.py** (11 connections) — `test/filter/unit/test_filter_map_function.py`
- **TestFilterMapFunction** (9 connections) — `test/filter/unit/test_filter_map_function.py`
- **TestFilterConstruction** (8 connections) — `test/filter/unit/test_filter_construction.py`
- **._get_datetime_bounds()** (6 connections) — `gen_epix/filter/partial_date_range.py`
- **._validate_state()** (6 connections) — `gen_epix/filter/partial_date_range.py`
- **test_filter_construction.py** (5 connections) — `test/filter/unit/test_filter_construction.py`
- **.test_composite_map_function()** (5 connections) — `test/filter/unit/test_filter_map_function.py`
- **.test_not_nested_composite_match()** (5 connections) — `test/filter/unit/test_filter_match.py`
- **.fromisoformat()** (4 connections) — `gen_epix/filter/partial_date_range.py`
- **.test_content()** (4 connections) — `test/casedb/integration/content/test_casedb_content.py`
- **._date_to_datetime()** (4 connections) — `test/filter/unit/test_filter_construction.py`
- **.test_composite_filter_pydantic_and_plain_python_class()** (4 connections) — `test/filter/unit/test_filter_match.py`
- **datetime** (3 connections)
- **.test_date_range_construction()** (3 connections) — `test/filter/unit/test_filter_construction.py`
- **.test_date_range_map_function()** (3 connections) — `test/filter/unit/test_filter_map_function.py`
- **.test_exists_map_function()** (3 connections) — `test/filter/unit/test_filter_map_function.py`
- **.test_number_range_map_function()** (3 connections) — `test/filter/unit/test_filter_map_function.py`
- **.test_nested_composite_match()** (3 connections) — `test/filter/unit/test_filter_match.py`
- **_match()** (2 connections) — `gen_epix/filter/partial_date_range.py`
- *... and 33 more nodes in this community*

## Relationships

- [Filter Base Abstractions](Filter_Base_Abstractions.md) (24 shared connections)
- [Exists Filters](Exists_Filters.md) (11 shared connections)
- [Composite Filters](Composite_Filters.md) (10 shared connections)
- [Regex & Passthrough Filters](Regex_&_Passthrough_Filters.md) (5 shared connections)
- [Commondb SQLAlchemy Mapper](Commondb_SQLAlchemy_Mapper.md) (3 shared connections)
- [Case Query Retrieval](Case_Query_Retrieval.md) (3 shared connections)
- [Database Session Isolation](Database_Session_Isolation.md) (2 shared connections)
- [Filter Test Base](Filter_Test_Base.md) (2 shared connections)
- [Case Upload Batch Mixin](Case_Upload_Batch_Mixin.md) (2 shared connections)
- [FastApp HTTP Client](FastApp_HTTP_Client.md) (2 shared connections)
- [Seqdb Locus & Protocol CRUD](Seqdb_Locus_&_Protocol_CRUD.md) (2 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (2 shared connections)

## Source Files

- `gen_epix/filter/date_range.py`
- `gen_epix/filter/number_range.py`
- `gen_epix/filter/partial_date_range.py`
- `gen_epix/filter/string_set.py`
- `test/casedb/integration/content/test_casedb_content.py`
- `test/filter/unit/test_filter_construction.py`
- `test/filter/unit/test_filter_map_function.py`
- `test/filter/unit/test_filter_match.py`

## Audit Trail

- EXTRACTED: 147 (88%)
- INFERRED: 20 (12%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*