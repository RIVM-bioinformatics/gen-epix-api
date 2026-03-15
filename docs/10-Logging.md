Creation Date: March 2, 2026

# Logging

This chapter documents the current logging setup across all app variants (`CASEDB`, `SEQDB`, `OMOPDB`, `COMMONDB`), including configuration files, JSON formatting behavior, debug-level behavior, and runtime load/overwrite precedence.

---

## 1. Logging Architecture Overview

The logging stack has three layers:

1. YAML logging config (`logging.yaml`) defines handlers, formatters, filters, logger namespaces, and baseline levels.
2. `JsonFormatter` and `UvicornAccessLogFilter` convert records to structured, single-line JSON and normalize access logs.
3. `AppCfg.set_log_level()` applies runtime level control with explicit pinned logger exceptions.

(Source: `gen_epix/commondb/config/cfg.py#L203-L214`; Source: `gen_epix/commondb/config/json_logging.py#L89-L303`; Source: `gen_epix/commondb/config/cfg.py#L352-L405`)

---

## 2. Config Files and Their Roles

Per app (`casedb`, `seqdb`, `omopdb`, `commondb`) there are two logging YAML variants:

- `config/logging.yaml`: production/default baseline (root and app loggers at `INFO`).
- `config/logging.debug.yaml`: debug variant with multiple `DEBUG` levels.
- `config/feature_flags.yaml`: feature flag configuration.

The default runtime bootstrap points to `logging.yaml`, not `logging.debug.yaml`.

(Source: `gen_epix/casedb/config/logging.yaml#L1-L78`; Source: `gen_epix/seqdb/config/logging.yaml#L1-L78`; Source: `gen_epix/omopdb/config/logging.yaml#L1-L78`; Source: `gen_epix/commondb/config/logging.yaml#L1-L78`; Source: `gen_epix/commondb/domain/util.py#L118-L119`; Source: `gen_epix/casedb/config/feature_flags.yaml#L1-L3`; Source: `gen_epix/seqdb/config/feature_flags.yaml#L1-L3`; Source: `gen_epix/omopdb/config/feature_flags.yaml#L1-L3`; Source: `gen_epix/commondb/config/feature_flags.yaml#L1-L3`)

In each app `settings.toml`, the baseline setting is:

```toml
[log]
level = "INFO"
```

and command-object list summarization is enabled:

```toml
[log.command_object_summarization]
enabled = true
max_list_items = 10
sample_items = 3
```

(Source: `gen_epix/casedb/config/settings.toml#L46-L52`; Source: `gen_epix/seqdb/config/settings.toml#L46-L52`; Source: `gen_epix/omopdb/config/settings.toml#L46-L52`; Source: `gen_epix/commondb/config/settings.toml#L46-L52`)

---

## 3. JSON Formatter Behavior

`gen_epix/commondb/config/json_logging.py` provides the shared formatter and access-log filter used by all services.

### Envelope and output guarantees

- Emits single-line JSON using `json.dumps(..., default=str)`.
- Always includes envelope fields (`ts`, `level`, `logger`), plus optional `service` and `environment`.
- Uses `extras_key` (default `props`) for non-reserved extra fields.

(Source: `gen_epix/commondb/config/json_logging.py#L146-L177`; Source: `gen_epix/commondb/config/json_logging.py#L226-L303`)

### Message merge and normalization

- If `merge_message_json=true`, JSON messages are parsed and merged into the top-level payload.
- Envelope fields are re-enforced after merge (cannot be silently overwritten by payload keys).
- `content` is normalized into `message` when needed.

(Source: `gen_epix/commondb/config/json_logging.py#L246-L269`)

### Sensitive data handling

- Redacts configured sensitive key-value material in:
  - free-text message strings (`key=value` form)
  - nested dict/list payloads and extras by key name
- Default redaction token is `[REDACTED]`.

(Source: `gen_epix/commondb/config/json_logging.py#L39-L87`; Source: `gen_epix/commondb/config/json_logging.py#L154-L225`)

### Exception handling

- Adds structured `exception` object when `exc_info` exists.
- Truncates overly long stack traces with a configurable limit (`max_stacktrace_length`, default 8000).

(Source: `gen_epix/commondb/config/json_logging.py#L155-L158`; Source: `gen_epix/commondb/config/json_logging.py#L271-L285`)

### Uvicorn access normalization

