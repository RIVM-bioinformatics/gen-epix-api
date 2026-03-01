Creation Date: March 1, 2026

# Development Guide

This chapter covers local development workflows, testing, and linting. For the full `run.py` CLI catalog, see [06a-CLI-Reference](./06a-CLI-Reference.md). For mutation testing, see [06b-Mutation-Testing](./06b-Mutation-Testing.md).

---

## 1. Local Development Model

Local development is centered on a single CLI entrypoint (`run.py`) that orchestrates API startup, test execution, and data-loading workflows. (Source: `run.py#L15-L15`; Source: `run.py#L82-L205`)

```text
Developer command (run.py)
  -> choose app + IDP mode + repository mode
  -> set environment-backed settings stack
  -> start FastAPI (uvicorn) or run tests/ETL helpers
```

See [01-Getting-Started](./01-Getting-Started.md) for initial setup and quickstart.

---

## 2. Running Tests

### Full test suite (CI entry point)

```
python run.py test_all
```

This runs curated test directories via `coverage` and writes HTML/XML reports to `test/output/`. Performance and code-quality test folders are intentionally excluded from the default run. (Source: `run.py#L163-L200`; Source: `.github/workflows/main.yml#L167-L170`)

### Per-app test commands

Test methods follow `test_{app}_{scope}` naming, directly mirroring the `test/` directory tree:

| Command pattern | Example |
|----------------|---------|
| `test_{app}_unit` | `python run.py test_casedb_unit` |
| `test_{app}_integration` | `python run.py test_seqdb_integration` |
| `test_{app}_performance` | `python run.py test_fastapp_performance` |

Available apps: `fastapp`, `commondb`, `casedb`, `seqdb`, `omopdb`.
Shared module tests: `test_filter_unit`, `test_transform_unit`, `test_general_docs`, `test_general_code`.

Per-app test commands use `pytest.main()` in-process (faster, no coverage overhead). (Source: `run.py#L163-L887`)

### End-to-end tests

```
python run.py test_end_to_end
```

---

## 3. Code Quality Checks

### Formatting

CI uses `isort` and `black`:

```
isort --check-only --diff --profile black .
black --check --diff .
```

To auto-fix:

```
isort --profile black .
black .
```

(Source: `.github/workflows/main.yml#L73-L77`)

### Linting

```
python run.py other_general_run_pylint
```

Or narrowed to specific error codes:

```
python run.py other_general_run_pylint <error_code>
```

(Source: `.github/workflows/main.yml#L102-L113`)

### Type checking

```
python run.py other_general_run_mypy
```

CI runs strict `mypy` flags. (Source: `.github/workflows/main.yml#L136-L140`)

### All linters at once

```
python run.py other_general_run_linters
```

Writes output to `test/output/`. (Source: `run.py`)

---

## 4. Dependencies

| File | Contents |
|------|----------|
| `requirements.txt` | Runtime dependencies |
| `dev-requirements.txt` | Dev/test tools: `pytest`, `isort`, `black`, `pylint`, `mypy`, `coverage` |

(Source: `requirements.txt#L3-L35`; Source: `dev-requirements.txt#L1-L25`)

---

## 5. Troubleshooting Local Development

When local startup breaks, reason in stages:

1. **Env stack construction** — `set_env_variables()` builds the settings file list. Invalid mode names raise `ValueError`. (Source: `gen_epix/commondb/util.py#L74-L119`)
2. **Settings file load** — `SettingsManager` reads and validates. Missing files raise `FileNotFoundError`. (Source: `gen_epix/commondb/config/settings_manager.py#L43-L67`)
3. **App startup** — `uvicorn.run()` starts the ASGI server. Composition failures are logged and re-raised. (Source: `gen_epix/commondb/env.py#L185-L197`)

Operator Note: `CASEDB` env setup also sets `SEQDB` env variables, so multi-app sessions can be affected by launching casedb first. (Source: `gen_epix/commondb/util.py#L61-L64`)

---

## Evidence Sources

- `run.py#L15-L887`
- `.github/workflows/main.yml#L73-L197`
- `gen_epix/commondb/util.py#L61-L119`
- `gen_epix/commondb/config/settings_manager.py#L43-L67`
- `gen_epix/commondb/env.py#L185-L197`
- `requirements.txt#L3-L35`
- `dev-requirements.txt#L1-L25`
