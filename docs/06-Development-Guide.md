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

### Specific test folders

Use the `run_test` command to run tests in any folder:

```
python run.py run_test "test/casedb/unit"
```

Available folders mirror the `test/` directory tree:
- **Apps**: `casedb`, `commondb`, `fastapp`, `omopdb`, `seqdb`
- **Scopes**: `unit`, `integration`, `performance`, `custom`
- **Submodules**: `data_access`, `services`, `domain`, `repositories`, `policies`, `routers`, etc.

Examples:
- `python run.py run_test "test/casedb/unit"` — all unit tests for casedb
- `python run.py run_test "test/fastapp/integration"` — fastapp integration tests
- `python run.py run_test "test/general/code"` — code quality tests

The `run_test` command uses `pytest.main()` in-process. For VS Code debugging, launch
configurations automatically call `run_test` with the appropriate folder path.

### End-to-end tests

```
python run.py test_end_to_end
```

### Live tests

Tests marked `live` (currently `test/end_to_end/remote_client`) call real, deployed
services with real credentials, using `create_client` and the `<APP>_*` settings
from the environment or a `.env` file in the working directory. They are skipped
unless explicitly selected, so `run.py test_all` (including its e2e folder) never
runs them even when a `.env` is present:

```
python -m pytest test/end_to_end/remote_client -m live
```

An app whose settings are missing or whose host is unreachable is skipped rather than
failed. The module docstring of `test_remote_client_live.py` lists the exact variables
expected in the `.env` file. Only non-destructive reads are performed.

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

Run the same Ruff docstring check locally that CI runs:

```
python run.py other_general_run_ruff
```

This command checks Google-style docstring rules for `gen_epix/transform` only.
The scope expands package by package as documented modules are completed.

Run Pylint locally:

```
python run.py other_general_run_pylint
```

Or narrowed to specific error codes:

```
python run.py other_general_run_pylint <error_code>
```

Pylint is currently used as an advisory score report in CI: the workflow captures
and comments the score but does not fail the lint job on Pylint findings. The local
Pylint preset keeps `--fail-under=9` as the tracked target, while the `run.py`
wrapper writes the report and continues so developers can inspect the same signal.

(Source: `.github/workflows/main.yml#L102-L113`; Source:
`test/test_client/linter.py#L57-L73`)

### Docstring convention

Gen-EpiX uses PEP 257 as the baseline docstring convention and Google-style
sections when a docstring needs structure. Keep docstrings concise, behavior-led,
and focused on contract details that are not already obvious from the type hints.

For the full canonical reference, see
[docs/standards/google-python-style-guide-3.8-comments-and-docstrings.md](./standards/google-python-style-guide-3.8-comments-and-docstrings.md).

In practice:
- prefer a one-line docstring for simple behavior
- use `Args:`, `Returns:`, `Yields:`, and `Raises:` only when the contract is
  not obvious from the signature or intent
- do not repeat obvious type information already present in annotations
- document side effects, constraints, caller expectations, and invariants when
  they matter

During the staged rollout, Ruff and Pylint intentionally overlap on missing
docstring messages in the Ruff-enabled package. Ruff owns the Google-style
section syntax checks, while Pylint continues to provide the existing broader
code-quality report.

### Type checking

```
python run.py other_general_run_mypy
```

Equivalent direct CI command:

```
mypy --config-file mypy.ini ./
```

Gen-EpiX uses `mypy` to protect architecture boundaries, catch defects earlier, and improve refactoring safety. The goal is pragmatic typing, not full static coverage.

Typing strictness is layered:

- **Strict**: `gen_epix.*.domain.*`, `gen_epix.*.services.*`, `gen_epix.*.policies.*`
- **Moderate**: `gen_epix.*.repositories.*`, `gen_epix.fastapp.*`, `gen_epix.*.config.*`
- **Relaxed**: `test.*`, `tests.*`

Guidelines:

- Type public interfaces and return values first.
- Avoid `Any` at domain/service/repository/config boundaries.
- Prefer explicit domain types (`BaseModel`, `TypedDict`, dataclasses).
- Use `# type: ignore[...]` only when necessary, and keep ignores minimal.