- `UvicornAccessLogFilter` converts `uvicorn.access` records into structured `http` fields (`client`, `method`, `path`, `version`, `status`).
- Access-log `message` is normalized to `http.access <METHOD> <PATH> <STATUS>` so Azure Monitor/Grafana `LogMessage` remains informative while structured `http.*` fields are still emitted.
- Includes regex fallback when access logs are already interpolated text.

(Source: `gen_epix/commondb/config/json_logging.py#L89-L143`)

---

## 4. Logger Namespaces and Default Levels

In each production `logging.yaml`:

- App loggers (`*.setup`, `*.service`, `*.app`, `*.api`, `*.external`) are configured at `INFO`.
- `uvicorn.error` and `uvicorn.access` are `INFO`; `uvicorn.access` has `uvicorn_access_structured` filter.
- SQLAlchemy namespaces are pinned at `WARNING`:
  - `sqlalchemy.engine`
  - `sqlalchemy.pool`
- Other pinned third-party loggers:
  - `httpx` at `INFO`
  - `asyncio` at `WARNING`
- Root logger is `INFO`.

(Source: `gen_epix/casedb/config/logging.yaml#L24-L78`; Source: `gen_epix/seqdb/config/logging.yaml#L24-L78`; Source: `gen_epix/omopdb/config/logging.yaml#L24-L78`; Source: `gen_epix/commondb/config/logging.yaml#L24-L78`)

Contract tests enforce these expectations on all production `logging.yaml` files.

(Source: `test/commondb/unit/domain/test_logging_yaml.py#L1-L113`)

### 4.1 Third-party logger default behavior vs explicit management

By default, third-party libraries use Python logger names such as:

- `sqlalchemy.engine.Engine`
- `sqlalchemy.pool.impl.QueuePool`
- `httpx`
- `asyncio`
- `uvicorn.*`

If a third-party logger is not explicitly configured in `logging.yaml`, behavior is governed by standard logging propagation:

1. The third-party logger emits a record.
2. If it has no handler and `propagate=True`, the record bubbles up to ancestor/root logger handlers.
3. In this project, root routes to `console` which uses `JsonFormatter`, so the record is still emitted as structured JSON.

This means third-party logs are typically still JSON-formatted even when the logger itself is not explicitly listed, because root has the JSON handler.

(Source: `gen_epix/commondb/config/logging.yaml#L2-L23`; Source: `gen_epix/commondb/config/logging.yaml#L76-L78`)

Current explicit management strengthens that default behavior:

- `disable_existing_loggers: false` keeps existing library loggers active.
- Known noisy/important third-party namespaces are explicitly declared with `handlers: [console]` and `propagate: false`, making routing deterministic.
- Their baseline levels are pinned in YAML and preserved by runtime level updates:
  - `sqlalchemy.engine` -> `WARNING`
  - `sqlalchemy.pool` -> `WARNING`
  - `httpx` -> `INFO`
  - `asyncio` -> `WARNING`
- Runtime descendants of pinned SQLAlchemy namespaces are also pinned (`sqlalchemy.engine.Engine`, `sqlalchemy.pool.impl.QueuePool`) to avoid child logger leakage when global level is raised.

(Source: `gen_epix/casedb/config/logging.yaml#L2-L78`; Source: `gen_epix/seqdb/config/logging.yaml#L2-L78`; Source: `gen_epix/omopdb/config/logging.yaml#L2-L78`; Source: `gen_epix/commondb/config/logging.yaml#L2-L78`; Source: `gen_epix/commondb/config/cfg.py#L20-L35`; Source: `gen_epix/commondb/config/cfg.py#L374-L405`; Source: `test/commondb/unit/domain/test_cfg_log_level.py#L22-L79`)

---

## 5. Load and Overwrite Behavior (Important)

This is the effective precedence that can influence what actually gets logged.

### Step A: Logging config file selection

`set_env_variables(...)` writes:

- `<APP>_SETTINGS_FILES`
- `<APP>_LOG_CONFIG_FILE` -> `<app>/config/logging.yaml`

`run.py` passes that file to `uvicorn.run(..., log_config=...)`.

(Source: `gen_epix/commondb/domain/util.py#L115-L119`; Source: `run.py#L92-L110`)

### Step B: AppCfg startup order

`AppCfg.__init__()` does:

1. `_init_configure_loggers()` -> applies YAML `dictConfig`
2. `set_log_level()` (pre-settings)
3. load Dynaconf settings
4. `set_log_level()` (post-settings)

(Source: `gen_epix/commondb/config/cfg.py#L175-L186`; Source: `gen_epix/commondb/config/cfg.py#L203-L214`)

