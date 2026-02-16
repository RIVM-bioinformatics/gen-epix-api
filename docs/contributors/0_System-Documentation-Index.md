Creation Date: February 16, 2026

# Consolidated System Documentation

## 1. Purpose and Audience
This document is the system-level map for maintainers, security reviewers, and operators. It explains how Gen-EpiX is structured, where control points live, and what is explicitly evidenced versus still undocumented. (Source: `gen_epix/casedb/app.py#L28-L45`; Source: `gen_epix/commondb/env.py#L89-L205`; Source: `.github/workflows/main.yml#L1-L197`)

It consolidates the architecture and operational implications that are implemented in primary sources, and links detailed treatment to the deep-dive documents.

Developer Note: use this as the "why and where" map; use each deep dive for lower-level details. (Source: `docs/API-Endpoints-Deep-Dive.md#L1-L89`; Source: `docs/Authorization-Authentication-Deep-Dive.md#L1-L124`; Source: `docs/Deployment-Release-Process-Deep-Dive.md#L1-L85`; Source: `docs/High-Level-Architecture-Deep-Dive.md#L1-L97`; Source: `docs/Local-Development-Deep-Dive.md#L1-L83`)

### Deep-Dive Guides
- [API Endpoints Deep Dive](./API-Endpoints-Deep-Dive.md): Focuses on the external API contract shape, route-family patterns, and how to interpret OpenAPI surface boundaries.
- [Authorization & Authentication Deep Dive](./Authorization-Authentication-Deep-Dive.md): Explains the security architecture end to end, including trust boundaries, identity resolution, and command-layer policy enforcement.
- [Deployment & Release Process Deep Dive](./Deployment-Release-Process-Deep-Dive.md): Summarizes CI quality gates and release publication flow, including release-please version orchestration and PyPI publishing.
- [High-Level Architecture Deep Dive](./High-Level-Architecture-Deep-Dive.md): Covers system composition, runtime lifecycle, and the core command-centric execution model across apps.
- [Local Development Deep Dive](./Local-Development-Deep-Dive.md): Documents local startup modes, settings layering, test/ETL workflows, and operational implications for developer environments.
- [Contributor Documentation Landing](./README.md): Entry point for contributor-oriented guidance and evidence policy.
- [Getting Started](./Getting-Started.md): Local prerequisites, startup commands, test execution, and health/log verification.
- [Architecture Principles](./Architecture-Principles.md): Evidence-grounded architecture invariants and security-relevant boundaries.
- [Extending the System](./Extending-the-System.md): Observed extension patterns for modules, commands, RBAC, routers, and IDP config.
- [Contribution Workflow](./Contribution-Workflow.md): CI triggers, quality gates, local command parity, and release automation.

Recommended reading order for onboarding:
1. Start with [Contributor Documentation Landing](./README.md) for scope and documentation policy.
2. Continue with [Getting Started](./Getting-Started.md) to run the system locally and validate health/logging.
3. Read [Architecture Principles](./Architecture-Principles.md) to understand boundaries and invariants before changing code.
4. Read [High-Level Architecture Deep Dive](./High-Level-Architecture-Deep-Dive.md) to build the system mental model.
5. Read [Authorization & Authentication Deep Dive](./Authorization-Authentication-Deep-Dive.md) to understand trust boundaries and policy enforcement points.
6. Continue with [API Endpoints Deep Dive](./API-Endpoints-Deep-Dive.md) to map the exposed contract to the architecture and security model.
7. Use [Extending the System](./Extending-the-System.md) before adding modules, commands, RBAC rules, routers, or IDP config.
8. Use [Contribution Workflow](./Contribution-Workflow.md) before opening a PR to align with CI/release gates.
9. Use [Local Development Deep Dive](./Local-Development-Deep-Dive.md) for deeper local-mode and troubleshooting details.
10. Finish with [Deployment & Release Process Deep Dive](./Deployment-Release-Process-Deep-Dive.md) for CI/CD and release operations context.

## 2. System Architecture at a Glance
The platform is built as four FastAPI applications (`CASEDB`, `SEQDB`, `OMOPDB`, `COMMONDB`) that share a common composition model. Each app constructs `AppCfg`, composes services/repositories/policies with `AppComposer`, and then exposes HTTP routes through the shared FastAPI assembly function. (Source: `run.py#L17-L38`; Source: `gen_epix/casedb/app.py#L28-L45`; Source: `gen_epix/seqdb/app.py#L28-L45`; Source: `gen_epix/omopdb/app.py#L28-L45`; Source: `gen_epix/commondb/app.py#L26-L42`; Source: `gen_epix/commondb/app_setup.py#L27-L35`)

