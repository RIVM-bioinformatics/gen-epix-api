# Gen-EpiX Agent Guide

Use this file as the short, always-relevant operating guide for coding agents.
The repository documentation is the navigation hub; source code, configuration,
tests, and workflows are the final authority when they disagree with docs.

## Before Changing Code

- Start at the owning command, service, repository, router, or configuration
      module. Use nearby tests and existing implementations as the primary pattern.
- For architecture or relationship questions, query `graphify-out/graph.json`
      first when it exists. Then verify the relevant behavior in source code.
- Do not invent endpoints, settings, ports, roles, repository modes, or module
      ownership. Search for missing references and report stale documentation.
- Keep changes focused. Do not rewrite unrelated user changes or generated
      output.

## Architecture Rules

The runtime package is under `gen_epix/`:

- `fastapp/` is the shared application framework: commands, domain metadata,
      policies, application dispatch, services, repositories, and API utilities.
- `commondb/` supplies shared users, organizations, authentication, policies,
      configuration, composition, and routers.
- `casedb/`, `seqdb/`, and `omopdb/` are app-specific domains built on that
      foundation. `filter/` and `transform/` are shared support packages.
- Each app is composed from configuration, repositories, services, policies,
      domain registrations, and routers before FastAPI starts serving requests.

Preserve these boundaries:

- API functions are transport adapters: parse the request, construct a
      command, call `app.handle(command)`, and return the result.
- Business rules belong in commands, policies, or services; persistence belongs
      behind repository interfaces. Do not call repositories directly from routes.
- Authorization is command-centric. `App.handle()` applies policies in
      `BEFORE`, `DURING`, and `AFTER` phases; do not add RBAC or ABAC decisions to
      FastAPI handlers.
- Routers are mounted under `/v1`. Reuse the shared router composition pattern
      and check OpenAPI behavior when changing an endpoint.
- Repository behavior must stay equivalent across `DICT`, `SA_SQLITE`, and
      `SA_SQL` implementations. Justify any backend-specific behavior.
- In production, cross-domain communication uses HTTP. Search for an existing
      client abstraction before adding a new remote-call pattern.

## Commands

Use Python 3.14 or newer, preferably in the project virtual environment.
Install runtime and development dependencies with:

```bash
pip install -r requirements.txt
pip install -r dev-requirements.txt
```

Useful verified commands:

| Purpose | Command |
| --- | --- |
| Curated suite with coverage | `python run.py test_all --include_e2e=False` |
| Curated suite including E2E | `python run.py test_all` |
| Fast pytest discovery | `make test` |
| Targeted app/scope tests | `python run.py test_<app>_<scope>` |
| Format check | `isort --check-only --diff --profile black --float-to-top --line-length=88 .` and `black -l 88 --check --diff .` |
| Autoformat | `isort --profile black .` and `black .` |
| Pylint | `pylint ./gen_epix --disable=C0301` |
| Type checking | `mypy --config-file mypy.ini ./` |

`run.py test_all` is the CI-style curated suite and writes reports below
`test/output/`; it excludes performance tests and, when requested, E2E tests.
`make test` is a separate raw pytest invocation. Performance tests require the
`performance` marker, and E2E tests require their external services/configuration.

CI currently runs pylint and mypy with `|| true`, so their output is reported
but does not fail the workflow. Formatting and tests do fail their CI steps.

For Docker-backed local services:

```bash
make restart-docker
make restart-docker-teardown
```

The teardown target deletes database volumes. SQL Server performance testing is
available through `make calculate-distances-performance-mssql` and requires
pyodbc plus an installed SQL Server ODBC driver.

## Running An App

The main entrypoint is:

```bash
python run.py api <app> <idp_mode> <repository_mode>
```

Apps and default ports are `casedb:8000`, `seqdb:8001`, `omopdb:8002`, and
`commondb:8010`. Supported IDP modes are `IDPS`, `MOCK`, and `NONE`. Repository
modes include `DICT_DEMO`, `DICT_EMPTY`, `SA_SQLITE_DEMO`, `SA_SQLITE_EMPTY`,
and `SA_SQL`; verify exact enum names before using one.

Configuration is Dynaconf-based and assembled through environment variables.
Settings files are ordered, later files override earlier files, nested runtime
overrides use `__`, and missing settings files fail at startup. Do not hardcode
configuration paths or assume a port from memory.

`NONE` mode uses the no-IDP path and changes the trust posture through root-user
fallback. Treat it as a constrained local/test mode, not as equivalent to OIDC
authentication. Only OIDC identity-provider protocols are implemented, and
authentication setup supports at most five active IDPs.

Debug mode changes the middleware security posture. TLS is enabled by `run.py`
only when `cert/key.pem` and `cert/cert.pem` exist. When diagnosing startup,
separate settings loading, composition, IDP initialization, user resolution,
and request policy failures.

## Tests And Changes

- Add or update focused tests for behavior changes. Match the existing `test/`
      tree: `unit`, `integration`, `performance`, and `end_to_end`.
- Use the repository's pytest markers: `integration`, `performance`, and `e2e`.
- For command or authorization changes, test the command lifecycle and state
      the affected policy phase and trust implications.
- For repository changes, test or justify parity across dictionary, SQLite, and
      SQL implementations.
- Avoid broad formatting or generated-report changes in focused patches.

## Documentation Map

Start with [docs/00-Index.md](docs/00-Index.md). Link to the detailed source
instead of duplicating it:

- [Architecture](docs/02-Architecture.md) and
      [FastApp framework](docs/02a-Fastapp-Framework.md)
- [Security](docs/03-Security.md)
- [Configuration and runtime](docs/05-Configuration-and-Runtime.md)
- [Development guide](docs/06-Development-Guide.md) and
      [CLI reference](docs/06a-CLI-Reference.md)
- [CI/CD and release](docs/07-CI-CD-and-Release.md)
- [Extending the system](docs/08-Extending-the-System.md)
- [Constraints and open questions](docs/09-Constraints-and-Open-Questions.md)

When docs and executable behavior conflict, report both explicitly as "Docs say
X, code shows Y" and recommend which should be updated.

## Graphify

For any question about this repo's architecture, structure, components, or how to add/modify/find
code, use the `$graphify` skill first when it is available. If the skill is unavailable, your
first action should be `graphify query "<question>"` when `graphify-out/graph.json` exists. Use
`graphify path "<A>" "<B>"` for relationship questions and `graphify explain "<concept>"` for
focused-concept questions. These return a scoped subgraph, usually much smaller than the full report
or raw grep output.

Triggers: "how do I…", "where is…", "what does … do", "add/modify a <component>",
"explain the architecture", or anything that depends on how files or classes relate.

If `graphify-out/wiki/index.md` exists, use it for broad navigation. Read `graphify-out/GRAPH_REPORT.md`
only for broad architecture review or when query/path/explain do not surface enough context. Only read
source files when (a) modifying/debugging specific code, (b) the graph lacks the needed detail, or
(c) the graph is missing or stale.

Type `/graphify` in Copilot Chat to build or update the graph.
