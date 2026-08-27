# ObjectAdapter

> 94 nodes · cohesion 0.04

## Key Concepts

- **ObjectAdapter** (89 connections) — `gen_epix/transform/adapter.py`
- **TupleMapTransformer** (55 connections) — `gen_epix/transform/transformers/tuple_map.py`
- **TestTupleMapTransformer** (18 connections) — `test/transform/unit/test_transform_tuple_map.py`
- **TestTupleMapTransformerValidation** (15 connections) — `test/transform/unit/test_transform_tuple_map.py`
- **test_transform_tuple_map.py** (11 connections) — `test/transform/unit/test_transform_tuple_map.py`
- **TestTupleMapTransformerCaseInsensitivity** (11 connections) — `test/transform/unit/test_transform_tuple_map.py`
- **TestTupleMapTransformerDefaultValues** (9 connections) — `test/transform/unit/test_transform_tuple_map.py`
- **.transform()** (5 connections) — `gen_epix/transform/transformers/tuple_map.py`
- **.transform_row()** (4 connections) — `gen_epix/transform/transformers/tuple_map.py`
- **scenario_ids** (4 connections)
- **.test_basic_single_field_mapping()** (4 connections) — `test/transform/unit/test_transform_tuple_map.py`
- **.test_different_map_and_row_field_names()** (4 connections) — `test/transform/unit/test_transform_tuple_map.py`
- **.test_is_active_map_field()** (4 connections) — `test/transform/unit/test_transform_tuple_map.py`
- **.test_multi_source_to_multi_target()** (4 connections) — `test/transform/unit/test_transform_tuple_map.py`
- **.test_multi_source_to_single_target()** (4 connections) — `test/transform/unit/test_transform_tuple_map.py`
- **.test_preserves_existing_fields()** (4 connections) — `test/transform/unit/test_transform_tuple_map.py`
- **.test_single_source_to_multi_target()** (4 connections) — `test/transform/unit/test_transform_tuple_map.py`
- **.test_transform_no_match_raises()** (4 connections) — `test/transform/unit/test_transform_tuple_map.py`
- **.test_update_map()** (4 connections) — `test/transform/unit/test_transform_tuple_map.py`
- **.test_case_insensitive_by_default()** (4 connections) — `test/transform/unit/test_transform_tuple_map.py`
- **.test_case_insensitive_match()** (4 connections) — `test/transform/unit/test_transform_tuple_map.py`
- **.test_case_insensitive_non_string_values_unaffected()** (4 connections) — `test/transform/unit/test_transform_tuple_map.py`
- **.test_case_insensitive_with_set_default()** (4 connections) — `test/transform/unit/test_transform_tuple_map.py`
- **.test_case_sensitive_explicit()** (4 connections) — `test/transform/unit/test_transform_tuple_map.py`
- **.test_set_default_applies_defaults_on_no_match()** (4 connections) — `test/transform/unit/test_transform_tuple_map.py`
- *... and 69 more nodes in this community*

## Relationships

- [Transformer](Transformer.md) (30 shared connections)
- [case_validator.py](case_validator.py.md) (12 shared connections)
- [IntervalToIntervalTransformer](IntervalToIntervalTransformer.md) (11 shared connections)
- [Hashable](Hashable.md) (7 shared connections)
- [.__init__](__init__.md) (7 shared connections)
- [CaseValidator](CaseValidator.md) (4 shared connections)
- [IsoTimeTransformer](IsoTimeTransformer.md) (4 shared connections)
- [.__call__](__call__.md) (2 shared connections)
- [CrudOperation](CrudOperation.md) (2 shared connections)

## Source Files

- `gen_epix/transform/adapter.py`
- `gen_epix/transform/transformers/conditional.py`
- `gen_epix/transform/transformers/field.py`
- `gen_epix/transform/transformers/multi_field.py`
- `gen_epix/transform/transformers/object.py`
- `gen_epix/transform/transformers/tuple_map.py`
- `gen_epix/transform/transformers/validation.py`
- `test/transform/unit/test_transform_tuple_map.py`

## Audit Trail

- EXTRACTED: 222 (91%)
- INFERRED: 21 (9%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*