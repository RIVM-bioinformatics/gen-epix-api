Creation Date: March 1, 2026

# CI/CD & Release

This chapter consolidates the CI quality pipeline, release publication flow, and contribution workflow into a single reference. It merges content previously spread across two separate documents.

For local commands that mirror CI gates, see [06-Development-Guide](./06-Development-Guide.md).

---

## 1. Delivery Architecture Overview

This repository implements delivery as two connected but distinct pipelines: a CI quality pipeline (`main.yml`) and a release publication pipeline (`release.yaml`). The separation keeps routine code-quality feedback fast while reserving packaging/publishing actions for release events. (Source: `.github/workflows/main.yml#L1-L20`; Source: `.github/workflows/release.yaml#L1-L19`)

```text
Code change
  -> CI gates (format, lint, type-check, tests)
  -> coverage artifact
  -> SonarCloud scan
  -> (main release flow) release-please + version bump
  -> build dist + attach artifact + publish to PyPI
```

---

## 2. CI Triggers and Scope

Main CI workflow (`main.yml`) runs on:
- Push to `dev`, `test`, `main`
- Pull requests targeting `dev`, `test`, `main` (opened/synchronize/reopened/edited)

CI uses concurrency cancellation per branch/run, which prevents duplicate in-flight runs for the same change stream. (Source: `.github/workflows/main.yml#L3-L18`)

---

## 3. CI Quality Gate Flow

CI first establishes a reusable environment (`~/.venv`) with Python 3.14, ODBC headers, dependencies, and source-built `pyodbc`, then fans out into quality jobs that all depend on this setup stage. (Source: `.github/workflows/main.yml#L21-L57`)

Quality enforcement is split into focused checks:

| Gate | Tool | Source |
|------|------|--------|
| Formatting | `isort --check-only --diff --profile black .` + `black --check --diff .` | `.github/workflows/main.yml#L73-L77` |
| Linting | `pylint` with PR comment output | `.github/workflows/main.yml#L102-L113` |
| Type checking | `mypy` with strict flags | `.github/workflows/main.yml#L136-L140` |
| Tests | `python run.py test_all` | `.github/workflows/main.yml#L167-L170` |
| Coverage | XML uploaded as artifact, consumed by SonarCloud | `.github/workflows/main.yml#L171-L197` |

Developer Note: CI test scope is exactly what `run.py test_all` includes; performance/code test folders are intentionally commented out there by default. (Source: `run.py#L180-L187`)

### Local Commands Aligned with CI

| CI gate | Local equivalent |
|---------|-----------------|
| Tests | `python run.py test_all` |
| Formatting check | `isort --check-only --diff --profile black .` then `black --check --diff .` |
| Type checking | `python run.py other_general_run_mypy` |
| Linting | `python run.py other_general_run_pylint` |

Tooling is present in `dev-requirements.txt` (`pytest`, `isort`, `black`, `pylint`, `mypy`, `coverage`). (Source: `dev-requirements.txt#L6-L16`)

---

## 4. Authority Model for Versions and Releases

Release intent comes from release-please configuration and manifest state, not from manual tag creation. The workflow explicitly passes both config and manifest files into `googleapis/release-please-action`. (Source: `.github/workflows/release.yaml#L25-L31`; Source: `release-please-config.json#L2-L9`; Source: `.release-please-manifest.json#L1-L3`)

The workflow also updates `pyproject.toml` version by comparing current project version against release-please-derived target version, then auto-commits if changed. This creates a second version authority synchronization step inside CI/CD. (Source: `.github/workflows/release.yaml#L51-L77`)

Operator Note: current repository state shows manifest and `pyproject.toml` version values diverging (`7.1.2` vs `7.1.1`), which explains why the version bump step exists. (Source: `.release-please-manifest.json#L2-L2`; Source: `pyproject.toml#L7-L7`)

---

## 5. Release Publication Flow

