# Getting Started

## Evidenced in Repository

### Prerequisites
- Python is required at `>=3.13`; CI uses Python `3.14`. (Source: `pyproject.toml#L17-L24`; Source: `.github/workflows/main.yml#L30-L33`)
- The CI environment installs `unixodbc-dev` and builds `pyodbc` from source. (Source: `.github/workflows/main.yml#L34-L37`; Source: `.github/workflows/main.yml#L56-L57`)
- Runtime and development dependencies are split between `requirements.txt` and `dev-requirements.txt`. (Source: `requirements.txt#L3-L35`; Source: `dev-requirements.txt#L6-L16`)

### Local Runtime Command
- CLI entrypoint is `python run.py ...` via `fire.Fire(Run)`. (Source: `run.py#L856-L857`)
- API startup command is `api(app_type, idp_config, dev_repository_config)`. (Source: `run.py#L82-L90`)
- App targets are `COMMONDB`, `CASEDB`, `SEQDB`, `OMOPDB`. (Source: `gen_epix/commondb/domain/enum.py#L82-L87`; Source: `run.py#L17-L38`)
- IDP modes are `IDPS`, `MOCK`, `NONE`. (Source: `gen_epix/commondb/domain/enum.py#L101-L104`)
- Repository modes are `DICT_DEMO`, `DICT_EMPTY`, `SA_SQLITE_DEMO`, `SA_SQLITE_EMPTY`, `SA_SQL`. (Source: `gen_epix/commondb/domain/enum.py#L107-L113`)

Example command patterns:
- `python run.py api casedb idps dict_empty`
- `python run.py api seqdb mock sa_sqlite_demo`

The examples above follow the parsed enum inputs and startup path in `Run.api`. (Source: `run.py#L82-L107`)

### Settings Model
- Runtime settings are assembled by `set_env_variables(...)`, which writes `<APP>_SETTINGS_FILES` and `<APP>_LOG_CONFIG_FILE`. (Source: `gen_epix/commondb/domain/util.py#L30-L37`; Source: `gen_epix/commondb/domain/util.py#L114-L120`)
- Missing settings files raise `FileNotFoundError`. (Source: `gen_epix/commondb/config/settings_manager.py#L63-L67`)
- Dynaconf nested env overrides use `__`. (Source: `gen_epix/commondb/config/settings_manager.py#L15-L17`; Source: `gen_epix/commondb/config/settings_manager.py#L70-L74`)

### Mock IDP Mode
- `MOCK` mode maps to `config/mock_identity_provider.toml`. (Source: `gen_epix/commondb/domain/util.py#L81-L83`; Source: `config/mock_identity_provider.toml#L1-L16`)
- No-IDP mode also exists (`NONE`) and maps to `config/no_identity_providers.toml`. (Source: `gen_epix/commondb/domain/util.py#L83-L85`; Source: `config/no_identity_providers.toml#L1-L1`)

### Running Tests
- The CI test command is `python run.py test_all`. (Source: `.github/workflows/main.yml#L167-L170`)
- `test_all` runs curated suites and writes coverage reports to `test/output/coverage.html` and `test/output/coverage.xml`. (Source: `run.py#L163-L200`)

### Verifying Health
- Health endpoint is implemented at `/health` and returns `HEALTHY`. (Source: `gen_epix/commondb/api/system.py#L60-L73`)
- Routers are mounted under `/v1`, so health is available at `/v1/health`. (Source: `gen_epix/commondb/app_setup.py#L119-L120`)
- Container healthcheck also calls `http://127.0.0.1:8000/v1/health`. (Source: `Dockerfile#L63-L64`)

### Logs
- Application logs go to stdout via `logging.StreamHandler` configured with `stream: ext://sys.stdout`. (Source: `gen_epix/commondb/config/logging.yaml#L7-L12`)
- Logger namespaces include setup/app/service/api/external channels. (Source: `gen_epix/commondb/config/logging.yaml#L13-L32`)

## Inferred from Code Structure
- Running `Run.api` for different app types should expose local endpoints on the configured ports (`8000`, `8001`, `8002`, `8010`). (Source: `run.py#L17-L38`; Source: `run.py#L91-L104`)
- A practical local smoke check is: start one app, then call `/v1/health` on its port. (Source: `gen_epix/commondb/app_setup.py#L119-L120`; Source: `gen_epix/commondb/api/system.py#L60-L73`)

## Deployment
- Production deployment instructions are not fully specified in repository code/docs: `<TBF elsewhere>`.

## Evidence Sources
- `pyproject.toml#L17-L24`
- `.github/workflows/main.yml#L30-L37`
- `.github/workflows/main.yml#L56-L57`
- `requirements.txt#L3-L35`
- `dev-requirements.txt#L6-L16`
- `run.py#L17-L38`
- `run.py#L82-L107`
- `run.py#L163-L200`
- `run.py#L856-L857`
- `gen_epix/commondb/domain/enum.py#L82-L113`
- `gen_epix/commondb/domain/util.py#L30-L37`
- `gen_epix/commondb/domain/util.py#L78-L85`
- `gen_epix/commondb/domain/util.py#L114-L120`
- `gen_epix/commondb/config/settings_manager.py#L15-L17`
- `gen_epix/commondb/config/settings_manager.py#L63-L74`
- `config/mock_identity_provider.toml#L1-L16`
- `config/no_identity_providers.toml#L1-L1`
- `gen_epix/commondb/api/system.py#L60-L73`
- `gen_epix/commondb/app_setup.py#L119-L120`
- `gen_epix/commondb/config/logging.yaml#L7-L32`
- `Dockerfile#L63-L64`
