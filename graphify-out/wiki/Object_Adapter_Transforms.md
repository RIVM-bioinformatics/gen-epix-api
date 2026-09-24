# Object Adapter Transforms

> 42 nodes · cohesion 0.05

## Key Concepts

- **ObjectAdapter** (84 connections) — `gen_epix/transform/adapter.py`
- **TestTupleMapTransformerCaseInsensitivity** (12 connections) — `test/transform/unit/test_transform_tuple_map.py`
- **.__call__()** (7 connections) — `gen_epix/transform/transformer.py`
- **.transform()** (4 connections) — `gen_epix/transform/transformer.py`
- **.test_case_insensitive_by_default()** (4 connections) — `test/transform/unit/test_transform_tuple_map.py`
- **.test_case_insensitive_match()** (4 connections) — `test/transform/unit/test_transform_tuple_map.py`
- **.test_case_insensitive_non_string_values_unaffected()** (4 connections) — `test/transform/unit/test_transform_tuple_map.py`
- **.test_case_insensitive_with_set_default()** (4 connections) — `test/transform/unit/test_transform_tuple_map.py`
- **.test_case_sensitive_explicit()** (4 connections) — `test/transform/unit/test_transform_tuple_map.py`
- **.unwrap()** (3 connections) — `gen_epix/transform/adapter.py`
- **.transform()** (3 connections) — `gen_epix/transform/examples.py`
- **.transform()** (3 connections) — `gen_epix/transform/transformers/conditional.py`
- **.transform()** (3 connections) — `gen_epix/transform/transformers/field.py`
- **.transform()** (3 connections) — `gen_epix/transform/transformers/iso_time.py`
- **.transform()** (3 connections) — `gen_epix/transform/transformers/multi_field.py`
- **.transform()** (3 connections) — `gen_epix/transform/transformers/object.py`
- **.__init__()** (3 connections) — `gen_epix/transform/transformers/validation.py`
- **.transform()** (3 connections) — `gen_epix/transform/transformers/validation.py`
- **.test_case_insensitive_map_key_conflict_raises()** (3 connections) — `test/transform/unit/test_transform_tuple_map.py`
- **.has_key()** (2 connections) — `gen_epix/transform/adapter.py`
- **.keys()** (2 connections) — `gen_epix/transform/adapter.py`
- **Encapsulates adapter selection for supported object representations. Supported…** (1 connections) — `gen_epix/transform/adapter.py`
- **Return the wrapped object, including any adapter-applied updates.** (1 connections) — `gen_epix/transform/adapter.py`
- **Return the example object unchanged.** (1 connections) — `gen_epix/transform/examples.py`
- **Any** (1 connections)
- *... and 17 more nodes in this community*

## Relationships

- [Tuple Mapping Transformer](Tuple_Mapping_Transformer.md) (27 shared connections)
- [Transform Adapters & Examples](Transform_Adapters_&_Examples.md) (26 shared connections)
- [Transform Enums & Intervals](Transform_Enums_&_Intervals.md) (20 shared connections)
- [Dict & Polars Adapters](Dict_&_Polars_Adapters.md) (7 shared connections)
- [ISO Time Granularity Transform](ISO_Time_Granularity_Transform.md) (6 shared connections)
- [Transform Pipeline](Transform_Pipeline.md) (1 shared connections)
- [Domain & Entity Registry](Domain_&_Entity_Registry.md) (1 shared connections)

## Source Files

- `gen_epix/transform/adapter.py`
- `gen_epix/transform/examples.py`
- `gen_epix/transform/transformer.py`
- `gen_epix/transform/transformers/conditional.py`
- `gen_epix/transform/transformers/field.py`
- `gen_epix/transform/transformers/iso_time.py`
- `gen_epix/transform/transformers/multi_field.py`
- `gen_epix/transform/transformers/object.py`
- `gen_epix/transform/transformers/validation.py`
- `test/transform/unit/test_transform_tuple_map.py`

## Audit Trail

- EXTRACTED: 117 (87%)
- INFERRED: 18 (13%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*