CI runs the same `mypy.ini`-driven policy as a required quality gate. (Source: `.github/workflows/main.yml#L136-L140`; Source: `mypy.ini#L1-L80`; Source: `run.py#L855-L871`; Source: `test/test_client/linter.py#L50-L58`)

### All linters at once

```
python run.py other_general_run_linters
```

Runs the repository linter presets, including Pylint, Ruff, isort, black, and
mypy, and writes output to `test/output/`. (Source: `run.py`; Source:
`test/test_client/linter.py`)

---

## 4. Dependencies

| File | Contents |
|------|----------|
| `requirements.txt` | Runtime dependencies |
| `dev-requirements.txt` | Dev/test tools: `pytest`, `isort`, `black`, `ruff`, `pylint`, `mypy`, `coverage` |

(Source: `requirements.txt#L3-L35`; Source: `dev-requirements.txt#L1-L25`)

---

## 5. Graphify Setup For Coding Agents

This repository includes `graphify-out/` artifacts and `AGENTS.md` instructions
that expect Graphify to be used for architecture, structure, relationship,
code-navigation, and blast-radius questions.

Install the Graphify CLI first:

```bash
uv tool install graphifyy
```

For Codex, Graphify can also be exposed as a user-level skill by placing a
`SKILL.md` file under:

```text
%USERPROFILE%\.codex\skills\graphify\SKILL.md
```
Local testing showed that Codex uses Graphify more reliably through the
user-level skill on the local machine.

The user-level skill is still optional and machine-local. The repository-level 
fallback remains `AGENTS.md`, which tells agents to use 
`$graphify` when available, then fall back to `graphify query`, `graphify path`, or
`graphify explain` against `graphify-out/graph.json`.