```text
Process start
  -> AppCfg (logging + settings)
  -> AppComposer (repositories + services + user deps + policies)
  -> create_fast_api (middleware + /v1 routers + root redirect)
  -> endpoint function
  -> app.handle(command)
  -> policy phases BEFORE / DURING / AFTER
```
(Source: `gen_epix/commondb/config/cfg.py#L155-L177`; Source: `gen_epix/commondb/env.py#L103-L177`; Source: `gen_epix/commondb/app_setup.py#L74-L126`; Source: `gen_epix/fastapp/app.py#L314-L360`)

**Architectural anchor:** endpoint code is mostly transport glue; authorization and policy enforcement are centralized at command execution time. (Source: `gen_epix/commondb/api/auth.py#L30-L34`; Source: `gen_epix/commondb/api/system.py#L85-L90`; Source: `gen_epix/fastapp/app.py#L314-L360`)

## 3. Trust and Control Boundaries
Trust enters through configured identity providers and security dependencies, then flows into internal user/policy enforcement. Authentication resolves identity; authorization decides command permission. (Source: `config/identity_providers.toml#L1-L34`; Source: `gen_epix/fastapp/services/auth/service.py#L84-L90`; Source: `gen_epix/fastapp/services/auth/service.py#L450-L470`; Source: `gen_epix/fastapp/app.py#L406-L418`)

When no IDP clients are configured, auth dependencies intentionally switch to a fallback that can return/create root user paths. This is an implemented mode, not an accidental failure path. (Source: `gen_epix/fastapp/services/auth/service.py#L88-L91`; Source: `gen_epix/fastapp/services/auth/service.py#L376-L424`; Source: `config/no_identity_providers.toml#L1-L1`)

Security Note: OIDC is the only implemented auth protocol in the IDP client initialization path; non-OIDC protocol config raises `NotImplementedError`. (Source: `gen_epix/fastapp/services/auth/service.py#L675-L694`)

## 4. Application Topology and Boundaries
`COMMONDB` provides shared routers (`auth`, `rbac`, `organization`, `system`) and shared service configuration baseline. (Source: `gen_epix/commondb/api/router.py#L23-L48`; Source: `gen_epix/commondb/config/settings.toml#L56-L75`)

`CASEDB`, `SEQDB`, and `OMOPDB` extend the common router set with domain routers (`case/geo/ontology/subject/abac`, `seq/file`, `omop`). (Source: `gen_epix/casedb/api/router.py#L26-L72`; Source: `gen_epix/seqdb/api/router.py#L26-L64`; Source: `gen_epix/omopdb/api/router.py#L25-L55`)

Repository bindings are configuration-driven by module/class mappings, while runtime repository type handling is bounded to `DICT`, `SA_SQLITE`, and `SA_SQL`. (Source: `gen_epix/casedb/config/settings.repository.dict.toml#L1-L27`; Source: `gen_epix/casedb/config/settings.repository.sa.toml#L1-L27`; Source: `gen_epix/seqdb/config/settings.repository.sa.toml#L1-L19`; Source: `gen_epix/omopdb/config/settings.repository.sa.toml#L1-L15`; Source: `gen_epix/commondb/base_env.py#L66-L93`)

Operator Note: `SEQDB` router data contains duplicate `file` registration entries and should be treated as a boundary maintenance risk. (Source: `gen_epix/seqdb/api/router.py#L57-L63`)

## 5. Request Lifecycle and Enforcement
Requests are routed under `/v1`, and `/` redirects to the configured default route. In non-debug mode, the API shell applies rate limiting, gzip compression, response header hardening, and auth exception handling middleware. (Source: `gen_epix/commondb/app_setup.py#L75-L109`; Source: `gen_epix/commondb/app_setup.py#L120-L126`; Source: `gen_epix/commondb/config/settings.toml#L8-L9`; Source: `gen_epix/commondb/config/settings.toml#L42-L43`)

The command runtime applies policy at three explicit timing phases:
1. `BEFORE` gate (allow/deny)
2. `DURING` policy injection
3. `AFTER` return-value filtering/transform
(Source: `gen_epix/fastapp/app.py#L314-L320`; Source: `gen_epix/fastapp/app.py#L347-L360`; Source: `gen_epix/fastapp/app.py#L406-L418`)

RBAC registration is command-policy based and wired through service registration at startup rather than hardcoded per route. (Source: `gen_epix/commondb/env.py#L175-L177`; Source: `gen_epix/fastapp/services/rbac/service.py#L365-L375`; Source: `gen_epix/commondb/services/rbac.py#L32-L49`)

## 6. Runtime Modes and Configuration Model
Per-app settings files define host/port/debug and `/v1` route prefix (`CASEDB:8000`, `SEQDB:8001`, `OMOPDB:8002`, `COMMONDB:8010`). (Source: `gen_epix/casedb/config/settings.toml#L1-L4`; Source: `gen_epix/seqdb/config/settings.toml#L1-L4`; Source: `gen_epix/omopdb/config/settings.toml#L1-L4`; Source: `gen_epix/commondb/config/settings.toml#L1-L4`; Source: `gen_epix/commondb/config/settings.toml#L42-L43`)

