# Application Log Items

> 46 nodes · cohesion 0.08

## Key Concepts

- **LogItem** (33 connections) — `gen_epix/fastapp/log.py`
- **test_fastapp_app_log_summarise.py** (26 connections) — `test/fastapp/unit/test_fastapp_app_log_summarise.py`
- **scenario_ids** (15 connections)
- **test_create_log_message_uses_configured_threshold_and_sample_size()** (7 connections) — `test/fastapp/unit/test_fastapp_app_log_summarise.py`
- **test_create_log_message_with_large_command_stays_under_16384_bytes()** (7 connections) — `test/fastapp/unit/test_fastapp_app_log_summarise.py`
- **test_create_log_message_with_summarization_disabled_keeps_full_list()** (7 connections) — `test/fastapp/unit/test_fastapp_app_log_summarise.py`
- **_make_user()** (6 connections) — `test/fastapp/unit/test_fastapp_app_log_summarise.py`
- **test_create_log_message_invalid_bool_config_raises()** (6 connections) — `test/fastapp/unit/test_fastapp_app_log_summarise.py`
- **_LargeListCommand** (5 connections) — `test/fastapp/unit/test_fastapp_app_log_summarise.py`
- **test_large_dict_is_summarised()** (5 connections) — `test/fastapp/unit/test_fastapp_app_log_summarise.py`
- **test_long_exception_message_is_truncated_from_the_middle()** (5 connections) — `test/fastapp/unit/test_fastapp_app_log_summarise.py`
- **test_long_list_is_summarised()** (5 connections) — `test/fastapp/unit/test_fastapp_app_log_summarise.py`
- **test_long_list_respects_configured_max_list_items()** (5 connections) — `test/fastapp/unit/test_fastapp_app_log_summarise.py`
- **test_long_string_is_truncated()** (5 connections) — `test/fastapp/unit/test_fastapp_app_log_summarise.py`
- **test_long_string_respects_configured_max_string_length()** (5 connections) — `test/fastapp/unit/test_fastapp_app_log_summarise.py`
- **test_nested_long_list_is_summarised()** (5 connections) — `test/fastapp/unit/test_fastapp_app_log_summarise.py`
- **test_short_list_is_logged_verbatim()** (5 connections) — `test/fastapp/unit/test_fastapp_app_log_summarise.py`
- **test_short_string_passes_through()** (5 connections) — `test/fastapp/unit/test_fastapp_app_log_summarise.py`
- **test_small_dict_passes_through()** (5 connections) — `test/fastapp/unit/test_fastapp_app_log_summarise.py`
- **test_short_exception_message_passes_through()** (4 connections) — `test/fastapp/unit/test_fastapp_app_log_summarise.py`
- **._custom_json_encoder()** (3 connections) — `gen_epix/fastapp/log.py`
- **.__init__()** (3 connections) — `gen_epix/fastapp/log.py`
- **.__init__()** (3 connections) — `gen_epix/fastapp/log.py`
- **Any** (3 connections)
- **.dumps()** (2 connections) — `gen_epix/fastapp/log.py`
- *... and 21 more nodes in this community*

## Relationships

- [Seqdb Sequence Retrieval Commands](Seqdb_Sequence_Retrieval_Commands.md) (17 shared connections)
- [Auth Protocols & Structured Logging](Auth_Protocols_&_Structured_Logging.md) (12 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (3 shared connections)
- [Domain Registry & ABAC Policies](Domain_Registry_&_ABAC_Policies.md) (3 shared connections)
- [RBAC Service Tests](RBAC_Service_Tests.md) (2 shared connections)
- [Command Exception Handling](Command_Exception_Handling.md) (2 shared connections)
- [Commondb Client](Commondb_Client.md) (1 shared connections)
- [Mock IDP Client](Mock_IDP_Client.md) (1 shared connections)

## Source Files

- `gen_epix/fastapp/log.py`
- `test/fastapp/unit/test_fastapp_app_log_summarise.py`

## Audit Trail

- EXTRACTED: 85 (70%)
- INFERRED: 36 (30%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*