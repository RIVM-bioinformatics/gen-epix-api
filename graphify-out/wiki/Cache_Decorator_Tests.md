# Cache Decorator Tests

> 73 nodes · cohesion 0.03

## Key Concepts

- **.load()** (28 connections) — `test/fastapp/unit/repositories/sa/test_fastapp_sa_repository_mapper.py`
- **test_fastapp_cache_decorator.py** (24 connections) — `test/fastapp/unit/cache/test_fastapp_cache_decorator.py`
- **make_region()** (19 connections) — `test/fastapp/unit/cache/test_fastapp_cache_region.py`
- **UnreadableSerializer** (7 connections) — `test/fastapp/unit/cache/test_fastapp_cache_region.py`
- **test_an_unreadable_entry_is_replaced_instead_of_failing()** (6 connections) — `test/fastapp/unit/cache/test_fastapp_cache_region.py`
- **fixture_region()** (5 connections) — `test/fastapp/unit/cache/test_fastapp_cache_decorator.py`
- **test_a_key_template_narrows_what_participates_in_the_key()** (5 connections) — `test/fastapp/unit/cache/test_fastapp_cache_decorator.py`
- **test_a_condition_bypasses_the_cache_for_selected_calls()** (4 connections) — `test/fastapp/unit/cache/test_fastapp_cache_decorator.py`
- **test_a_writer_can_reproduce_the_key_of_a_reader()** (4 connections) — `test/fastapp/unit/cache/test_fastapp_cache_decorator.py`
- **test_get_reports_a_miss_without_computing()** (4 connections) — `test/fastapp/unit/cache/test_fastapp_cache_decorator.py`
- **test_invalidate_all_removes_every_entry_of_that_function()** (4 connections) — `test/fastapp/unit/cache/test_fastapp_cache_decorator.py`
- **test_invalidate_removes_one_argument_combination()** (4 connections) — `test/fastapp/unit/cache/test_fastapp_cache_decorator.py`
- **test_original_bypasses_the_cache_in_both_directions()** (4 connections) — `test/fastapp/unit/cache/test_fastapp_cache_decorator.py`
- **test_refresh_recomputes_and_stores()** (4 connections) — `test/fastapp/unit/cache/test_fastapp_cache_decorator.py`
- **test_repeated_calls_run_the_function_once()** (4 connections) — `test/fastapp/unit/cache/test_fastapp_cache_decorator.py`
- **test_set_publishes_a_value_without_calling_the_function()** (4 connections) — `test/fastapp/unit/cache/test_fastapp_cache_decorator.py`
- **test_a_cached_none_is_distinguishable_from_a_miss()** (4 connections) — `test/fastapp/unit/cache/test_fastapp_cache_region.py`
- **test_a_configured_exception_is_cached_and_re_raised()** (4 connections) — `test/fastapp/unit/cache/test_fastapp_cache_region.py`
- **test_a_disabled_region_behaves_as_a_pass_through()** (4 connections) — `test/fastapp/unit/cache/test_fastapp_cache_region.py`
- **test_a_negative_result_can_expire_sooner_than_a_positive_one()** (4 connections) — `test/fastapp/unit/cache/test_fastapp_cache_region.py`
- **test_a_second_read_is_served_from_cache()** (4 connections) — `test/fastapp/unit/cache/test_fastapp_cache_region.py`
- **test_absent_results_are_not_cached_when_configured()** (4 connections) — `test/fastapp/unit/cache/test_fastapp_cache_region.py`
- **test_an_expired_entry_is_reloaded()** (4 connections) — `test/fastapp/unit/cache/test_fastapp_cache_region.py`
- **test_an_unlisted_exception_is_not_cached()** (4 connections) — `test/fastapp/unit/cache/test_fastapp_cache_region.py`
- **test_multi_key_reads_load_only_what_is_missing()** (4 connections) — `test/fastapp/unit/cache/test_fastapp_cache_region.py`
- *... and 48 more nodes in this community*

## Relationships

- [Cache Region](Cache_Region.md) (20 shared connections)
- [Cache Backend Interface](Cache_Backend_Interface.md) (19 shared connections)
- [Cache Clock & Config Enums](Cache_Clock_&_Config_Enums.md) (6 shared connections)
- [Cache Decorator & Key Generation](Cache_Decorator_&_Key_Generation.md) (4 shared connections)
- [Cache Error Types](Cache_Error_Types.md) (3 shared connections)
- [Field Type Metadata](Field_Type_Metadata.md) (3 shared connections)
- [Manual Clock Test Helpers](Manual_Clock_Test_Helpers.md) (2 shared connections)
- [Request Scope Provider](Request_Scope_Provider.md) (2 shared connections)

## Source Files

- `test/fastapp/unit/cache/test_fastapp_cache_decorator.py`
- `test/fastapp/unit/cache/test_fastapp_cache_region.py`
- `test/fastapp/unit/repositories/sa/test_fastapp_sa_repository_mapper.py`

## Audit Trail

- EXTRACTED: 105 (71%)
- INFERRED: 43 (29%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*