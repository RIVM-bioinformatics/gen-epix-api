Creation Date: February 16, 2026

# Local Development Deep Dive

## 1. Local Runtime Model Overview
Local development is centered on a single CLI entrypoint (`run.py`) that orchestrates API startup, test execution, and data-loading workflows. This keeps day-to-day developer operations in one command surface rather than separate scripts per subsystem. (Source: `run.py#L15-L15`; Source: `run.py#L82-L205`; Source: `run.py#L887-L887`)

The local API launcher uses a fixed app map (`CASEDB`, `SEQDB`, `OMOPDB`, `COMMONDB`) with predefined import URI, host, and port values, then passes control to uvicorn. (Source: `run.py#L17-L38`; Source: `run.py#L100-L107`)

```text
Developer command (run.py)
  -> choose app + IDP mode + repository mode
  -> set environment-backed settings stack
  -> start FastAPI (uvicorn) or run tests/ETL helpers
```
(Source: `run.py#L82-L90`; Source: `gen_epix/commondb/util.py#L74-L119`; Source: `run.py#L163-L200`; Source: `run.py#L134-L160`)

## 2. Configuration Authority in Local Mode
Local runtime behavior is built from layered settings files selected by `set_env_variables(...)`, then exported through `<APP>_SETTINGS_FILES` and `<APP>_LOG_CONFIG_FILE`. (Source: `gen_epix/commondb/util.py#L74-L77`; Source: `gen_epix/commondb/util.py#L114-L119`)

IDP mode is explicit and finite:
1. `IDPS` -> `config/identity_providers.toml`
2. `MOCK` -> `config/mock_identity_provider.toml`
3. `NONE` -> `config/no_identity_providers.toml`
(Source: `gen_epix/commondb/util.py#L78-L85`; Source: `config/identity_providers.toml#L1-L34`; Source: `config/mock_identity_provider.toml#L1-L16`; Source: `config/no_identity_providers.toml#L1-L1`)

Repository mode is also explicit and finite (DICT vs SA families) with mode-specific secrets files appended to the settings stack. (Source: `gen_epix/commondb/util.py#L87-L109`)

Developer Note: local config fails fast on invalid mode names (`ValueError`) and missing settings files (`FileNotFoundError`), which prevents silent startup in an unintended configuration. (Source: `gen_epix/commondb/util.py#L85-L93`; Source: `gen_epix/commondb/util.py#L109-L109`; Source: `gen_epix/commondb/config/settings_manager.py#L63-L67`)

## 3. Primary Local Workflows
The `api(...)` workflow is the main runtime path: parse mode enums, set env vars, and run uvicorn with reload enabled; TLS key/cert are used only if expected files exist. (Source: `run.py#L82-L107`; Source: `run.py#L40-L41`)

Local platform helpers delegate to `run_platform(...)` for multi-service startup paths with either dict-backed or SQL-backed repository choice flags. (Source: `run.py#L109-L117`; Source: `test/test_client/start_all_services.py#L210-L223`)

Testing workflow uses `test_all`, which executes selected test directories via coverage, then writes HTML/XML coverage reports to `test/output`. (Source: `run.py#L163-L200`)

ETL workflow (`etl_load_demo_data`) prepares env context and calls repository transfer logic that moves demo data from dict repositories into SQL repositories when connection checks pass. (Source: `run.py#L134-L160`; Source: `etl.py#L72-L87`; Source: `etl.py#L122-L133`; Source: `etl.py#L141-L148`)

## 4. Operational Interpretation for Developers and Operators
Before exposing local instances beyond loopback/trusted environments, operators should verify which IDP mode and repository mode were selected, because those two switches define authentication posture and persistence behavior. (Source: `run.py#L82-L90`; Source: `gen_epix/commondb/util.py#L78-L109`)

`NONE` IDP mode is implemented as a real configuration path, not an error fallback. Treat it as a reduced-security local mode that should be intentional. (Source: `gen_epix/commondb/util.py#L82-L85`; Source: `config/no_identity_providers.toml#L1-L1`)

When local auth/config startup breaks, reason in stages:
1. Env stack construction (`set_env_variables`)
2. Settings file existence/load (`SettingsManager`)
3. App startup (`uvicorn.run`) or downstream command behavior
(Source: `gen_epix/commondb/util.py#L74-L119`; Source: `gen_epix/commondb/config/settings_manager.py#L43-L67`; Source: `run.py#L100-L107`)

Operator Note: `CASEDB` env setup also sets `SEQDB` env variables, so multi-app sessions can be affected by launching casedb first. (Source: `gen_epix/commondb/util.py#L61-L64`)

## 5. Security and Risk Modes in Local Development
Local security posture is mode-driven, not auto-detected.

1. `IDPS` mode points to configured OIDC providers (including a public provider entry and claim mapping configuration).
2. `MOCK` mode points to local mock OIDC settings.
3. `NONE` mode provides an explicit no-provider path.
(Source: `config/identity_providers.toml#L1-L34`; Source: `config/mock_identity_provider.toml#L1-L16`; Source: `config/no_identity_providers.toml#L1-L1`; Source: `gen_epix/commondb/util.py#L78-L85`)

Security Note: local convenience commands are designed for development velocity; they do not evidence production ingress hardening or deployment guardrails by themselves. `<TBF elsewhere>`

## 6. Constraints & Guardrails
1. Local app host/port defaults are hard-coded in `Run.APP_URI` unless code/config is changed. (Source: `run.py#L17-L38`)
2. `test_all` scope is curated and excludes commented performance/code test suites by default. (Source: `run.py#L166-L187`)
3. Runtime and development dependency surfaces are separated into `requirements.txt` and `dev-requirements.txt`. (Source: `requirements.txt#L3-L35`; Source: `dev-requirements.txt#L1-L25`)
4. Nested envvar overrides use Dynaconf `__` separator semantics. (Source: `gen_epix/commondb/config/settings_manager.py#L15-L17`; Source: `gen_epix/commondb/config/settings_manager.py#L71-L74`)

## 7. Open Questions / <TBF elsewhere>
1. Official local container orchestration profile (`docker-compose`/k8s dev profile) for this repository: `<TBF elsewhere>`.
2. Standardized team runbook for mode selection (when to use `IDPS` vs `MOCK` vs `NONE`) beyond code-level options: `<TBF elsewhere>`.
3. Production-equivalent secret management flow for local-to-prod parity: `<TBF elsewhere>`.

## 8. Evidence Index
- `run.py#L15-L205`
- `run.py#L887-L887`
- `etl.py#L72-L148`
- `gen_epix/commondb/util.py#L61-L119`
- `gen_epix/commondb/config/settings_manager.py#L43-L77`
- `config/identity_providers.toml#L1-L34`
- `config/mock_identity_provider.toml#L1-L16`
- `config/no_identity_providers.toml#L1-L1`
- `test/test_client/start_all_services.py#L210-L223`
- `requirements.txt#L3-L35`
- `dev-requirements.txt#L1-L25`
