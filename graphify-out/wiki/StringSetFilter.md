# StringSetFilter

> 63 nodes · cohesion 0.05

## Key Concepts

- **StringSetFilter** (33 connections) — `gen_epix/filter/string_set.py`
- **ExistsFilter** (17 connections) — `gen_epix/filter/exists.py`
- **TestFilterMatch** (16 connections) — `test/filter/unit/test_filter_match.py`
- **NumberRangeFilter** (15 connections) — `gen_epix/filter/number_range.py`
- **DateRangeFilter** (14 connections) — `gen_epix/filter/date_range.py`
- **PartialDateRangeFilter** (13 connections) — `gen_epix/filter/partial_date_range.py`
- **test_filter_match.py** (13 connections) — `test/filter/unit/test_filter_match.py`
- **test_filter_map_function.py** (10 connections) — `test/filter/unit/test_filter_map_function.py`
- **TestFilterMapFunction** (9 connections) — `test/filter/unit/test_filter_map_function.py`
- **TestFilterConstruction** (8 connections) — `test/filter/unit/test_filter_construction.py`
- **Any** (5 connections)
- **._get_datetime_bounds()** (5 connections) — `gen_epix/filter/partial_date_range.py`
- **._validate_state()** (5 connections) — `gen_epix/filter/partial_date_range.py`
- **test_filter_construction.py** (5 connections) — `test/filter/unit/test_filter_construction.py`
- **.test_composite_map_function()** (5 connections) — `test/filter/unit/test_filter_map_function.py`
- **.test_not_nested_composite_match()** (5 connections) — `test/filter/unit/test_filter_match.py`
- **._match()** (4 connections) — `gen_epix/filter/range.py`
- **._validate_state()** (4 connections) — `gen_epix/filter/string_set.py`
- **._date_to_datetime()** (4 connections) — `test/filter/unit/test_filter_construction.py`
- **.test_composite_filter_pydantic_and_plain_python_class()** (4 connections) — `test/filter/unit/test_filter_match.py`
- **.match_row()** (3 connections) — `gen_epix/filter/exists.py`
- **.match_rows()** (3 connections) — `gen_epix/filter/exists.py`
- **.fromisoformat()** (3 connections) — `gen_epix/filter/partial_date_range.py`
- **datetime** (3 connections)
- **_enum_to_str()** (3 connections) — `gen_epix/filter/string_set.py`
- *... and 38 more nodes in this community*

## Relationships

- [composite.py](composite.py.md) (34 shared connections)
- [CompositeFilter](CompositeFilter.md) (13 shared connections)
- [log_parser_v2.py](log_parser_v2.py.md) (5 shared connections)
- [retrieve_case.py](retrieve_case.py.md) (4 shared connections)
- [test_filter_base_filter.py](test_filter_base_filter.py.md) (3 shared connections)
- [BaseUnitOfWork](BaseUnitOfWork.md) (3 shared connections)
- [Filter](Filter.md) (2 shared connections)
- [BaseSeqService](BaseSeqService.md) (2 shared connections)
- [IntervalToIntervalTransformer](IntervalToIntervalTransformer.md) (2 shared connections)
- [case_service_create_file_for_read_set_or_seq](case_service_create_file_for_read_set_or_seq.md) (1 shared connections)
- [UuidSetFilter](UuidSetFilter.md) (1 shared connections)

## Source Files

- `gen_epix/filter/date_range.py`
- `gen_epix/filter/exists.py`
- `gen_epix/filter/number_range.py`
- `gen_epix/filter/partial_date_range.py`
- `gen_epix/filter/range.py`
- `gen_epix/filter/string_set.py`
- `test/filter/unit/test_filter_construction.py`
- `test/filter/unit/test_filter_map_function.py`
- `test/filter/unit/test_filter_match.py`

## Audit Trail

- EXTRACTED: 148 (86%)
- INFERRED: 24 (14%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*