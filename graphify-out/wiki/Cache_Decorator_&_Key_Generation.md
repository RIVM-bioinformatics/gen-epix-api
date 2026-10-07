# Cache Decorator & Key Generation

> 79 nodes · cohesion 0.05

## Key Concepts

- **test_fastapp_cache_key.py** (28 connections) — `test/fastapp/unit/cache/test_fastapp_cache_key.py`
- **KeySpec** (23 connections) — `gen_epix/fastapp/cache/key.py`
- **cache/key.py** (19 connections) — `gen_epix/fastapp/cache/key.py`
- **decorator.py** (16 connections) — `gen_epix/fastapp/cache/decorator.py`
- **sample()** (13 connections) — `test/fastapp/unit/cache/test_fastapp_cache_key.py`
- **bind_arguments()** (12 connections) — `gen_epix/fastapp/cache/key.py`
- **function_namespace()** (9 connections) — `gen_epix/fastapp/cache/key.py`
- **.build()** (9 connections) — `gen_epix/fastapp/cache/key.py`
- **kwarg_key_generator()** (9 connections) — `gen_epix/fastapp/cache/key.py`
- **Any** (9 connections)
- **arg_key_generator()** (7 connections) — `gen_epix/fastapp/cache/key.py`
- **template_key_generator()** (7 connections) — `gen_epix/fastapp/cache/key.py`
- **compose_key()** (6 connections) — `gen_epix/fastapp/cache/key.py`
- **._selective_generator()** (6 connections) — `gen_epix/fastapp/cache/key.py`
- **length_conditional_mangler()** (6 connections) — `gen_epix/fastapp/cache/key.py`
- **generate_key()** (5 connections) — `gen_epix/fastapp/cache/key.py`
- **KeyGeneratorFactory** (5 connections) — `gen_epix/fastapp/cache/key.py`
- **sha256_mangle_key()** (5 connections) — `gen_epix/fastapp/cache/key.py`
- **factory()** (5 connections) — `gen_epix/fastapp/cache/key.py`
- **Holder** (5 connections) — `test/fastapp/unit/cache/test_fastapp_cache_key.py`
- **test_bind_arguments_applies_defaults_and_drops_the_receiver()** (5 connections) — `test/fastapp/unit/cache/test_fastapp_cache_key.py`
- **test_include_and_exclude_together_are_rejected()** (5 connections) — `test/fastapp/unit/cache/test_fastapp_cache_key.py`
- **test_positional_templates_are_rejected()** (5 connections) — `test/fastapp/unit/cache/test_fastapp_cache_key.py`
- **test_unknown_parameter_names_are_rejected()** (5 connections) — `test/fastapp/unit/cache/test_fastapp_cache_key.py`
- **_has_receiver()** (4 connections) — `gen_epix/fastapp/cache/key.py`
- *... and 54 more nodes in this community*

## Relationships

- [Cache Error Types](Cache_Error_Types.md) (11 shared connections)
- [Cached Function Wrappers](Cached_Function_Wrappers.md) (9 shared connections)
- [Cache Backend Interface](Cache_Backend_Interface.md) (7 shared connections)
- [Cache Clock & Config Enums](Cache_Clock_&_Config_Enums.md) (5 shared connections)
- [Cache Decorator Tests](Cache_Decorator_Tests.md) (4 shared connections)
- [Cache Region](Cache_Region.md) (3 shared connections)
- [Cache Statistics](Cache_Statistics.md) (1 shared connections)
- [Cache Tag Index](Cache_Tag_Index.md) (1 shared connections)

## Source Files

- `gen_epix/fastapp/cache/decorator.py`
- `gen_epix/fastapp/cache/key.py`
- `test/fastapp/unit/cache/test_fastapp_cache_key.py`

## Audit Trail

- EXTRACTED: 156 (87%)
- INFERRED: 24 (13%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*