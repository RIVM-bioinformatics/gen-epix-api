# JSON Log Formatter

> 105 nodes · cohesion 0.05

## Key Concepts

- **JsonFormatter** (57 connections) — `gen_epix/commondb/config/json_logging.py`
- **test_json_logging.py** (49 connections) — `test/commondb/unit/logging/test_json_logging.py`
- **scenario_ids** (43 connections)
- **_make_record()** (41 connections) — `test/commondb/unit/logging/test_json_logging.py`
- **UvicornAccessLogFilter** (15 connections) — `gen_epix/commondb/config/json_logging.py`
- **.format()** (10 connections) — `gen_epix/commondb/config/json_logging.py`
- **json_logging.py** (9 connections) — `gen_epix/commondb/config/json_logging.py`
- **._normalise_containerlogv2_fields()** (9 connections) — `gen_epix/commondb/config/json_logging.py`
- **Any** (9 connections)
- **_format_payload()** (8 connections) — `test/commondb/unit/logging/test_json_logging.py`
- **._ensure_uvicorn_access_json_formatter()** (7 connections) — `gen_epix/commondb/config/json_logging.py`
- **_make_uvicorn_access_record()** (6 connections) — `test/commondb/unit/logging/test_json_logging.py`
- **test_non_mergeable_json_like_messages_are_kept_as_plain_text()** (6 connections) — `test/commondb/unit/logging/test_json_logging.py`
- **test_uses_secondary_env_fallbacks_when_primary_env_vars_missing()** (6 connections) — `test/commondb/unit/logging/test_json_logging.py`
- **._redact_nested()** (5 connections) — `gen_epix/commondb/config/json_logging.py`
- **._discover_json_formatter()** (5 connections) — `gen_epix/commondb/config/json_logging.py`
- **.filter()** (5 connections) — `gen_epix/commondb/config/json_logging.py`
- **._is_json_formatter()** (5 connections) — `gen_epix/commondb/config/json_logging.py`
- **test_custom_extras_key_is_used_for_extra_fields()** (5 connections) — `test/commondb/unit/logging/test_json_logging.py`
- **test_long_exception_message_is_truncated()** (5 connections) — `test/commondb/unit/logging/test_json_logging.py`
- **test_uses_env_when_constructor_values_missing()** (5 connections) — `test/commondb/unit/logging/test_json_logging.py`
- **test_uvicorn_access_filter_falls_back_to_regex_on_formatted_string()** (5 connections) — `test/commondb/unit/logging/test_json_logging.py`
- **test_uvicorn_access_filter_leaves_unparseable_status_records_untouched()** (5 connections) — `test/commondb/unit/logging/test_json_logging.py`
- **test_uvicorn_access_filter_parses_args_tuple()** (5 connections) — `test/commondb/unit/logging/test_json_logging.py`
- **test_uvicorn_access_filter_passes_through_non_access_records()** (5 connections) — `test/commondb/unit/logging/test_json_logging.py`
- *... and 80 more nodes in this community*

## Relationships

- [Seqdb Demo Data Generation](Seqdb_Demo_Data_Generation.md) (1 shared connections)

## Source Files

- `gen_epix/commondb/config/json_logging.py`
- `test/commondb/unit/logging/test_json_logging.py`

## Audit Trail

- EXTRACTED: 227 (82%)
- INFERRED: 51 (18%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*