# test_cfg_log_level.py

> 23 nodes

## Key Concepts

- **test_cfg_log_level.py** (12 connections) — `test/commondb/unit/logging/test_cfg_log_level.py`
- **_DummyLogger** (9 connections) — `test/commondb/unit/logging/test_cfg_log_level.py`
- **_build_test_fixture()** (9 connections) — `test/commondb/unit/logging/test_cfg_log_level.py`
- **_patch_logging_get_logger()** (8 connections) — `test/commondb/unit/logging/test_cfg_log_level.py`
- **test_set_log_level_diagnostic_precedence_arg_over_env_and_settings()** (7 connections) — `test/commondb/unit/logging/test_cfg_log_level.py`
- **test_set_log_level_diagnostic_precedence_env_over_settings()** (7 connections) — `test/commondb/unit/logging/test_cfg_log_level.py`
- **test_set_log_level_diagnostic_precedence_settings_when_env_absent()** (7 connections) — `test/commondb/unit/logging/test_cfg_log_level.py`
- **_extract_diagnostic_payload()** (6 connections) — `test/commondb/unit/logging/test_cfg_log_level.py`
- **_patch_runtime_logger_dict()** (6 connections) — `test/commondb/unit/logging/test_cfg_log_level.py`
- **test_set_log_level_preserves_pinned_third_party_loggers_without_handler_overwrite()** (6 connections) — `test/commondb/unit/logging/test_cfg_log_level.py`
- **MonkeyPatch** (6 connections)
- **_DummyHandler** (5 connections) — `test/commondb/unit/logging/test_cfg_log_level.py`
- **scenario_ids** (4 connections)
- **.__init__()** (2 connections) — `test/commondb/unit/logging/test_cfg_log_level.py`
- **.__init__()** (1 connections) — `test/commondb/unit/logging/test_cfg_log_level.py`
- **.setLevel()** (1 connections) — `test/commondb/unit/logging/test_cfg_log_level.py`
- **.debug()** (1 connections) — `test/commondb/unit/logging/test_cfg_log_level.py`
- **.info()** (1 connections) — `test/commondb/unit/logging/test_cfg_log_level.py`
- **.setLevel()** (1 connections) — `test/commondb/unit/logging/test_cfg_log_level.py`
- **Return the latest APPLIED_LOG_LEVEL diagnostic payload from a dummy logger.** (1 connections) — `test/commondb/unit/logging/test_cfg_log_level.py`
- **Create an AppCfg test instance with controllable dummy loggers and handlers.** (1 connections) — `test/commondb/unit/logging/test_cfg_log_level.py`
- **Patch logging.getLogger so tests can inspect logger state deterministically.** (1 connections) — `test/commondb/unit/logging/test_cfg_log_level.py`
- **Patch runtime logger registry with synthetic logger names for descendant tests.** (1 connections) — `test/commondb/unit/logging/test_cfg_log_level.py`

## Relationships

- [AppCfg](AppCfg.md) (2 shared connections)
- [BaseAppCfg](BaseAppCfg.md) (1 shared connections)

## Source Files

- `test/commondb/unit/logging/test_cfg_log_level.py`

## Audit Trail

- EXTRACTED: 52 (98%)
- INFERRED: 1 (2%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*