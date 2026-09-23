# Composite Filters

> 39 nodes · cohesion 0.11

## Key Concepts

- **CompositeFilter** (91 connections) — `gen_epix/filter/composite.py`
- **.match_row()** (12 connections) — `gen_epix/filter/composite.py`
- **.filter_rows()** (11 connections) — `gen_epix/filter/composite.py`
- **.match_rows()** (11 connections) — `gen_epix/filter/composite.py`
- **._get_row_value()** (10 connections) — `gen_epix/filter/composite.py`
- **._not_na_row_iterator()** (9 connections) — `gen_epix/filter/composite.py`
- **._not_none_row_iterator()** (9 connections) — `gen_epix/filter/composite.py`
- **Any** (9 connections)
- **Hashable** (9 connections)
- **._get_map_fun_list()** (7 connections) — `gen_epix/filter/composite.py`
- **validate_filter_behavior()** (7 connections) — `test/filter/unit/util.py`
- **BaseModel** (6 connections)
- **unit/util.py** (6 connections) — `test/filter/unit/util.py`
- **._all_subfilters_have_key()** (5 connections) — `gen_epix/filter/composite.py`
- **._match_row()** (5 connections) — `gen_epix/filter/composite.py`
- **.get_keys()** (4 connections) — `gen_epix/filter/composite.py`
- **.set_keys()** (4 connections) — `gen_epix/filter/composite.py`
- **._validate_state()** (4 connections) — `gen_epix/filter/composite.py`
- **._match()** (3 connections) — `gen_epix/filter/composite.py`
- **Self** (2 connections)
- **_recursion()** (1 connections) — `gen_epix/filter/composite.py`
- **model_validator** (1 connections)
- **Match row values using the function generated during validation. Args:…** (1 connections) — `gen_epix/filter/composite.py`
- **Yield child-value presence flags while treating `None` as absent.** (1 connections) — `gen_epix/filter/composite.py`
- **Yield child-value presence flags while excluding configured NA values.** (1 connections) — `gen_epix/filter/composite.py`
- *... and 14 more nodes in this community*

## Relationships

- [Range Filters](Range_Filters.md) (10 shared connections)
- [Case Date Derivation](Case_Date_Derivation.md) (7 shared connections)
- [Filter Base Abstractions](Filter_Base_Abstractions.md) (6 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (6 shared connections)
- [Exists Filters](Exists_Filters.md) (6 shared connections)
- [Case Service Implementation](Case_Service_Implementation.md) (4 shared connections)
- [Best Sequence Retrieval](Best_Sequence_Retrieval.md) (4 shared connections)
- [Regex & Passthrough Filters](Regex_&_Passthrough_Filters.md) (4 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (4 shared connections)
- [Reference Data Access Filters](Reference_Data_Access_Filters.md) (3 shared connections)
- [Row Filter Matching](Row_Filter_Matching.md) (3 shared connections)
- [Case Upload Batch Mixin](Case_Upload_Batch_Mixin.md) (2 shared connections)

## Source Files

- `gen_epix/filter/composite.py`
- `test/filter/unit/util.py`

## Audit Trail

- EXTRACTED: 148 (91%)
- INFERRED: 14 (9%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*