Creation Date: 2026-03-01

# Configuration & Runtime

This chapter covers the settings model, IDP and repository modes, startup lifecycle, logging, and port assignments. It consolidates configuration detail from multiple source documents into a single reference.

---

## 1. Settings Model

Configuration loading is Dynaconf-based and environment-driven, layered on
top of hardcoded Python defaults. The process is staged:

1. **Hardcoded defaults** — `AppCfg._DEFAULT_SETTINGS` (a plain class
   attribute, not a file) supplies the values shared across every app:
   HTTP headers, log format, the `service.defaults`/`repository.defaults`
   factory and connection shape, and commondb's own module paths, port,
   and role, since commondb uses plain `AppCfg` directly. `CasedbAppCfg`,
   `SeqdbAppCfg`, and `OmopdbAppCfg` each declare their own
   `_DEFAULT_SETTINGS`, built by recursively merging their deltas (port,
   module paths, role, extra services) on top of the base dict. See
   §1a below.
2. **Logging configuration** is loaded from `<APP>_LOG_CONFIG_FILE`. (Source: `gen_epix/commondb/config/cfg.py#L188-L215`)
3. **Settings files** are loaded from `<APP>_SETTINGS_FILES` via a `SettingsManager`, with the hardcoded defaults given the lowest precedence. Dynaconf merges the files in order — later files override earlier ones, and any of them can override the defaults. (Source: `gen_epix/commondb/config/settings_manager.py#L31-L120`)
4. **Runtime env vars** with `__` separators override any nested key, including a file's own value (e.g. `COMMONDB__LOG__LEVEL`). (Source: `gen_epix/commondb/config/settings_manager.py#L15-L17`)
5. **Validation** — a set of `dynaconf.Validator` objects run immediately once settings files and environment variables are merged, rejecting values that don't fit their expected type, allowed set, or presence, with a message naming the exact key. Only after validation passes are string-based class references and factory names resolved into actual Python objects: service and repository classes are loaded via `importlib.import_module`, with a clear error naming the app, the key, and the module/class string if that import fails. (Source: `gen_epix/commondb/config/cfg.py`, `_get_validators`/`_init_validate_settings`)

Missing settings files fail fast (`FileNotFoundError`). This makes misconfiguration a startup failure rather than a silent foot-gun. (Source: `gen_epix/commondb/config/settings_manager.py#L63-L67`)

### Settings file categories

| Category | Description |
|----------|-------------|
| `settings.toml` | Overrides for the app-agnostic parts of `AppCfg._DEFAULT_SETTINGS` not otherwise covered below (rarely needed, since those defaults are already correct for each app) |
| `settings.repository.dict.toml` / `settings.repository.sa_sqlite.toml` | Shared per-backend-family repository config (type, module/class_name where applicable, and a per-repo file-path template) for the `DICT_*`/`SA_SQLITE_*` repository modes. Not named `.secrets.` — none of these files contain a credential |
| `settings.repository.{dict,sa_sqlite}.{demo,empty}.toml` | One line each, setting that backend family's file-path template to the demo or empty dataset. Not named `.secrets.` either, for the same reason |
| `.example.secrets.repository.sa_sql.toml` | Copy-first template for `SA_SQL`'s credentials — the one file in this group that actually has credential-shaped fields (uid/pwd, mostly commented out). `SA_SQL` itself needs no file at all for local/dev use, since its dummy values already live in `AppCfg._DEFAULT_SETTINGS`; copying this template to `secrets.repository.sa_sql.toml` (gitignored) is how a deployment overrides them via a file instead of environment variables |
| Root `config/identity_providers.toml` / `mock_identity_provider.toml` / `no_identity_providers.toml` | Selected per `DevIdpConfig` — genuine per-mode choices, not filler defaults |

`SA_SQL` is the baseline repository backend: it needs no settings file at
all, since `AppCfg._DEFAULT_SETTINGS["repository"]` already describes it
completely, including credentials that match the SA password this repo's
own docker-compose SQL Server container is provisioned with. Selecting
`DICT_*` or `SA_SQLITE_*` layers the two files above on top of that
default. See §1b below for the full precedence and a documented side
effect of that layering.

(Source: `gen_epix/commondb/config/cfg.py`, `AppCfg._DEFAULT_SETTINGS`; Source: `gen_epix/casedb/config/settings.repository.dict.toml`)

### 1a. Hardcoded defaults and per-app configuration classes