`run.py` is the local orchestration entrypoint for API start, ETL loading, and test commands. API launch chooses app/IDP/repository modes, builds env settings stack, and starts uvicorn with reload and optional local TLS files. (Source: `run.py#L15-L15`; Source: `run.py#L82-L107`; Source: `run.py#L134-L200`; Source: `gen_epix/commondb/util.py#L74-L119`)

Configuration loading is environment-driven via `<APP>_SETTINGS_FILES` and `<APP>_LOG_CONFIG_FILE`, with Dynaconf nested overrides using `__`. Missing settings files fail fast. (Source: `gen_epix/commondb/util.py#L114-L119`; Source: `gen_epix/commondb/config/settings_manager.py#L15-L17`; Source: `gen_epix/commondb/config/settings_manager.py#L63-L77`; Source: `gen_epix/commondb/config/cfg.py#L188-L215`)

Developer Note: local `CASEDB` environment setup also sets `SEQDB` environment variables, which can affect multi-service sessions. (Source: `gen_epix/commondb/util.py#L61-L64`)

## 7. API Surface Strategy
Endpoint surfaces are composed from common + app-specific routers and then expanded heavily by CRUD endpoint generation. Generated route families follow conventional `/batch`, `/query`, `/query/ids`, and `/{object_id}` patterns with consistent operation IDs. (Source: `gen_epix/commondb/api/router.py#L23-L48`; Source: `gen_epix/casedb/api/router.py#L26-L72`; Source: `gen_epix/fastapp/api/crud_endpoint_generator.py#L55-L58`; Source: `gen_epix/fastapp/api/crud_endpoint_generator.py#L702-L757`)

In the inspected OpenAPI artifact (`docs/openapi.json`), contract title indicates `casedb`, and tags present are common + casedb domains; seqdb/omopdb contract coverage is `<TBF elsewhere>` via separate artifacts. (Source: `docs/openapi.json#L4-L4`; Source: `docs/openapi.json#L18-L18`; Source: `docs/openapi.json#L21-L23`; Source: `docs/openapi.json#L18484-L18484`; Source: `docs/openapi.json#L33175-L33175`)

Operator Note: `GET /identity_providers` and root redirect are intentionally exposed behaviors and should be reviewed explicitly in external exposure assessments. (Source: `gen_epix/commondb/api/auth.py#L24-L33`; Source: `docs/openapi.json#L19-L27`; Source: `docs/openapi.json#L36616-L36620`; Source: `gen_epix/commondb/app_setup.py#L123-L126`)

## 8. Delivery and Release Architecture
CI (`main.yml`) is the quality gate pipeline: setup/cache environment, formatting, linting, type checking, tests (`python run.py test_all`), coverage artifact upload, and SonarCloud scan. (Source: `.github/workflows/main.yml#L21-L57`; Source: `.github/workflows/main.yml#L59-L197`; Source: `run.py#L163-L200`)

Release (`release.yaml`) is event-gated by release-please outputs. It runs release-please, optionally bumps `pyproject.toml`, auto-commits/pushes version updates, builds dist artifacts, uploads release assets, and publishes to PyPI. (Source: `.github/workflows/release.yaml#L25-L31`; Source: `.github/workflows/release.yaml#L51-L85`; Source: `.github/workflows/release.yaml#L99-L118`)

Version authority currently needs reconciliation logic because repository state shows a mismatch (`pyproject.toml` `7.1.1` vs manifest `7.1.2`). (Source: `pyproject.toml#L7-L7`; Source: `.release-please-manifest.json#L2-L2`; Source: `.github/workflows/release.yaml#L65-L74`)

## 9. Container and Infrastructure Boundary
Container baseline is defined in `Dockerfile` with Python slim image, ODBC driver install, dependency install, non-root runtime user, exposed port `8000`, and healthcheck at `/v1/health`. (Source: `Dockerfile#L3-L4`; Source: `Dockerfile#L20-L30`; Source: `Dockerfile#L53-L55`; Source: `Dockerfile#L39-L47`; Source: `Dockerfile#L61-L64`; Source: `Dockerfile#L67-L67`)

No active runtime `CMD` is present in the inspected Dockerfile (examples are commented), so final production start command is `<TBF elsewhere>`. (Source: `Dockerfile#L68-L69`)

Cloud provider topology, IaC stack, network segmentation, and rollout model are not evidenced in inspected primary files: `<TBF elsewhere>`.

## 10. Observability and Operational Signals
Logging is JSON-formatted to stdout and scoped by logger namespaces (`commondb.setup`, `service`, `app`, `api`, `external`) with root `INFO` defaults. (Source: `gen_epix/commondb/config/logging.yaml#L1-L35`)

