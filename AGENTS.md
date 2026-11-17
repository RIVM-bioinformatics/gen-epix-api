# Gen-EpiX Agent Guide

Use this file as the short, always-relevant operating guide for coding agents.
The repository documentation is the navigation hub; source code, configuration,
tests, and workflows are the final authority when they disagree with docs.

## Before Changing Code

- Start at the owning command, service, repository, router, or configuration
      module. Use nearby tests and existing implementations as the primary pattern.
- Do not invent endpoints, settings, ports, roles, repository modes, or module
      ownership. Search for missing references and report stale documentation.
- Keep changes focused. Do not rewrite unrelated user changes or generated
      output.

## Architecture Rules

The runtime package is under `gen_epix/`:

- `fastapp/` is the shared application framework: commands, domain metadata,
      policies, application dispatch, services, repositories, and API utilities.
- `commondb/` supplies shared users, organizations, authentication, policies,
      configuration, composition, routers, and the shared ETL-run result
      accumulator layer (`domain/model/etl.py`) used by ETL pipelines.
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
- Python docstrings and comments follow the repo standard in
  `docs/standards/google-python-style-guide-3.8-comments-and-docstrings.md`.

## Dependencies

`pyproject.toml` splits the runtime dependencies; see "Installing as a package:
client versus server" in `docs/06-Development-Guide.md`.

- The base `dependencies` are the client: domain models, commands, enums and the
      remote clients. Consumers that only call the apps (the lsp-data Airflow
      worker) install only these.
- The `server` extra is everything else needed to run an app: the web stack,
      repositories, services, policies, configuration and `run.py`. idsdb and
      lsp-data's refdata build install `gen-epix[server]`.
- A new runtime dependency goes in `server`, unless client-facing code imports
      it. Import a package that only a service or repository needs there, not in
      a model; if a model method needs one, import it inside that method.
- Development tools and type stubs go in `dev-requirements.txt`.
- `requirements.txt` is the base dependencies plus `server`, and must follow
      `pyproject.toml`; `test/general/code/test_general_dependency_list.py` checks
      this.

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
| Specific test folder | `python run.py run_test "test/casedb/unit"` |
| Format check | `isort --check-only --diff --profile black --float-to-top --line-length=88 .` and `black -l 88 --check --diff .` |
| Autoformat | `isort --profile black .` and `black .` |
| Pylint | `pylint ./gen_epix --disable=C0301` |
| Type checking | `mypy --config-file mypy.ini ./` |
| One test file or test | `pytest test/casedb/unit/services/case/test_casedb_unit_services_case_crud_case_set.py` (add `::test_name` or `-k EXPR`) |
| Docstring lint (blocking in CI) | `ruff check --select D --ignore D212,D417 <paths>` |

Before calling work done, run `python run.py test_all --include_e2e=False`.

`run.py test_all` is the CI-style curated suite and writes reports below
`test/output/`; it excludes performance tests and, when requested, E2E tests.
`run.py run_test` targets specific test folders via the `test/` directory tree.
`make test` is a separate raw pytest invocation. Performance tests require the
`performance` marker, and E2E tests require their external services/configuration.

CI currently runs pylint and mypy with `|| true`, so their output is reported
but does not fail the workflow. Formatting and tests do fail their CI steps.

For Docker-backed local services:

```bash
make restart-docker
make restart-docker-teardown
```

`make start-db` and `make stop-db` start and stop the local SQL Server
(`lsp_sql`) used by SQL Server tests. `make restart-docker-teardown` and
`make calculate-distances-performance-mssql` both delete the Docker database
volumes; confirm before running either. The benchmark target also needs pyodbc
and an installed SQL Server ODBC driver.

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
- Use the repository's pytest markers: `integration`, `performance`, `e2e`, and `live`.
      `performance` and `live` tests are skipped unless selected with `-m`; `live` tests call
      real deployed services with real credentials (see the Development Guide).
- For command or authorization changes, test the command lifecycle and state
      the affected policy phase and trust implications.
- For repository changes, test or justify parity across dictionary, SQLite, and
      SQL implementations.
- Avoid broad formatting or generated-report changes in focused patches.

### Unit-test paths and filenames

- For `gen_epix/<package>/<subfolders>/<module_name>.py`, place the test in
  `test/<package>/unit/<subfolders>/`, preserving each source subfolder in order.
- Name it `test_<path_with_underscores>_<module_name>.py`, where
  `path_with_underscores` joins the test folders below `test` (`<package>`,
  `unit`, every subfolder) with underscores.
- A module directly under `gen_epix/` maps to `test/unit/test_unit_<module_name>.py`.
- Example: `gen_epix/casedb/services/case/crud_case_set.py` maps to
  `test/casedb/unit/services/case/test_casedb_unit_services_case_crud_case_set.py`.
- Inventory script mapping (create-unit-test): `--map "gen_epix={package}/unit/{subdirs}"`.
- For each new test folder (including new parents), add a folder entry to
  `.vscode/launch.json`: `"name": "test.<folder path with dots>"`,
  `"type": "debugpy"`, `"request": "launch"`, `"program": "run.py"`,
  `"args": ["run_test", "<folder>"]`, `"console": "integratedTerminal"`,
  `"justMyCode": true`. Insert it in folder-path order after the API,
  environment and ETL entries.
- Import mocks from `test.util.mock_compat`, never directly from `unittest.mock`.

## Git and Jira workflow

- Base branch: `dev`. Work branches start from `dev`; pull requests target `dev`.
- Jira project `LSP` (keys such as `LSP-1234`), reached through the Atlassian MCP
  server in `.vscode/mcp.json`. Branch names start with the key. After the draft
  pull request exists, move the issue to `In Test`.
- Review gates (required, as in CI): `black -l 88 --check --diff .`,
  `ruff check --select D --ignore D212,D417 gen_epix` and
  `python run.py test_all --include_e2e=False`.
- Advisory (reported, not blocking): `isort --check-only --diff .` (disabled in CI),
  `pylint ./gen_epix --disable=C0301`, `mypy --config-file mypy.ini ./`.

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

## Agent skills

- Repository-only skills live in `.agents/skills/<name>/SKILL.md` (read by Codex and Copilot).
  Shared skills come from the `gen-epix-agent-skills` plugins; do not copy them here.
- Claude Code reads `.claude/skills`, a git symlink to `../.agents/skills`. On Windows it only
  works with Developer Mode on and `git config core.symlinks true`; otherwise the link is a
  small text file and Claude Code sees no repository skills.
- Bundled scripts live inside the skill folder. Use the `skill-generation` skill to add or
  change a skill.
- To change how a shared skill behaves in this repository, add a `## Skill rules: <name>`
  section to this file. It may make the skill's safety rules stricter, never looser.

## Skill rules: implement-jira-issue

- Run the baseline test suite only when the user asks; then say in the pull request
  that no baseline was run.