Release workflow starts by running release-please, then checks out repository state and optionally switches to a release-please branch when PRs are created. (Source: `.github/workflows/release.yaml#L25-L36`)

If release-please indicates a version update path:
1. Workflow bumps `pyproject.toml` and commits the change.
2. Pushes with `--force`.

(Source: `.github/workflows/release.yaml#L51-L85`)

If a release is created:
1. Builds distributions.
2. Zips artifacts.
3. Uploads zip to GitHub Release.
4. Publishes package files from `dist` to PyPI.

(Source: `.github/workflows/release.yaml#L87-L118`)

Security Note: Publishing is configured with `id-token: write` and a named `PyPI` environment, so release permissions and secrets posture are tied to GitHub environment governance. (Source: `.github/workflows/release.yaml#L11-L23`)

---

## 6. Container Model

The root `Dockerfile` is written for CASEDB (port 8000) but the pattern is identical for every app; only the module path and port change.

Key steps in the image:
1. Installs `msodbcsql18` — required for the `SA_SQL` repository backend (SQL Server via pyodbc).
2. Creates a non-root `appuser` (UID 10001) for security.
3. Installs Python dependencies from `requirements.txt` with layer caching.
4. Copies the full source tree into `/app`.
5. Adds a health-check (`curl /v1/health`).

The intended production `CMD` (commented out in the current Dockerfile) is:

```
gunicorn --preload -k uvicorn.workers.UvicornWorker gen_epix.casedb.app:FAST_API
```

`--preload` runs the app module once in the master process before forking workers, so `AppCfg` + `AppComposer` execute only once and the resulting `FAST_API` object is shared across all workers via copy-on-write. (Source: `Dockerfile`)

---

## 7. Branching Model

Branches `dev`, `test`, and `main` are automation targets in CI. (Source: `.github/workflows/main.yml#L3-L14`)

A formal branching model policy is not documented in repository governance files: `<TBF elsewhere>`.

---

## 8. Configuration Surfaces That Control Delivery

| Surface | Role |
|---------|------|
| Branch/event triggers + concurrency policy | Controls when CI runs |
| Job dependency graph (`needs`) + artifact hand-off | Structures the quality gate pipeline |
| `release-please-config.json` + `.release-please-manifest.json` | Release metadata authority |
| `pyproject.toml` version field | Python package version authority |
| `sonar-project.properties` | SonarCloud analysis configuration |

---

## 9. Operational Interpretation

Before external publication, operators should reason about delivery in phases:
1. **Environment setup reliability** — look at setup-env and cache/install stages.
2. **Quality gate outcomes** — formatting/lint/type-check job outputs and PR comments.
3. **Test/coverage production** — `run-tests` step and coverage artifact presence.
4. **Publication side effects** — build/zip/upload/publish steps gated by `release_created`.

That phase model maps directly to workflow structure and is the fastest incident triage path.

---

## 10. Open Questions / `<TBF elsewhere>`

1. Environment protection rules, required reviewers, and secret governance for the `PyPI` environment: `<TBF elsewhere>`. (Source: `.github/workflows/release.yaml#L21-L23`)
2. Formal rollback process for a bad PyPI/GitHub release: `<TBF elsewhere>`.
3. Branch protection and force-push policy alignment with automated version bumping: `<TBF elsewhere>`. (Source: `.github/workflows/release.yaml#L84-L85`)
4. Code review policy (required approvals, reviewer roles, merge policy): `<TBF elsewhere>`.
5. Issue triage and prioritization process: `<TBF elsewhere>`.
6. Runtime infrastructure rollout/rollback strategy: `<TBF elsewhere>`.

---

## Evidence Sources

- `.github/workflows/main.yml#L1-L197`
- `.github/workflows/release.yaml#L1-L118`
- `release-please-config.json#L2-L9`
- `.release-please-manifest.json#L1-L3`
- `pyproject.toml#L5-L7`
- `run.py#L163-L200`
- `dev-requirements.txt#L6-L16`
- `sonar-project.properties`
- `Dockerfile`
