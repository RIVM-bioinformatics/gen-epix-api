# Row Filter Matching

> 43 nodes · cohesion 0.09

## Key Concepts

- **Filter** (93 connections) — `gen_epix/filter/base.py`
- **Any** (12 connections)
- **._is_row_match_with_na_values()** (10 connections) — `gen_epix/filter/base.py`
- **._is_row_match_without_na_values()** (10 connections) — `gen_epix/filter/base.py`
- **.filter_rows()** (9 connections) — `gen_epix/filter/base.py`
- **Hashable** (9 connections)
- **._match()** (8 connections) — `gen_epix/filter/base.py`
- **.match_row()** (8 connections) — `gen_epix/filter/base.py`
- **.match_rows()** (8 connections) — `gen_epix/filter/base.py`
- **._get_row_value()** (7 connections) — `gen_epix/filter/base.py`
- **._initialize_mapping()** (7 connections) — `gen_epix/filter/base.py`
- **BaseModel** (7 connections)
- **.__call__()** (5 connections) — `gen_epix/filter/base.py`
- **.filter_column()** (5 connections) — `gen_epix/filter/base.py`
- **.match_column()** (4 connections) — `gen_epix/filter/base.py`
- **.match_value()** (4 connections) — `gen_epix/filter/base.py`
- **.set_key()** (4 connections) — `gen_epix/filter/base.py`
- **EqualsFilter** (4 connections) — `gen_epix/filter/equals.py`
- **_default_validate_query_filter()** (3 connections) — `gen_epix/fastapp/api/crud_endpoint_generator.py`
- **.get_key()** (3 connections) — `gen_epix/filter/base.py`
- **._match()** (3 connections) — `gen_epix/filter/equals.py`
- **.is_composite()** (2 connections) — `gen_epix/filter/base.py`
- **Allow query filters with at most one level of composite filters.** (1 connections) — `gen_epix/fastapp/api/crud_endpoint_generator.py`
- **Self** (1 connections)
- **Yield column values that match the filter.** (1 connections) — `gen_epix/filter/base.py`
- *... and 18 more nodes in this community*

## Relationships

- [Filter Base Abstractions](Filter_Base_Abstractions.md) (15 shared connections)
- [Regex & Passthrough Filters](Regex_&_Passthrough_Filters.md) (8 shared connections)
- [CRUD Endpoint Generation](CRUD_Endpoint_Generation.md) (7 shared connections)
- [SQLAlchemy Repository Queries](SQLAlchemy_Repository_Queries.md) (7 shared connections)
- [Filter Test Base](Filter_Test_Base.md) (4 shared connections)
- [Generic Repository CRUD](Generic_Repository_CRUD.md) (4 shared connections)
- [Generic Repository Base](Generic_Repository_Base.md) (3 shared connections)
- [Composite Filters](Composite_Filters.md) (3 shared connections)
- [In-Memory Dict Repository](In-Memory_Dict_Repository.md) (2 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (2 shared connections)
- [Domain Registry & ABAC Policies](Domain_Registry_&_ABAC_Policies.md) (2 shared connections)
- [Audit Metadata Modifiers](Audit_Metadata_Modifiers.md) (2 shared connections)

## Source Files

- `gen_epix/fastapp/api/crud_endpoint_generator.py`
- `gen_epix/filter/base.py`
- `gen_epix/filter/equals.py`

## Audit Trail

- EXTRACTED: 157 (98%)
- INFERRED: 4 (2%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*