Application startup/shutdown and command lifecycle logging are emitted from shared startup and command runtime code paths, making those logs the primary control-point signals during incident triage. (Source: `gen_epix/commondb/app_setup.py#L40-L57`; Source: `gen_epix/fastapp/app.py#L86-L95`; Source: `gen_epix/fastapp/app.py#L329-L337`; Source: `gen_epix/fastapp/app.py#L510-L512`)

CI observability includes coverage artifact publication and SonarCloud analysis; runtime metrics/tracing/alerting backend is `<TBF elsewhere>`. (Source: `.github/workflows/main.yml#L171-L197`)

## 11. Constraints and Guardrails
1. Authentication protocol support is OIDC-only in current auth service initialization path. (Source: `gen_epix/fastapp/services/auth/service.py#L675-L694`)
2. No-IDP mode exists and maps to root-user fallback dependencies; treat as a high-risk security mode when externally exposed. (Source: `gen_epix/fastapp/services/auth/service.py#L88-L91`; Source: `gen_epix/fastapp/services/auth/service.py#L376-L424`; Source: `config/no_identity_providers.toml#L1-L1`)
3. IDP configuration enforces unique `name` and `label`; duplicates fail initialization. (Source: `gen_epix/fastapp/services/auth/service.py#L753-L775`)
4. Security dependency variants are hard-limited by implementation to five IDP bases. (Source: `gen_epix/fastapp/services/auth/service.py#L442-L449`; Source: `gen_epix/fastapp/services/auth/service.py#L360-L366`)
5. Repository mode handling is limited to `DICT`, `SA_SQLITE`, and `SA_SQL`. (Source: `gen_epix/commondb/base_env.py#L66-L93`)
6. Metadata mismatch exists: package license is `EUPL-1.2` while `seqdb`/`omopdb` OpenAPI metadata still uses placeholder `Apache-2.0`. (Source: `pyproject.toml#L13-L14`; Source: `gen_epix/seqdb/app.py#L22-L25`; Source: `gen_epix/omopdb/app.py#L22-L25`)

## 12. Open Questions / <TBF elsewhere>
1. Production runtime process command and service manager contract for container deployments: `<TBF elsewhere>`.
2. Stage/prod promotion, rollback, and environment isolation model beyond local + CI/release workflows: `<TBF elsewhere>`.
3. Secret management architecture for IDP and repository credentials in production: `<TBF elsewhere>`.
4. Cloud/IaC ownership and topology: `<TBF elsewhere>`.
5. Runtime monitoring/alerting/SLO definitions and incident runbooks: `<TBF elsewhere>`.
6. Complete OpenAPI contract coverage for `SEQDB` and `OMOPDB`: `<TBF elsewhere>`.

## 13. Evidence Index
- `run.py#L15-L200`
- `etl.py#L44-L148`
- `gen_epix/casedb/app.py#L28-L45`
- `gen_epix/seqdb/app.py#L22-L45`
- `gen_epix/omopdb/app.py#L22-L45`
- `gen_epix/commondb/app.py#L26-L42`
- `gen_epix/commondb/env.py#L89-L205`
- `gen_epix/commondb/base_env.py#L66-L93`
- `gen_epix/commondb/app_setup.py#L40-L126`
- `gen_epix/commondb/config/cfg.py#L155-L269`
- `gen_epix/commondb/config/settings_manager.py#L15-L77`
- `gen_epix/commondb/config/logging.yaml#L1-L35`
- `gen_epix/commondb/util.py#L61-L119`
- `gen_epix/commondb/api/router.py#L23-L48`
- `gen_epix/casedb/api/router.py#L26-L72`
- `gen_epix/seqdb/api/router.py#L26-L64`
- `gen_epix/omopdb/api/router.py#L25-L55`
- `gen_epix/commondb/api/auth.py#L24-L46`
- `gen_epix/commondb/api/system.py#L47-L141`
- `gen_epix/fastapp/app.py#L314-L418`
- `gen_epix/fastapp/api/crud_endpoint_generator.py#L55-L58`
- `gen_epix/fastapp/api/crud_endpoint_generator.py#L702-L757`
- `gen_epix/fastapp/services/auth/service.py#L84-L825`
- `gen_epix/fastapp/services/rbac/service.py#L121-L375`
- `gen_epix/commondb/services/rbac.py#L32-L49`
- `.github/workflows/main.yml#L1-L197`
- `.github/workflows/release.yaml#L1-L118`
- `release-please-config.json#L2-L10`
- `.release-please-manifest.json#L1-L3`
- `pyproject.toml#L5-L57`
- `Dockerfile#L3-L69`
- `docs/openapi.json#L4-L36620`
