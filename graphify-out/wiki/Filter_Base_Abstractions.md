# Filter Base Abstractions

> 58 nodes · cohesion 0.06

## Key Concepts

- **composite.py** (47 connections) — `gen_epix/filter/composite.py`
- **filter/__init__.py** (40 connections) — `gen_epix/filter/__init__.py`
- **filter/enum.py** (34 connections) — `gen_epix/filter/enum.py`
- **filter/base.py** (18 connections) — `gen_epix/filter/base.py`
- **RangeFilter** (16 connections) — `gen_epix/filter/range.py`
- **uuid_set.py** (16 connections) — `gen_epix/filter/uuid_set.py`
- **seq/crud_common.py** (14 connections) — `gen_epix/seqdb/services/seq/crud_common.py`
- **string_set.py** (13 connections) — `gen_epix/filter/string_set.py`
- **range.py** (10 connections) — `gen_epix/filter/range.py`
- **date_range.py** (9 connections) — `gen_epix/filter/date_range.py`
- **equals.py** (9 connections) — `gen_epix/filter/equals.py`
- **partial_date_range.py** (9 connections) — `gen_epix/filter/partial_date_range.py`
- **equals_boolean.py** (8 connections) — `gen_epix/filter/equals_boolean.py`
- **number_range.py** (8 connections) — `gen_epix/filter/number_range.py`
- **equals_number.py** (7 connections) — `gen_epix/filter/equals_number.py`
- **HashableSetFilter** (7 connections) — `gen_epix/filter/hashable_set.py`
- **no_filter.py** (7 connections) — `gen_epix/filter/no_filter.py`
- **regex.py** (7 connections) — `gen_epix/filter/regex.py`
- **_compose_id_filter()** (7 connections) — `gen_epix/seqdb/services/seq/crud_common.py`
- **equals_string.py** (6 connections) — `gen_epix/filter/equals_string.py`
- **hashable_set.py** (6 connections) — `gen_epix/filter/hashable_set.py`
- **._validate_state()** (5 connections) — `gen_epix/filter/range.py`
- **Enum** (4 connections)
- **ComparisonOperator** (3 connections) — `gen_epix/filter/enum.py`
- **FilterType** (3 connections) — `gen_epix/filter/enum.py`
- *... and 33 more nodes in this community*

## Relationships

- [Range Filters](Range_Filters.md) (24 shared connections)
- [Exists Filters](Exists_Filters.md) (17 shared connections)
- [Row Filter Matching](Row_Filter_Matching.md) (15 shared connections)
- [Case Date Derivation](Case_Date_Derivation.md) (15 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (10 shared connections)
- [Composite Filters](Composite_Filters.md) (6 shared connections)
- [Database Session Isolation](Database_Session_Isolation.md) (6 shared connections)
- [Regex & Passthrough Filters](Regex_&_Passthrough_Filters.md) (6 shared connections)
- [Reference Data Access Filters](Reference_Data_Access_Filters.md) (6 shared connections)
- [Case Repository](Case_Repository.md) (5 shared connections)
- [Best Sequence Retrieval](Best_Sequence_Retrieval.md) (4 shared connections)
- [Role Generation & Hierarchy](Role_Generation_&_Hierarchy.md) (4 shared connections)

## Source Files

- `gen_epix/filter/__init__.py`
- `gen_epix/filter/base.py`
- `gen_epix/filter/composite.py`
- `gen_epix/filter/date_range.py`
- `gen_epix/filter/enum.py`
- `gen_epix/filter/equals.py`
- `gen_epix/filter/equals_boolean.py`
- `gen_epix/filter/equals_number.py`
- `gen_epix/filter/equals_string.py`
- `gen_epix/filter/hashable_set.py`
- `gen_epix/filter/no_filter.py`
- `gen_epix/filter/number_range.py`
- `gen_epix/filter/partial_date_range.py`
- `gen_epix/filter/range.py`
- `gen_epix/filter/regex.py`
- `gen_epix/filter/string_set.py`
- `gen_epix/filter/uuid_set.py`
- `gen_epix/seqdb/services/seq/crud_common.py`

## Audit Trail

- EXTRACTED: 243 (99%)
- INFERRED: 2 (1%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*