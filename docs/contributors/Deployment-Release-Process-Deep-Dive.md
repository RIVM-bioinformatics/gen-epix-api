# Deployment & Release Process Deep Dive

## 1. Delivery Architecture Overview
This repository implements delivery as two connected but distinct pipelines: a CI quality pipeline (`main.yml`) and a release publication pipeline (`release.yaml`). The separation keeps routine code-quality feedback fast while reserving packaging/publishing actions for release events. (Source: `.github/workflows/main.yml#L1-L20`; Source: `.github/workflows/release.yaml#L1-L19`)

CI is triggered broadly (push + PR on `dev`, `test`, `main`) with concurrency cancellation, which prevents duplicate in-flight runs for the same change stream. (Source: `.github/workflows/main.yml#L3-L18`)

Release automation is anchored to `main` activity and release-please outputs, then conditionally performs version bumping, artifact publication, and PyPI publishing. (Source: `.github/workflows/release.yaml#L2-L10`; Source: `.github/workflows/release.yaml#L25-L31`; Source: `.github/workflows/release.yaml#L87-L118`)

```text
Code change
  -> CI gates (format, lint, type-check, tests)
  -> coverage artifact
  -> SonarCloud scan
  -> (main release flow) release-please + version bump
  -> build dist + attach artifact + publish to PyPI
```
(Source: `.github/workflows/main.yml#L59-L197`; Source: `.github/workflows/release.yaml#L25-L118`)

## 2. Authority Model for Versions and Releases
Release intent comes from release-please configuration and manifest state, not from manual tag creation in this workflow definition. The workflow explicitly passes both config and manifest files into `googleapis/release-please-action`. (Source: `.github/workflows/release.yaml#L25-L31`; Source: `release-please-config.json#L2-L9`; Source: `.release-please-manifest.json#L1-L3`)

The workflow also updates `pyproject.toml` version by comparing current project version against release-please-derived target version, then auto-commits if changed. This creates a second version authority synchronization step inside CI/CD. (Source: `.github/workflows/release.yaml#L51-L77`; Source: `.github/workflows/release.yaml#L79-L85`; Source: `pyproject.toml#L5-L7`)

Operator Note: current repository state shows manifest and `pyproject.toml` version values diverging (`7.1.2` vs `7.1.1`), which explains why the version bump step exists. (Source: `.release-please-manifest.json#L2-L2`; Source: `pyproject.toml#L7-L7`; Source: `.github/workflows/release.yaml#L68-L75`)

## 3. CI Quality Gate Flow
CI first establishes a reusable environment (`~/.venv`) with Python 3.14, ODBC headers, dependencies, and source-built `pyodbc`, then fan-outs into quality jobs that all depend on this setup stage. (Source: `.github/workflows/main.yml#L21-L57`; Source: `.github/workflows/main.yml#L59-L65`; Source: `.github/workflows/main.yml#L93-L94`; Source: `.github/workflows/main.yml#L127-L128`; Source: `.github/workflows/main.yml#L155-L156`)

Quality enforcement is split into focused checks:
1. Formatting (`isort`, `black`)
2. Linting (`pylint` with PR comment output)
3. Type checking (`mypy` with strict flags)
(Source: `.github/workflows/main.yml#L73-L87`; Source: `.github/workflows/main.yml#L102-L120`; Source: `.github/workflows/main.yml#L136-L151`)

Test execution runs through `python run.py test_all`, uploads `test/output/coverage.xml` as an artifact, and SonarCloud downloads that artifact for scan. (Source: `.github/workflows/main.yml#L167-L177`; Source: `.github/workflows/main.yml#L178-L197`; Source: `run.py#L163-L200`)

Developer Note: CI test scope is exactly what `run.py test_all` includes; performance/code test folders are intentionally commented out there by default. (Source: `run.py#L180-L187`)

## 4. Release Publication Flow
Release workflow starts by running release-please, then checks out repository state and optionally switches to a release-please branch when PRs are created. (Source: `.github/workflows/release.yaml#L25-L36`; Source: `.github/workflows/release.yaml#L38-L50`)

