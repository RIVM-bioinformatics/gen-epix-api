Creation Date: February 16, 2026

# Contribution Workflow

## Evidenced in Repository

### CI Triggers and Scope
- Main CI workflow (`main.yml`) runs on: (Source: `.github/workflows/main.yml#L3-L14`)
  - push to `dev`, `test`, `main`
  - pull requests targeting `dev`, `test`, `main` (opened/synchronize/reopened/edited)
- CI uses concurrency cancellation per branch/run. (Source: `.github/workflows/main.yml#L16-L18`)

### Quality Gates
- Shared environment setup installs Python 3.14, dependencies, and source-built `pyodbc`. (Source: `.github/workflows/main.yml#L30-L57`)
- Formatting gate uses `isort` and `black`. (Source: `.github/workflows/main.yml#L73-L77`)
- Linting gate runs `pylint`. (Source: `.github/workflows/main.yml#L102-L113`)
- Type-checking gate runs strict `mypy` flags. (Source: `.github/workflows/main.yml#L136-L140`)
- Test gate runs `python run.py test_all`. (Source: `.github/workflows/main.yml#L167-L170`)
- Coverage XML is uploaded and then used by SonarCloud job. (Source: `.github/workflows/main.yml#L171-L197`)

### Local Commands Aligned With CI
- Tests: `python run.py test_all`. (Source: `run.py#L163-L200`; Source: `.github/workflows/main.yml#L167-L170`)
- Formatting check: `isort --check-only --diff --profile black . && black --check --diff .`. (Source: `.github/workflows/main.yml#L73-L77`)
- Type-checking: run the same `mypy` flags used in CI. (Source: `.github/workflows/main.yml#L136-L140`)
- Tooling is present in `dev-requirements.txt` (`pytest`, `isort`, `black`, `pylint`, `mypy`, `coverage`). (Source: `dev-requirements.txt#L6-L16`)

### Release Automation
- Release workflow (`release.yaml`) runs on push to `main` and PR activity on `main`. (Source: `.github/workflows/release.yaml#L2-L10`)
- It runs release-please using `release-please-config.json` and `.release-please-manifest.json`. (Source: `.github/workflows/release.yaml#L25-L31`; Source: `release-please-config.json#L2-L9`; Source: `.release-please-manifest.json#L1-L3`)
- When a release PR is created, workflow can bump `pyproject.toml` version and auto-commit with force push. (Source: `.github/workflows/release.yaml#L51-L85`; Source: `pyproject.toml#L5-L7`)
- When a release is created, it builds distributions and publishes to PyPI. (Source: `.github/workflows/release.yaml#L99-L118`)

## Inferred from Code Structure

### Branching Model
- Branches `dev`, `test`, and `main` are automation targets in CI. (Source: `.github/workflows/main.yml#L3-L14`)
- A formal branching model policy is not documented in repository governance files: `<TBF elsewhere>`.

### Pull Request and Governance Process
- CI behavior for PRs is evidenced by workflow triggers and jobs. (Source: `.github/workflows/main.yml#L3-L14`; Source: `.github/workflows/main.yml#L30-L197`)
- Code review policy (required approvals, reviewer roles, merge policy): `<TBF elsewhere>`.
- Issue triage and prioritization process: `<TBF elsewhere>`.

## Evidence Sources
- `.github/workflows/main.yml#L3-L18`
- `.github/workflows/main.yml#L30-L57`
- `.github/workflows/main.yml#L73-L77`
- `.github/workflows/main.yml#L102-L113`
- `.github/workflows/main.yml#L136-L140`
- `.github/workflows/main.yml#L167-L197`
- `.github/workflows/release.yaml#L2-L10`
- `.github/workflows/release.yaml#L25-L31`
- `.github/workflows/release.yaml#L51-L85`
- `.github/workflows/release.yaml#L99-L118`
- `release-please-config.json#L2-L9`
- `.release-please-manifest.json#L1-L3`
- `run.py#L163-L200`
- `pyproject.toml#L5-L7`
- `dev-requirements.txt#L6-L16`
