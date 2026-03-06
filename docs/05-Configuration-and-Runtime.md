Creation Date: March 1, 2026

# Configuration & Runtime

This chapter covers the settings model, IDP and repository modes, startup lifecycle, logging, and port assignments. It consolidates configuration detail from multiple source documents into a single reference.

---

## 1. Settings Model

Configuration loading is Dynaconf-based and environment-driven. The process is staged:

1. **Logging configuration** is loaded from `<APP>_LOG_CONFIG_FILE`. (Source: `gen_epix/commondb/config/cfg.py#L188-L215`)
2. **Settings** are loaded from `<APP>_SETTINGS_FILES` via a `SettingsManager`. Dynaconf merges the files in order — later files override earlier ones. (Source: `gen_epix/commondb/config/settings_manager.py#L43-L77`)
3. **Runtime env vars** with `__` separators override any nested key (e.g. `COMMONDB__LOG__LEVEL`). (Source: `gen_epix/commondb/config/settings_manager.py#L15-L17`; Source: `gen_epix/commondb/config/settings_manager.py#L71-L74`)
4. **Validation** — string-based class references and factory names are resolved into actual Python objects. Service and repository classes are loaded via `importlib.import_module`. (Source: `gen_epix/commondb/config/cfg.py#L218-L269`)

Missing settings files fail fast (`FileNotFoundError`). This makes misconfiguration a startup failure rather than a silent foot-gun. (Source: `gen_epix/commondb/config/settings_manager.py#L63-L67`)

### Settings file categories

| Category | Description |
|----------|-------------|
| `settings.toml` | Base config: host, port, HTTP headers, service class names, default factories |
| `settings.repository.dict.toml` / `settings.repository.sa.toml` | Swaps in Dict or SQLAlchemy repository classes per service type |
| `.example.secrets.*` files | Connection strings, file paths, IdP tokens — never checked in; supplied per environment |

(Source: `gen_epix/casedb/config/settings.toml#L1-L4`; Source: `gen_epix/casedb/config/settings.repository.dict.toml#L1-L27`)

---

## 2. IDP Modes

The system supports three identity provider modes, selected at startup:

| Mode | Config file | Behavior |
|------|-------------|----------|
| `IDPS` | `config/identity_providers.toml` | Configured OIDC providers with discovery metadata, claim mapping |
| `MOCK` | `config/mock_identity_provider.toml` | Local mock OIDC settings — bypasses real token validation |
| `NONE` | `config/no_identity_providers.toml` | No-provider path; falls back to root user dependencies |

(Source: `gen_epix/commondb/util.py#L78-L85`; Source: `config/identity_providers.toml#L1-L34`; Source: `config/mock_identity_provider.toml#L1-L16`; Source: `config/no_identity_providers.toml#L1-L1`)

**Security Note:** `NONE` mode is a real configuration path, not an error fallback. It materially changes trust posture. Before exposing any instance beyond a trusted environment, verify both IDP mode and repository mode. See [03-Security](./03-Security.md) for full risk analysis.

---

## 3. Repository Modes

Repository type is configuration-driven. The supported modes are:

| Mode | Description |
|------|-------------|
| `DICT_DEMO` | In-memory dict backend pre-loaded with demo data |
| `DICT_EMPTY` | In-memory dict backend, empty |
| `SA_SQLITE_DEMO` | SQLAlchemy with SQLite, pre-loaded with demo data |
| `SA_SQLITE_EMPTY` | SQLAlchemy with SQLite, empty |
| `SA_SQL` | SQLAlchemy with SQL Server (production) |

(Source: `gen_epix/commondb/domain/enum.py#L107-L113`; Source: `gen_epix/commondb/base_env.py#L66-L93`)

Runtime repository type handling is bounded to `DICT`, `SA_SQLITE`, and `SA_SQL`. Unsupported modes fail at composition time with `NotImplementedError`.

---

## 4. Startup Lifecycle

Local bootstrap is controlled by `run.py`, which orchestrates:

1. Select app type, IDP mode, and repository mode.
2. `set_env_variables(...)` assembles the ordered list of TOML settings files and writes them into `<APP>_SETTINGS_FILES` and `<APP>_LOG_CONFIG_FILE`. (Source: `gen_epix/commondb/util.py#L74-L119`)
3. Start uvicorn with reload enabled and optional TLS (if `cert/key.pem` and `cert/cert.pem` exist). (Source: `run.py#L82-L107`)