### Step C: Log-level precedence in `set_log_level()`

When `set_log_level(log_level=None)` is used:

1. `<APP>_LOG_LEVEL` env var wins, if present.
2. Else `[log].level` from loaded Dynaconf settings is used.
3. Else no change.

(Source: `gen_epix/commondb/config/cfg.py#L355-L364`)

### Step D: Pinned exceptions (not globally overwritten)

Even if global effective level is changed (for example to `DEBUG`), pinned logger groups keep their YAML level:

- Third-party pinned namespaces: `sqlalchemy.engine`, `sqlalchemy.pool`, `httpx`, `asyncio`.
- Runtime descendants of pinned third-party namespaces are also pinned (for example `sqlalchemy.engine.Engine`, `sqlalchemy.pool.impl.QueuePool`).
- Local app namespaces with suffixes `setup`, `service`, `app`, `api`, `external` are pinned to YAML levels using the app logger prefix.

(Source: `gen_epix/commondb/config/cfg.py#L20-L35`; Source: `gen_epix/commondb/config/cfg.py#L374-L405`; Source: `test/commondb/unit/domain/test_cfg_log_level.py#L22-L79`)

### Step E: Dynaconf runtime settings overrides

Dynaconf is loaded with:

- `envvar_prefix=<APP>`
- `settings_files=[...]`
- `merge_enabled=True`
- nested env separator `__`

So settings keys (including `log.level`) can also be overridden by Dynaconf-style environment variables (for example `<APP>__LOG__LEVEL`), which then feed into step C as `self._cfg["log"]["level"]`.

(Source: `gen_epix/commondb/config/settings_manager.py#L70-L76`; Source: `gen_epix/commondb/config/cfg.py#L360-L363`)

---

## 6. Debug Logging Modes

There are two practical ways debug output can appear:

1. Using `logging.debug.yaml` instead of `logging.yaml` (via `<APP>_LOG_CONFIG_FILE` override).
2. Setting `<APP>_LOG_LEVEL=DEBUG` (or Dynaconf-equivalent settings override).

With current runtime logic, pinned loggers remain at their configured levels, so third-party SQLAlchemy debug chatter is intentionally suppressed even when global level increases.

(Source: `gen_epix/casedb/config/logging.debug.yaml#L1-L39`; Source: `gen_epix/commondb/config/cfg.py#L355-L405`)

---

## 7. Operational Checklist

When observed log levels do not match expectation, verify in this order:

1. Effective `<APP>_LOG_CONFIG_FILE` value (should point to `logging.yaml` unless intentionally debugging).
2. Effective `<APP>_LOG_LEVEL` env var (unset or `INFO` in normal operation).
3. Effective Dynaconf overrides (for example `<APP>__LOG__LEVEL`).
4. App-specific `settings.toml` `[log].level`.
5. Whether the process/container was restarted after config changes.

---

## Evidence Sources

- `gen_epix/commondb/config/json_logging.py#L1-L303`
- `gen_epix/commondb/config/cfg.py#L20-L405`
- `gen_epix/commondb/config/settings_manager.py#L27-L76`
- `gen_epix/commondb/domain/util.py#L30-L119`
- `run.py#L92-L110`
- `gen_epix/casedb/config/logging.yaml#L1-L78`
- `gen_epix/seqdb/config/logging.yaml#L1-L78`
- `gen_epix/omopdb/config/logging.yaml#L1-L78`
- `gen_epix/commondb/config/logging.yaml#L1-L78`
- `gen_epix/casedb/config/logging.debug.yaml#L1-L39`
- `gen_epix/seqdb/config/logging.debug.yaml#L1-L39`
- `gen_epix/omopdb/config/logging.debug.yaml#L1-L39`
- `gen_epix/commondb/config/logging.debug.yaml#L1-L39`
- `gen_epix/casedb/config/settings.toml#L46-L52`
- `gen_epix/seqdb/config/settings.toml#L46-L52`
- `gen_epix/omopdb/config/settings.toml#L46-L52`
- `gen_epix/commondb/config/settings.toml#L46-L52`
- `gen_epix/casedb/config/feature_flags.toml#L1-L3`
- `gen_epix/seqdb/config/feature_flags.toml#L1-L3`
- `gen_epix/omopdb/config/feature_flags.toml#L1-L3`
- `gen_epix/commondb/config/feature_flags.toml#L1-L3`
- `test/commondb/unit/domain/test_logging_yaml.py#L1-L113`
- `test/commondb/unit/domain/test_cfg_log_level.py#L22-L79`