| App | `AppCfg` subclass | Location | Baked-in deltas over the base defaults |
|-----|--------------------|----------|------------------------------------------|
| commondb | `AppCfg` (no subclass) | `gen_epix/commondb/config/cfg.py` | — (this app's values *are* the base defaults) |
| casedb | `CasedbAppCfg` | `gen_epix/casedb/config/cfg.py` | port 8000, `id_factory="ULID"` (every other app uses `UUID4`), `CASEDB_ORG_USER` role, `case`/`geo`/`ontology` services, the seqdb client block |
| seqdb | `SeqdbAppCfg` | `gen_epix/seqdb/config/cfg.py` | port 8001, `SEQDB_ORG_USER` role, `seq`/`file` services |
| omopdb | `OmopdbAppCfg` | `gen_epix/omopdb/config/cfg.py` | port 8002, `OMOPDB_ORG_USER` role, `omop` service |

Each subclass's `_DEFAULT_SETTINGS` is built once, at class-definition
time, via `AppCfg._deep_merge(AppCfg._DEFAULT_SETTINGS, {...own deltas...})`
— a recursive dict merge (dict-vs-dict keys recurse, anything else is
replaced wholesale). Each app's `app.py` constructs its subclass with no
arguments (e.g. `APP_CFG = CasedbAppCfg()`); the subclass's `__init__`
supplies its own name and enums as constructor defaults, so any keyword
argument `AppCfg.__init__` accepts — including `settings_files=[...]` for
isolated test construction — still works as an override.

A small number of call sites construct configuration generically, for a
caller-supplied app type rather than one hardcoded app (the ETL script,
a couple of test/demo-data helpers): these resolve the right subclass via
`gen_epix.commondb.domain.util.get_app_cfg_class(app_type)` instead of
constructing `AppCfg` directly, which would otherwise silently pick up
commondb's own defaults regardless of which app is actually being
configured.

### 1b. Repository configuration: files and precedence

`repository.defaults.type = "SA_SQL"` and its connection details are
always present, supplied by `AppCfg._DEFAULT_SETTINGS`, active whenever
`DevRepositoryConfig.SA_SQL` is selected without any further file.
Choosing `DICT_DEMO`, `DICT_EMPTY`, `SA_SQLITE_DEMO`, or `SA_SQLITE_EMPTY`
layers two files on top of that default, assembled by `set_env_variables`:

- **`SA_SQL`**: `secrets.repository.sa_sql.toml` is loaded only if
  present — a local, gitignored copy of `.example.secrets.repository.sa_sql.toml`
  with its uid/pwd/server uncommented and filled in. Its absence is the
  common case: `AppCfg._DEFAULT_SETTINGS["repository"]` already describes
  a working `SA_SQL` configuration, so most local/dev use needs no file at
  all here, only the usual environment-variable overrides.
- **`DICT_DEMO` / `DICT_EMPTY`**: `settings.repository.dict.toml`
  (shared: `type = "DICT"`, `dir`, and every repo's `module`/`class_name`/
  `file` — the `file` value is a template referencing
  `{this.repository.defaults.props.variant}`, not a literal filename),
  then `settings.repository.dict.demo.toml` or
  `settings.repository.dict.empty.toml` (one line each:
  `variant = "full"` or `variant = "empty"`), which resolves every repo's
  `file` template at once. `@format` strings resolve against the
  fully-merged settings at read time, not at each file's own parse time,
  so load order between the two files does not matter for this to work.
- **`SA_SQLITE_DEMO` / `SA_SQLITE_EMPTY`**: the same two-file pattern with
  `settings.repository.sa_sqlite.toml` (`type = "SA_SQLITE"`; no
  module/class_name override, since SA_SQLITE reuses the SA_SQL default's
  repository classes) plus a one-line `variant` file.

**A known, accepted side effect**: because `AppCfg._DEFAULT_SETTINGS` is
always the lowest layer, switching to `DICT_DEMO` does not *remove*
`repository.defaults.props.driver`/`server`/`uid`/`pwd` — Dynaconf's
merge is per-key, not a whole-block replacement, so those SA_SQL-only
fields remain present, unused, alongside the new `dir`/`variant` keys. No
repository class ever reads them in DICT/SA_SQLITE mode, so this is
harmless at runtime; it does mean a `to_toml()` export (§1c) of a
DICT-mode config still shows those fields. Per-repo `connection_string`
is not duplicated for this same reason: it is set once, at
`repository.defaults.props`, and `AppCfg._init_validate_settings`'s
existing `repository.defaults | repository.<x>` merge takes the whole
`props` dict from whichever side has it — a repo with no `props` of its
own falls through to the default `connection_string` entirely, and a
repo whose `props` are overridden (a `file` path) replaces it entirely,
rather than the stale `connection_string` coexisting alongside `file`.

### 1c. Exporting resolved config

`AppCfg.to_toml()` / `AppCfg.to_dict()` serialize the fully-resolved
configuration (defaults, settings files, and environment variables
merged) for inspection or migration to another environment. By default
(`resolved=False`) they return the pre-validation snapshot — every value
still a plain string, safe to write to disk and reload as a settings
file. With `resolved=True`, they return a display-only copy of the
post-validation config, with non-serializable values (imported classes,
resolved factory objects, enum members) replaced by their `repr()` — not
meant to be reloaded.

### 1d. Typed configuration access

`AppCfg.cfg` (and, on `CasedbAppCfg`, the wider `resolved_cfg`) returns
the same live Dynaconf object every call site already reads via
`cfg["service"]["defaults"]`-style subscripting — but its *static* type
is now a `TypedDict` (`gen_epix/commondb/config/cfg_types.py`, one per
app), so a renamed or missing config key is a type-checker error rather
than a runtime one, with no change to how the value is actually read.
`TypedDict` does not support attribute-style access
(`cfg.app.debug`) the way Dynaconf's `Box` does — every call site uses
subscript access (`cfg["app"]["debug"]`).

### 1e. Feature flags

Feature-flag keys are enum members, not bare strings:
`gen_epix.commondb.domain.enum.FeatureFlag` holds the flags shared by
every app (`ALLOW_DELETE_ALL_OPERATIONAL_DATA`, `UPDATE_OWN_ORGANIZATION`,
`AUTO_CREATE_NEW_USERS`), and casedb additionally has
`gen_epix.casedb.domain.enum.CasedbFeatureFlag` (`DISABLE_UPLOAD`) for a
flag no other app uses — a standalone enum rather than a subclass, since
Python does not allow adding members to a subclass of an `Enum` that
already has any. `App.get_feature_flag`/`set_feature_flag` accept only
`Enum` members, not strings, so a typo or a stale rename is a static or
import-time error instead of a silently-ignored lookup. To add a new
flag: add a member to the enum it conceptually belongs to (commondb's, or
a new per-app one following the `CasedbFeatureFlag` pattern), whose
`.value` matches the `[feature_flags]` TOML key exactly; `AppComposer`
converts every `[feature_flags]` key into its matching enum member at
startup and raises a clear error for any key it doesn't recognize.

### Operational-data reset

`allow_delete_all_operational_data` defaults to `false`. When enabled for casedb,
seqdb, or omopdb, that application's OpenAPI document includes
`DELETE /v1/operational_data`. Only ROOT may call it. The operation deletes that
application's operational records and retains common organization data and
app-specific reference data.

Treat reset as a maintenance operation: pause uploads, imports, background jobs,
and other writers; call the endpoint; then resume writers after a successful 204
response. The endpoint is synchronous and idempotent. A missing endpoint means the
flag is disabled or the server version does not support this feature. Each app is
reset independently; the endpoint does not call the other applications.

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

Current defaults in app settings are:

```toml
[log.command_object_summarization]
enabled = true
max_list_items = 3
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

Starts OAuth (port 9000), seqdb (8003), and casedb (8000) together. casedb calls seqdb via the OAuth server using client-credentials flow. This command does **not** start commondb or omopdb, and does not have hot-reload (servers run as `ServerManager` subprocesses). (Source: `run.py#L109-L117`)

### ETL Data Loading

```
python run.py etl_load_demo_data <app_type|all>
```

Prepares environment context and transfers demo data from dict repositories into SQL repositories when connection checks pass. (Source: `run.py#L134-L160`; Source: `etl.py#L72-L148`)

---

## Evidence Sources

- `run.py`
- `gen_epix/commondb/domain/util.py` (`set_env_variables`, `get_app_cfg_class`)
- `gen_epix/commondb/config/cfg.py` (`AppCfg`, `_DEFAULT_SETTINGS`, `_get_validators`, `to_toml`/`to_dict`)
- `gen_epix/commondb/config/cfg_types.py`
- `gen_epix/commondb/config/settings_manager.py`
- `gen_epix/commondb/config/logging.yaml`
- `gen_epix/commondb/env.py` (`AppComposer.compose_application`, feature-flag conversion)
- `gen_epix/commondb/base_env.py`
- `gen_epix/commondb/app_setup.py`
- `gen_epix/commondb/domain/enum.py` (`FeatureFlag`, `FEATURE_FLAG_TOML_KEYS`)
- `gen_epix/casedb/config/cfg.py`, `gen_epix/casedb/config/cfg_types.py`
- `gen_epix/casedb/domain/enum.py` (`CasedbFeatureFlag`)
- `gen_epix/casedb/config/settings.repository.dict.toml`
- `gen_epix/casedb/config/.example.secrets.repository.sa_sql.toml`
- `config/identity_providers.toml`
- `config/mock_identity_provider.toml`
- `config/no_identity_providers.toml`
- `etl.py`