Configuration load is then staged within the app:
- `AppCfg` → logging config → settings loading → settings validation.
- `AppComposer` → repositories + services + user dependencies + policies.
- `create_fast_api` → middleware + routers under `/v1` + root redirect.

If startup fails at composition time, the system logs setup failure and re-raises, so deployment logs should show composition-stage failures explicitly. (Source: `gen_epix/commondb/env.py#L185-L197`)

Developer Note: `CASEDB` env setup also sets `SEQDB` env variables, which can affect multi-app sessions. (Source: `gen_epix/commondb/util.py#L61-L64`)

---

## 5. Port Assignments

| App | Port |
|-----|------|
| CASEDB | 8000 |
| SEQDB | 8001 |
| OMOPDB | 8002 |
| COMMONDB | 8010 |

(Source: `run.py#L17-L38`)

Local app host/port defaults are hard-coded in `Run.APP_URI` unless code/config is changed. All API routes are prefixed with `/v1`. The root path `/` redirects to the configured default route.

---

## 6. Middleware Posture

In non-debug mode, the API shell applies:
- Rate limiting (10 req/s per bearer token, falling back to IP)
- Gzip compression (≥ 1000 bytes at compression level 5)
- Response header hardening (CSP, HSTS, X-Frame-Options, etc.)
- Auth exception handling middleware

In debug mode, this hardening is disabled, changing the HTTP protection posture. (Source: `gen_epix/commondb/app_setup.py#L75-L109`)

---

## 7. Logging

Logging is JSON-formatted to stdout via `logging.StreamHandler`:

| Namespace | Scope |
|-----------|-------|
| `setup` | Startup/shutdown lifecycle |
| `api` | Per-request HTTP events |
| `app` | Application-level events (command dispatch, policy checks) |
| `service` | Service-layer events (business logic, repository calls) |
| `external` | External dependencies |

Root default level is `INFO`. (Source: `gen_epix/commondb/config/logging.yaml#L1-L35`)

### Command Object Summarization

Command payloads can contain very large list fields. To keep structured log
records bounded for downstream sinks, command-object list summarization is
configurable under `[log.command_object_summarization]` in each app's
`settings.toml`:

- `enabled` (bool): turns summarization on/off.
- `max_list_items` (int): lists with more than this many items are summarized.
- `sample_items` (int): number of list elements copied into `_sample`.

Current defaults in app settings are:

```toml
[log.command_object_summarization]
enabled = true
max_list_items = 10
sample_items = 3
```

Environment overrides follow the standard Dynaconf `__` convention. Example:

```bash
COMMONDB__LOG__COMMAND_OBJECT_SUMMARIZATION__MAX_LIST_ITEMS=20
```

The most operationally useful logs mark phase transitions or control points:
- IDP initialization/retry (trust anchors available vs degraded)
- User-verification warnings (auth dependency failures)
- `NOT_AUTHORIZED` events (command policy denials)

---

## 8. Multi-Service Startup

### Platform helper

```
python run.py api_platform_local_mock_dict_demo
```

Starts OAuth (port 9000), SeqDB (8003), and CaseDB (8000) together. CaseDB calls SeqDB via the OAuth server using client-credentials flow. This command does **not** start CommonDB or OmopDB, and does not have hot-reload (servers run as `ServerManager` subprocesses). (Source: `run.py#L109-L117`)

### ETL Data Loading

```
python run.py etl_load_demo_data <app_type|all>
```

Prepares environment context and transfers demo data from dict repositories into SQL repositories when connection checks pass. (Source: `run.py#L134-L160`; Source: `etl.py#L72-L148`)

---

## Evidence Sources

- `run.py#L17-L200`
- `gen_epix/commondb/util.py#L61-L119`
- `gen_epix/commondb/config/cfg.py#L155-L269`
- `gen_epix/commondb/config/settings_manager.py#L15-L77`
- `gen_epix/commondb/config/logging.yaml#L1-L35`
- `gen_epix/commondb/env.py#L103-L197`
- `gen_epix/commondb/base_env.py#L66-L93`
- `gen_epix/commondb/app_setup.py#L75-L126`
- `gen_epix/commondb/domain/enum.py#L82-L113`
- `gen_epix/casedb/config/settings.toml#L1-L4`
- `gen_epix/casedb/config/settings.repository.dict.toml#L1-L27`
- `config/identity_providers.toml#L1-L34`
- `config/mock_identity_provider.toml#L1-L16`
- `config/no_identity_providers.toml#L1-L1`
- `etl.py#L72-L148`
