# Filter

> 35 nodes · cohesion 0.13

## Key Concepts

- **Filter** (83 connections) — `gen_epix/filter/base.py`
- **Any** (12 connections)
- **.filter_rows()** (9 connections) — `gen_epix/filter/base.py`
- **._is_row_match_with_na_values()** (9 connections) — `gen_epix/filter/base.py`
- **._is_row_match_without_na_values()** (9 connections) — `gen_epix/filter/base.py`
- **Hashable** (9 connections)
- **._match()** (8 connections) — `gen_epix/filter/base.py`
- **.match_row()** (8 connections) — `gen_epix/filter/base.py`
- **.match_rows()** (8 connections) — `gen_epix/filter/base.py`
- **._get_row_value()** (7 connections) — `gen_epix/filter/base.py`
- **BaseModel** (7 connections)
- **._initialize_mapping()** (6 connections) — `gen_epix/filter/base.py`
- **validate_filter_behavior()** (6 connections) — `test/filter/unit/util.py`
- **.__call__()** (5 connections) — `gen_epix/filter/base.py`
- **.filter_column()** (5 connections) — `gen_epix/filter/base.py`
- **.match_column()** (4 connections) — `gen_epix/filter/base.py`
- **.match_value()** (4 connections) — `gen_epix/filter/base.py`
- **.set_key()** (3 connections) — `gen_epix/filter/base.py`
- **_default_validate_query_filter()** (2 connections) — `gen_epix/fastapp/api/crud_endpoint_generator.py`
- **.get_key()** (2 connections) — `gen_epix/filter/base.py`
- **.is_composite()** (1 connections) — `gen_epix/filter/base.py`
- **Self** (1 connections)
- **Base class for filters. Attributes: invert (bool): Whether to invert the…** (1 connections) — `gen_epix/filter/base.py`
- **Check if a row matches the filter. Args: row (dict[Hashable, Any | None]): The…** (1 connections) — `gen_epix/filter/base.py`
- **Check if each row in a collection of rows matches the filter. Args: rows…** (1 connections) — `gen_epix/filter/base.py`
- *... and 10 more nodes in this community*

## Relationships

- [composite.py](composite.py.md) (20 shared connections)
- [log_parser_v2.py](log_parser_v2.py.md) (8 shared connections)
- [BaseCaseService](BaseCaseService.md) (5 shared connections)
- [test_filter_base_filter.py](test_filter_base_filter.py.md) (5 shared connections)
- [CrudEndpointGenerator](CrudEndpointGenerator.md) (4 shared connections)
- [CompositeFilter](CompositeFilter.md) (4 shared connections)
- [CrudOperation](CrudOperation.md) (4 shared connections)
- [Model](Model.md) (4 shared connections)
- [BaseRepository](BaseRepository.md) (3 shared connections)
- [DictRepository](DictRepository.md) (2 shared connections)
- [test_casedb_crud_common.py](test_casedb_crud_common.py.md) (2 shared connections)
- [UuidSetFilter](UuidSetFilter.md) (2 shared connections)

## Source Files

- `gen_epix/fastapp/api/crud_endpoint_generator.py`
- `gen_epix/filter/base.py`
- `test/filter/unit/util.py`

## Audit Trail

- EXTRACTED: 143 (99%)
- INFERRED: 1 (1%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*