If release-please indicates a version update path, workflow bumps `pyproject.toml`, commits the change, and pushes with `--force`. (Source: `.github/workflows/release.yaml#L51-L85`)

If a release is created, workflow builds distributions, zips artifacts, uploads zip to GitHub Release, and publishes package files from `dist` to PyPI. (Source: `.github/workflows/release.yaml#L87-L118`)

Security Note: publishing is configured with `id-token: write` and a named `PyPI` environment, so release permissions and secrets posture are tied to GitHub environment governance. (Source: `.github/workflows/release.yaml#L11-L23`; Source: `.github/workflows/release.yaml#L114-L118`)

## 5. Configuration Surfaces That Control Delivery
The key control surfaces are:
1. Branch/event triggers and concurrency policy in CI.
2. Job dependency graph (`needs`) and artifact hand-off in CI.
3. release-please config/manifest files for release metadata.
4. Python package metadata/version in `pyproject.toml`.
(Source: `.github/workflows/main.yml#L3-L18`; Source: `.github/workflows/main.yml#L64-L65`; Source: `.github/workflows/main.yml#L172-L191`; Source: `.github/workflows/release.yaml#L29-L31`; Source: `release-please-config.json#L2-L9`; Source: `.release-please-manifest.json#L1-L3`; Source: `pyproject.toml#L5-L7`)

## 6. Operational Interpretation
Before external publication, operators should reason about delivery in phases: environment setup reliability, quality gate outcomes, test/coverage production, then release publication side effects. That phase model maps directly to workflow structure and is the fastest incident triage path. (Source: `.github/workflows/main.yml#L21-L57`; Source: `.github/workflows/main.yml#L59-L197`; Source: `.github/workflows/release.yaml#L87-L118`)

Common failure localization:
1. Setup/dependency failures: look at setup-env and cache/install stages.
2. Code quality failures: formatting/lint/type-check job outputs and PR comments.
3. Test/coverage failures: `run-tests` step and coverage artifact presence.
4. Publication failures: build/zip/upload/publish steps gated by `release_created`.
(Source: `.github/workflows/main.yml#L44-L57`; Source: `.github/workflows/main.yml#L73-L151`; Source: `.github/workflows/main.yml#L167-L177`; Source: `.github/workflows/release.yaml#L91-L118`)

Operator Note: the release workflow can force-push version bump commits, so branch protection and release branch handling outside this file are operationally significant but `<TBF elsewhere>`. (Source: `.github/workflows/release.yaml#L79-L85`)

## 7. Constraints & Guardrails
1. CI and release logic are GitHub Actions-specific in this repository; alternate CD systems are not evidenced here. (Source: `.github/workflows/main.yml#L1-L197`; Source: `.github/workflows/release.yaml#L1-L118`)
2. Runtime infrastructure rollout/rollback strategy is not implemented in these workflows: `<TBF elsewhere>`.
3. Release publication depends on release-please outputs (`prs_created`, `release_created`), so downstream publish steps are intentionally conditional. (Source: `.github/workflows/release.yaml#L49-L49`; Source: `.github/workflows/release.yaml#L77-L77`; Source: `.github/workflows/release.yaml#L91-L118`)

## 8. Open Questions / <TBF elsewhere>
1. Environment protection rules, required reviewers, and secret governance for the `PyPI` environment: `<TBF elsewhere>`. (Source: `.github/workflows/release.yaml#L21-L23`)
2. Formal rollback process for a bad PyPI/GitHub release: `<TBF elsewhere>`.
3. Branch protection and force-push policy alignment with automated version bumping: `<TBF elsewhere>`. (Source: `.github/workflows/release.yaml#L84-L85`)

## 9. Evidence Index
- `.github/workflows/main.yml#L1-L197`
- `.github/workflows/release.yaml#L1-L118`
- `release-please-config.json#L2-L9`
- `.release-please-manifest.json#L1-L3`
- `pyproject.toml#L5-L7`
- `run.py#L163-L200`
