Creation Date: March 1, 2026

# CLI Reference — run.py

`run.py` is the single CLI entry point for the entire project. It uses [Python Fire](https://github.com/google/python-fire) to expose every public method on the `Run` class as a subcommand (`python run.py <method_name> [args]`).

For configuration context, see [05-Configuration-and-Runtime](./05-Configuration-and-Runtime.md). For development workflows, see [06-Development-Guide](./06-Development-Guide.md).

---

## Quick Start

### Single service — browse one app's Swagger (recommended starting point)

```
python run.py api <app_type> mock dict_demo
```

`<app_type>` is one of `commondb`, `casedb`, `seqdb`, or `omopdb`. `mock` bypasses real IdP authentication. `dict_demo` uses in-memory repositories pre-populated with demo data. The app starts with hot-reload enabled.

| App | Port | Swagger | ReDoc |
|-----|------|---------|-------|
| commondb | 8010 | `https://127.0.0.1:8010/docs` | `https://127.0.0.1:8010/redoc` |
| casedb | 8000 | `https://127.0.0.1:8000/docs` | `https://127.0.0.1:8000/redoc` |
| seqdb | 8001 | `https://127.0.0.1:8001/docs` | `https://127.0.0.1:8001/redoc` |
| omopdb | 8002 | `https://127.0.0.1:8002/docs` | `https://127.0.0.1:8002/redoc` |

All API routes are prefixed with `/v1`.

### Multiple services — wired-up platform

```
python run.py api_platform_local_mock_dict_demo
```

Starts OAuth (port 9000), seqdb (8003), and casedb (8000) together. casedb calls seqdb via the OAuth server using client-credentials flow. Does **not** start commondb or omopdb, and does not have hot-reload (servers run as `ServerManager` subprocesses).

### Self-signed certificates

`cert/` exists in the repo, so both commands serve over HTTPS using those certs. Browsers will show an "untrusted certificate" warning — click through it. When hitting endpoints with `curl`, pass `-k` to skip verification.

---

## Subcommand Catalog

### api — start application servers

| Subcommand | Description |
|------------|-------------|
| `api` | Start a single app. Takes `app_type`, `idp_config`, and `dev_repository_config` as arguments. |
| `api_platform_local_mock_dict_demo` | Start the full platform using in-memory dict repositories. |
| `api_platform_local_mock_sa_sql_demo` | Start the full platform using SQLAlchemy SQL repositories. |

(Source: `run.py#L82-L117`)

### env — trigger dependency-injection initialisation

Imports a single app's `env` module, which wires up its DI container. Useful for verifying that an app's environment resolves without starting the server.

`env_casedb` / `env_seqdb` / `env_omopdb` / `env_commondb`

(Source: `run.py#L119-L132`)

### etl — seed data

| Subcommand | Description |
|------------|-------------|
| `etl_load_demo_data` | Load demo seed data into one or all apps. Pass `app_type` (`casedb`, `seqdb`, `omopdb`, `commondb`, or `all`). |

(Source: `run.py#L134-L160`)

### test — run test suites

Aggregate commands that span multiple apps:

| Subcommand | Description |
|------------|-------------|
| `test_all` | Full suite with coverage HTML/XML reports. CI entry point. Performance and code tests excluded. |
| `test_all_incl_performance` | Full suite including performance tests. |
| `test_all_unit` | All unit tests across every app. |
| `test_all_integration` | All integration tests across every app. |
| `test_all_performance` | All performance tests. |
| `test_end_to_end` | All end-to-end tests. |

Per-app commands follow the pattern `test_{app}_{scope}` and optionally `test_{app}_{scope}_{detail}`, where scope is `unit`, `integration`, or `performance`. Each targets the corresponding path under `test/`. Available apps: `fastapp`, `commondb`, `casedb`, `seqdb`, `omopdb`. Shared-module tests use `test_filter_unit`, `test_transform_unit`, `test_general_docs`, and `test_general_code`.

(Source: `run.py#L163-L887`)

### other — utilities and tooling

| Subcommand | Description |
|------------|-------------|
| `other_general_run_linters` | Run all linters and write output to `test/output/`. |
| `other_general_run_pylint` | Run pylint alone, with optional error-code filtering. |
| `other_general_run_mypy` | Run mypy alone using repository `mypy.ini` settings. |
| `other_general_analyse_pylint_code_impact` | Analyse relative impact of pylint codes across the codebase. |
| `other_general_generate_uuids` | Generate a grid of UUIDs (benchmarking utility). |
| `other_general_generate_erm_diagrams` | Generate entity-relationship diagrams into `docs/assets/erm/`. |
| `other_casedb_parse_user_journey_from_debug_log` | Parse a debug log into an Excel report and a pickled user-journey object. |
| `other_oauth_server_start` | Start the local OAuth test server. |

---

## Design Notes

### Fire class-as-CLI

The entire file is one class passed to `fire.Fire(Run)`. Every public method becomes a top-level subcommand. Fire automatically parses method parameters from the command line, including type coercion for primitives and enums.

### Lazy imports

Heavy modules (`uvicorn`, `pytest`, `subprocess`, the app modules themselves) are imported **inside** each method, not at the top of the file. This keeps CLI startup time negligible regardless of which command is invoked. Only lightweight imports used across multiple methods (`datetime`, `pathlib`, `fire`, and the enum/util imports needed for environment setup) are at module scope.

### Class-level configuration dictionaries

`APP_URI` and `ETL_ENV` are class-level `dict[AppType, ...]` that centralise per-app settings:

| Dict | What it holds |
|------|---------------|
| `APP_URI` | Uvicorn target string, host, and port for each app |
| `ETL_ENV` | Module root path and ordered list of ETL seed targets per app |

Using `AppType` enum keys means any code that needs to look up an app's configuration does a single dictionary access rather than a series of conditionals.

### Enum-driven app identity with CLI string conversion

CLI arguments arrive as plain strings. The `api()` and `etl_load_demo_data()` methods convert them at the boundary with `AppType[app_type.upper()]`. All internal logic then works with the enum exclusively. This keeps the public interface forgiving (case-insensitive) while the internals stay type-safe.

### Environment bootstrap before app startup

Both `api()` and `etl_load_demo_data()` call `set_env_variables()` as their first substantive action. This single function configures the dynaconf environment variables that every app module reads during initialisation. The pattern ensures dev environment setup happens exactly once, at the CLI boundary, before any application code is imported or executed.

### Conditional SSL

`api()` checks whether `cert/key.pem` and `cert/cert.pem` exist on disk and passes `None` to uvicorn if they do not. SSL is therefore opt-in by file presence — no configuration flag or environment variable is needed.

### Two distinct test invocation strategies

| Strategy | Used by | Why |
|----------|---------|-----|
| `subprocess.run` + `coverage` | `test_all` | Needs coverage instrumentation. Produces HTML and XML reports under `test/output/`. This is the CI entry point. |
| `pytest.main()` (in-process) | Every other `test_*` method | Faster for interactive development; no coverage overhead. |

### Shared default pytest arguments

`DEFAULT_PYTEST_ARGS` is a class-level list appended to by every test method:

```
-s -v  — show stdout, verbose output
-W ignore::DeprecationWarning
-W ignore::pytest.PytestAssertRewriteWarning
-W ignore::sqlalchemy.exc.SAWarning
```

This keeps warning suppression and verbosity consistent without repeating it in each method.

### Hierarchical test method naming

Test methods follow `test_{app}_{scope}_{detail}`, directly mirroring the `test/` directory tree. Examples:

```
test_casedb_unit_services_case   →  test/casedb/unit/services/case
test_seqdb_integration_build_db  →  test/seqdb/integration/build_db
```

Fire exposes these as flat subcommands, but the naming convention makes them browsable and discoverable, acting as a manual command hierarchy.

### Performance and code-quality tests are opt-out

In `test_all`, performance and `general/code` test paths are commented out with a note. Each has its own standalone method for on-demand execution. This keeps the default full-suite run fast while still providing easy access to the heavier checks when needed.

### `ALL` fan-out pattern in ETL

`etl_load_demo_data` accepts `AppType.ALL` as the `app_type` argument. When matched, it iterates over `AppTypeSet.ALL.value` and calls the load function for each app in sequence. Single-app calls fall through to the non-looping path below. This avoids duplicating the iteration logic at every call site.

### Section comments as logical grouping

Methods are partitioned under `## api`, `## env`, `## etl`, `## test`, and `## Other` comments. Fire has no native support for subcommand groups, so these comments serve purely as source-level navigation aids.

---

## Evidence Sources

- `run.py#L15-L887`
- `gen_epix/commondb/util.py#L74-L119`