See the upstream Graphify documentation for platform-specific details:
[Graphify README](https://github.com/Graphify-Labs/graphify/blob/v8/README.md).

### Maintaining the knowledge graph

The repository knowledge graph (`graphify-out/graph.json` and `GRAPH_REPORT.md`) is
regenerated after each merge to `dev` by the **Update Graphify Graph** CI workflow.

**Manual update (local or pre-PR):**

```bash
python run.py other_graphify_update
```

This runs `graphify-out/graphify_update.py`, an incremental update over the existing
graph rather than a rebuild from scratch. The pipeline:

1. Detects files changed since the last run, using `graphify-out/manifest.json`
2. Extracts code structure from those files via AST (deterministic, cached)
3. Merges the extraction into the existing `graph.json`, pruning deleted files
4. Re-clusters, keeping community ids stable against the previous assignment
5. Writes `graph.json` and `GRAPH_REPORT.md`

Because it only adds or replaces code-derived nodes, nodes extracted from documents
survive untouched — those need an LLM and so are produced only by a full local build.
If no extractable file changed, the run exits without rewriting the graph.

**Workflow automation:**

- **Post-merge to `dev`**: Graph updates are committed automatically after each successful merge
- **On-demand**: Manually trigger via [Actions tab](../../actions/workflows/update-graphify.yml)
- **Caching**: Graphify uses `.graphify_cache/` to speed up incremental runs on large corpora

**Community labelling is a manual step**

Naming communities requires an LLM call. This repository is public, so no API key is
configured for the CI workflow and CI never labels. Instead it reuses the curated names
committed in `graphify-out/.graphify_labels.json`, keeping each name only while that
community's membership still matches the signature recorded in the adjacent
`.graphify_labels.json.sig`, and falling back to a deterministic hub-derived name for any
community that re-clustering has changed. CI never writes either file.

Refresh the names periodically — after a large refactor, or once mechanical hub-derived
names such as `._create_validator` start appearing in `GRAPH_REPORT.md`:

```bash
graphify label . --backend claude-cli   # or gemini/openai, with that key exported
graphify export wiki
```

`graphify label` also regenerates `graph.html`, which the CI update does not produce.
Commit the refreshed `.graphify_labels.json`, `.graphify_labels.json.sig`, `graph.json`,
`GRAPH_REPORT.md`, `graph.html`, and `graphify-out/wiki/` together, so the names, the
graph they describe, and the generated wiki stay in step.

The repository exposes shared Graphify guidance through `AGENTS.md` and
Copilot-specific `/graphify` invocation through
`.github/copilot-instructions.md`. Other clients can reuse the generated
artifacts when they support these conventions, but this repository does not
configure a separate Cursor integration. (Source: `AGENTS.md#L146-L161`;
Source: `.github/copilot-instructions.md#L29-L32`)

---

## 6. Troubleshooting Local Development

When local startup breaks, reason in stages:

1. **Env stack construction** — `set_env_variables()` builds the settings file list. Invalid mode names raise `ValueError`. (Source: `gen_epix/commondb/util.py#L74-L119`)
2. **Settings file load** — `SettingsManager` reads and validates. Missing files raise `FileNotFoundError`. (Source: `gen_epix/commondb/config/settings_manager.py#L43-L67`)
3. **App startup** — `uvicorn.run()` starts the ASGI server. Composition failures are logged and re-raised. (Source: `gen_epix/commondb/env.py#L185-L197`)

Operator Note: `CASEDB` env setup also sets `SEQDB` env variables, so multi-app sessions can be affected by launching casedb first. (Source: `gen_epix/commondb/util.py#L61-L64`)

---

## Evidence Sources

- `run.py#L15-L887`
- `.github/workflows/main.yml#L73-L197`
- `mypy.ini#L1-L80`
- `test/test_client/linter.py#L50-L58`
- `gen_epix/commondb/util.py#L61-L119`
- `gen_epix/commondb/config/settings_manager.py#L43-L67`
- `gen_epix/commondb/env.py#L185-L197`
- `requirements.txt#L3-L35`
- `dev-requirements.txt#L1-L25`

## Startup benchmark

The standard-library harness measures a fresh interpreter through the first
completed `HTTP 200 GET /v1/health` from the launched instance. Select `casedb`,
`seqdb`, or `omopdb` and explicitly supply both existing development modes:

```bash
.venv/bin/python -m scripts.startup_benchmark benchmark casedb \
  --idp-mode NONE --repository-mode DICT_EMPTY
.venv/bin/python -m scripts.startup_benchmark diagnose seqdb \
  --idp-mode NONE --repository-mode DICT_EMPTY --kind both
.venv/bin/python -m scripts.startup_benchmark report RESULTS_JSON \
  --diagnostics DIAGNOSTICS_JSON --output REPORT_DIRECTORY
.venv/bin/python -m scripts.startup_benchmark report --input RESULTS_JSON \
  --diagnostics DIAGNOSTICS_JSON --output report.html
```

The positional-input report still writes Markdown, SVG, and JSON to a directory.
The `--input` form writes one offline HTML dashboard with embedded Plotly charts,
run filters, fixed overall statistics, and searchable import rankings. Install
its Jinja2/Plotly dependencies from `dev-requirements.txt`, then open the HTML
directly in a browser. Reporting reads saved JSON without starting applications
and does not require Linux/WSL. Diagnostics are optional and must match the saved
benchmark evidence. See the [dashboard usage guide](../scripts/startup_benchmark/README.md#offline-html-dashboard).

`NONE` and `DICT_EMPTY` are local examples, not a reference deployment. The
harness requires Python 3.14+ and Linux/WSL. It uses the invoking interpreter,
existing fixed ports (8000, 8001, 8002), `run.py api ... --noreload`, and
`WEB_CONCURRENCY=1`. It never starts external services, resets repositories,
flushes caches, or stops unrelated listeners. Fixed ports prevent concurrent
runs of the same app. Production application code and `Run.api` are unchanged.

Benchmark defaults are 30 measured runs, zero warmups, a 60-second readiness
limit, a 0.05-second polling interval, a 0.25-second request timeout bounded by
the deadline, and a one-second pause after cleanup. Override these with
`--runs`, `--warmups`, `--readiness-timeout`, `--poll-interval`,
`--request-timeout`, and `--settle-seconds`. Warmups remain visible and are
excluded from statistics. Diagnostics default to one run per selected kind;
`--kind imports|phases|both` controls independent diagnostic launches.

Reports are written to unique directories beneath ignored
`test/output/startup_benchmark/`, or a new `--output` directory. Each attempt is
persisted atomically before the next launch. JSON retains failures, cleanup,
log paths, metadata, configuration snapshots, and diagnostic data. Markdown
and standalone SVG reports can be regenerated offline. Attached diagnostics
must match application, commit, and non-secret configuration fingerprints.
Raw process logs can contain ordinary application output; use the redacted
JSON configuration when sharing configuration details.

Every run merges a fresh `X-Startup-Benchmark-Instance` nonce into the existing
`<APP>_API__HTTP_HEADER__GENERAL` dictionary override. Caller headers are
preserved. Readiness requires status 200, the expected nonce, and a live child.
The configuration checker currently warns that this extra header is an
unrecognized key even though middleware reads it. `debug=True` disables that
middleware and is rejected without changing the caller's configuration.
Configuration-only subprocesses capture preflight and post-measurement
snapshots without constructing repositories or serving an app. Their imports
can affect ordinary system caches; neither subprocess enters a measured timer.
Process-specific addresses in callable representations are normalized for
configuration comparison. Settings/logging-file selection follows the existing
launcher, which rebuilds `SETTINGS_FILES` and `LOG_CONFIG_FILE`.

TLS follows the launcher's certificate files. An incomplete certificate pair
is rejected. Verification is enabled by default; use `--ca-file` for a custom
CA or explicit, recorded `--insecure` for a local experiment. Requests bypass
proxies and never follow redirects. Inherited import profiling and subprocess
coverage activation are refused for normal measurements. Cleanup sends SIGTERM
to the process group, waits up to ten seconds, escalates to SIGKILL, and verifies
termination before another launch. Occupied ports, identity conflicts, failed
cleanup, configuration changes, and interruption abort remaining attempts.
Ordinary startup failures remain recorded and subsequent runs continue.

Statistics describe **successful measured runs**. p90 and p95 use nearest rank:
the sorted sample at `ceil(p × n)`. The signed margin is `15.0 − p95` seconds;
threshold exceedances count successful samples strictly above 15 seconds.
`--check-target` opts into a CI gate that requires at least 30 successful
measurements, a complete failure-free series, valid cleanup/configuration, and
`p95 < 15.0`. Smaller samples are exploratory. Exit statuses are 0 for completed
commands, 1 for startup failures or a failed requested gate, 2 for invalid
options/configuration, and 130 for interruption; partial reports retain all
attempted and unattempted runs.

The experiment is **fresh-process startup with ordinary system caches**.
Filesystem, shared libraries, bytecode, and external databases can retain
caches; startup can read data, acquire connections, create root users, or check
SQLite schemas. Thirty samples give a coarse empirical p95, not strong
confidence about a population p95. Fully cold experiments require externally
controlled fresh environments. Health proves endpoint service by this instance,
not database, IDP, or business-operation readiness. Polling and request overhead
are included without mathematical correction.

Import diagnostics retain raw `-X importtime` stderr and repeated module
occurrences, reconstruct observed postorder execution chains, and flag malformed
or incomplete trees. Cumulative subtree times must never be summed. Threaded
imports can disrupt the trace. Phase diagnostics install signature-preserving
sync/async wrappers in a separate child before running the existing launcher.
Preparation changes import order and is explicitly recorded. Inclusive spans,
derived synchronous exclusive times, overlapping spans, gaps, and incomplete
spans describe that instrumented run; they do not partition normal startup.
Engine creation alone does not prove a database connection. Keep the existing
in-process casedb pyinstrument/cProfile startup tooling separate.

Harness tests live under `test/general/unit/startup_benchmark/` and
`test/general/integration/startup_benchmark/`. Both are registered in the curated
suite and VS Code; lifecycle tests use controlled standard-library HTTP children
and do not require external databases. Adding an application requires a typed
descriptor in `scripts/startup_benchmark/models.py` and launcher contract coverage.
